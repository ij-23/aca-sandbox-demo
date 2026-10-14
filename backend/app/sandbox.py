"""Official SDK adapter. Repository code executes only in disposable MicroVMs."""

import asyncio
import json
import re
import shlex
import time
from pathlib import Path
from uuid import UUID, uuid4

from azure.containerapps.sandbox import (
    EgressPolicy,
    EgressRule,
    EgressRuleAction,
    EgressRuleMatch,
    SandboxGroupClient,
    endpoint_for_region,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import RequestsTransport
from azure.identity import ManagedIdentityCredential

from .security import redact

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "workflows"
OWNER = "academo-application-v1"
NAMES = {"security": "security-review", "build": "build-validation", "remediation": "remediation"}


class SandboxExecutor:
    def __init__(self, settings, store, events, *, group=None):
        self.settings, self.store, self.events = settings, store, events
        self.credential = None
        if group is None:
            for value in (
                settings.subscription_id,
                settings.credential_connection_id,
                settings.managed_identity_client_id,
            ):
                UUID(value)
            self.credential = ManagedIdentityCredential(client_id=settings.managed_identity_client_id)
            group = SandboxGroupClient(
                endpoint_for_region(settings.region),
                self.credential,
                subscription_id=settings.subscription_id,
                resource_group=settings.resource_group,
                sandbox_group=settings.sandbox_group,
                retry_total=0,
                transport=RequestsTransport(connection_timeout=10, read_timeout=90),
            )
        self.group = group
        self.locks = {}

    def egress_policy(self):
        hosts = self.settings.sandbox_egress_hosts
        if not hosts or any(not re.fullmatch(r"(?:\*\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+", h) for h in hosts):
            raise ValueError("Explicit egress host allowlist required")
        return EgressPolicy(
            default_action="Deny",
            traffic_inspection="Full",
            rules=[
                EgressRule(
                    name=f"approved-{index}", match=EgressRuleMatch(host=host), action=EgressRuleAction(type="Allow")
                )
                for index, host in enumerate(hosts)
            ],
        )

    async def call(self, function, *args, **kwargs):
        # Cancellation of an await does not stop an SDK thread. Drain it before cleanup
        # so a delayed create/exec cannot continue after deletion reconciliation.
        task = asyncio.create_task(asyncio.to_thread(function, *args, **kwargs))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            try:
                await task
            finally:
                raise

    async def read(self, sandbox, path, maximum=300000):
        value = await self.call(sandbox.read_file, path)
        if not isinstance(value, bytes) or len(value) > maximum:
            raise ValueError("Oversized or invalid sandbox output")
        return value.decode("utf-8")

    async def run(self, value, role, emit):
        UUID(value["run_id"])
        if role not in NAMES:
            raise ValueError("Invalid role")
        nonce = uuid4().hex
        record = {
            "run_id": value["run_id"],
            "role": role,
            "nonce": nonce,
            "sandbox_id": None,
            "state": "prepared",
            "labels": {"owner": OWNER, "run-id": value["run_id"], "role": role, "nonce": nonce},
        }
        # Durable intent is saved before the first create request.
        await self.store.save_ownership(record)
        await emit("sandbox.provisioning")
        sandbox = None
        try:
            record["state"] = "create_intent"
            await self.store.save_ownership(record)

            def create():
                return self.group.begin_create_sandbox(
                    disk="copilot",
                    connections=[self.settings.credential_connection_id],
                    cpu="1000m",
                    memory="2048Mi",
                    ports=[],
                    labels=record["labels"],
                    auto_suspend_seconds=300,
                    polling_timeout=80,
                    polling_interval=2,
                    egress_policy=self.egress_policy(),
                ).result(timeout=90)

            sandbox = await self.call(create)
            record.update(sandbox_id=sandbox.sandbox_id, state="running")
            await self.store.save_ownership(record)
            model = await self.call(sandbox.get)
            if model.ports or self.settings.credential_connection_id not in (model.connections or []):
                raise ValueError("Unexpected Sandbox connection/ports")
            await emit("sandbox.running", sandbox_id=sandbox.sandbox_id)
            control = f"/tmp/academo-{nonce}"
            extension_name = NAMES[role]
            await self.checked_exec(
                sandbox, f"mkdir -p {control}/.github/extensions/{extension_name} && git -C {control} init -q", 10
            )
            files = {
                f".github/extensions/{extension_name}/extension.mjs": WORKFLOWS / extension_name / "extension.mjs",
                ".github/runtime.mjs": WORKFLOWS / "shared/runtime.mjs",
                "operations.py": WORKFLOWS / "shared/operations.py",
                "runner.py": WORKFLOWS / "shared/runner.py",
                "cli_setup.py": ROOT / "scripts/smoke_workflow_runner.py",
            }
            for remote, local in files.items():
                await self.call(sandbox.write_file, f"{control}/{remote}", local.read_text())
            # The pinned standalone is installed only in each owned disposable directory.
            await self.checked_exec(sandbox, f"cd {control} && python3 cli_setup.py prepare-cli", 80)
            args = {
                "run_id": value["run_id"],
                "commit_sha": value["commit_sha"],
                "repository_url": value["repository_url"],
                "role": role,
                "publication_enabled": role == "remediation" and self.settings.publication_enabled,
                "approval": value.get("approval"),
                "finding": value.get("finding"),
            }
            for name, body in {
                "input.json": json.dumps(args),
                "events.jsonl": "",
                "status.json": '{"state":"pending"}',
            }.items():
                await self.call(sandbox.write_file, f"{control}/{name}", body)
            launch = "import subprocess; subprocess.Popen(['python3','runner.py'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)"
            await self.checked_exec(sandbox, f"cd {control} && python3 -c {shlex.quote(launch)}", 10)
            seen = 0
            started = time.monotonic()
            while time.monotonic() - started < 750:
                status = json.loads(await self.read(sandbox, f"{control}/status.json", 3000))
                lines = (await self.read(sandbox, f"{control}/events.jsonl", 2000000)).split("\n")[:-1]
                if len(lines) < seen:
                    raise ValueError("Workflow event journal truncated")
                for line in lines[seen:]:
                    event = json.loads(line)
                    if event["run_id"] != value["run_id"] or not re.fullmatch(
                        r"(?:workflow|step|command)\.[a-z_]+", event["type"]
                    ):
                        raise ValueError("Invalid workflow provenance")
                    await emit(
                        event["type"],
                        sandbox_id=sandbox.sandbox_id,
                        step_id=event["step_id"],
                        **redact(event["payload"]),
                        workflow_run_id=event["workflow_run_id"],
                        observed_at=event["timestamp"],
                    )
                seen = len(lines)
                if status["state"] == "finished":
                    log = await self.read(sandbox, f"{control}/cli.sanitized.log", 100000)
                    await emit(
                        "workflow.log",
                        sandbox_id=sandbox.sandbox_id,
                        step_id="cli.output",
                        text=log[-4000:],
                        exit_code=status.get("exit_code"),
                        duration_seconds=status.get("seconds"),
                        truncated=len(log) > 4000,
                    )
                    if status.get("exit_code") != 0:
                        raise RuntimeError("Genuine Dynamic Workflow failed; inspect sanitized evidence")
                    report = json.loads(await self.read(sandbox, f"{control}/result.json"))
                    await emit("sandbox.completed", sandbox_id=sandbox.sandbox_id)
                    # Orchestrator validates/persists report and diff before its finally cleanup.
                    return report
                await asyncio.sleep(1)
            raise TimeoutError("Workflow deadline exceeded")
        except BaseException:
            # TaskGroup first drains/cancels both roles. Orchestrator's finally then
            # cleans all durable intents, avoiding deletion while a peer is creating.
            raise

    async def checked_exec(self, sandbox, command, seconds):
        result = await self.call(sandbox.exec, f"timeout --kill-after=5s {seconds}s sh -c {shlex.quote(command)}")
        if result.exit_code != 0:
            raise RuntimeError("Sandbox command failed; raw output withheld")

    async def cleanup(self, value):
        lock = self.locks.setdefault(value["run_id"], asyncio.Lock())
        async with lock:
            # One failed ownership check/delete must not strand the other role.
            records = await self.store.ownership(value["run_id"])
            results = await asyncio.gather(
                *(self._cleanup_record(value, record) for record in records),
                return_exceptions=True,
            )
            for result in results:
                if isinstance(result, BaseException):
                    raise result

    async def _cleanup_record(self, value, record):
        if record["state"] == "deleted":
            return
        if record["state"] == "prepared":
            record["state"] = "deleted"  # No create request was started.
            await self.store.save_ownership(record)
            return
        labels = record["labels"]
        if labels != {
            "owner": OWNER,
            "run-id": value["run_id"],
            "role": record["role"],
            "nonce": record["nonce"],
        }:
            raise ValueError("Invalid ownership ledger")
        records = list(await self.call(lambda: list(self.group.list_sandboxes())))
        matches = [r for r in records if all((r.labels or {}).get(k) == v for k, v in labels.items())]
        if not record["sandbox_id"] and not matches:
            raise RuntimeError("Ambiguous creation requires manual owned-orphan reconciliation")
        ids = {r.id for r in matches}
        if record["sandbox_id"]:
            ids.add(record["sandbox_id"])
        for identifier in ids:
            sandbox = self.group.get_sandbox_client(identifier)
            try:
                model = await self.call(sandbox.get)
                if not all((model.labels or {}).get(k) == v for k, v in labels.items()):
                    raise ValueError("Refusing deletion after ownership mismatch")
            except ResourceNotFoundError:
                continue
            try:
                await self.events.emit(value["run_id"], record["role"], "sandbox.deleting", sandbox_id=identifier)
            except Exception:
                value["event_delivery_failed"] = True
            await self.call(sandbox.delete)
            for _ in range(30):
                try:
                    await self.call(sandbox.get)
                except ResourceNotFoundError:
                    break
                await asyncio.sleep(1)
            else:
                raise TimeoutError("Exact-ID deletion not confirmed")
        record["state"] = "deleted"
        await self.store.save_ownership(record)
        for identifier in ids:
            try:
                await self.events.emit(value["run_id"], record["role"], "sandbox.deleted", sandbox_id=identifier)
            except Exception:
                value["event_delivery_failed"] = True

    async def close(self):
        await self.call(self.group.close)
        if self.credential:
            await self.call(self.credential.close)
