#!/usr/bin/env python3
"""Milestone 0 smoke. Default is inert; --execute creates one paid sandbox.

No repository code is cloned or run. No token is read from local configuration.
SDK installation and real Azure execution remain separate verification gates.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from importlib.metadata import version
from pathlib import Path
from uuid import UUID, uuid4

SDK_VERSION = "0.1.0b4"
ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "workflows/smoke/extension.mjs"
OWNER = "aca-sandbox-demo-smoke"
REMOTE_RUNNER = ROOT / "scripts/smoke_workflow_runner.py"


class SmokeDeadline(BaseException):
    """Escape SDK Exception retry handlers when the local deadline expires."""


@contextmanager
def deadline(seconds):
    """Bound synchronous SDK calls on macOS/Linux, including cleanup separately."""

    def expired(_signum, _frame):
        raise SmokeDeadline("Local smoke deadline exceeded")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def save(path, evidence):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(evidence, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def text_file(sandbox, path, limit=16384):
    value = sandbox.read_file(path)
    if not isinstance(value, bytes) or len(value) > limit:
        raise ValueError("Unexpected file type or oversized evidence")
    return value.decode("utf-8")


def owned_records(group, labels):
    # Documentation disagrees on selector/labels keywords; list without either
    # and require exact ownership labels locally before considering deletion.
    return [
        item
        for item in group.list_sandboxes()
        if all(getattr(item, "labels", {}).get(k) == v for k, v in labels.items())
    ]


def cleanup(group, sandbox, labels, creation_returned, budget=60, protected_ids=()):
    """Delete only the returned sandbox and exact nonce-labeled matches."""
    if sandbox is not None:
        if sandbox.sandbox_id in protected_ids:
            raise RuntimeError("Refuse deleting a pre-existing sandbox")
        try:
            sandbox.delete()
        except Exception:
            # Reconcile and retry by exact ownership below; never delete a group.
            pass
    end = time.monotonic() + budget
    while time.monotonic() < end:
        remaining = owned_records(group, labels)
        if not remaining:
            # A lost create response may precede eventual server-side creation.
            # Empty listing alone cannot certify cleanup of that ambiguous case.
            if not creation_returned:
                raise RuntimeError("Ambiguous creation; manual orphan check required")
            # Listing can lag creation. Confirm the exact returned ID is gone.
            try:
                sandbox.get()
            except Exception as exc:
                if getattr(exc, "status_code", None) == 404:
                    return
                raise
            sandbox.delete()
            time.sleep(2)
            continue
        for item in remaining:
            if item.id in protected_ids:
                raise RuntimeError("Refuse deleting a pre-existing sandbox")
            group.get_sandbox_client(item.id).delete()
        time.sleep(2)
    raise TimeoutError("Owned sandbox deletion was not confirmed")


def read_events(sandbox, control, nonce, *, final=False):
    text = text_file(sandbox, f"{control}/smoke-events.jsonl", 32768)
    if final and text and not text.endswith("\n"):
        raise ValueError("Incomplete final event record")
    lines = text.split("\n")[:-1]  # Ignore a concurrently written partial line.
    events = [json.loads(line) for line in lines if line]
    for event in events:
        if (
            set(event) != {"timestamp", "workflow_run_id", "nonce", "step", "status"}
            or event["nonce"] != nonce
            or event["step"] not in {"prepare", "agent", "verify"}
            or event["status"] not in {"running", "passed", "failed"}
            or not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", event["workflow_run_id"])
            or not re.fullmatch(r"[0-9T:.Z+-]{20,35}", event["timestamp"])
        ):
            raise ValueError("Unexpected workflow event")
    return events


def validate_result(result, nonce, events):
    if (
        set(result) != {"nonce", "answer", "sum", "branch", "workflow_run_id", "steps"}
        or result["nonce"] != nonce
        or result["answer"] != "pong"
        or result["sum"] != 5
        or result["branch"] != "verified"
        or not isinstance(result["workflow_run_id"], str)
        or not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", result["workflow_run_id"])
    ):
        raise ValueError("Invalid workflow result or provenance")
    expected = [(step, status) for step in ("prepare", "agent", "verify") for status in ("running", "passed")]
    if [(e["step"], e["status"]) for e in events] != expected:
        raise ValueError("Missing real workflow boundaries")
    if any(e["workflow_run_id"] != result["workflow_run_id"] for e in events):
        raise ValueError("Event and result workflow IDs differ")
    steps = result["steps"]
    if not isinstance(steps, list) or len(steps) != 3:
        raise ValueError("Missing step results")
    outputs = [
        {"sum": 5, "observation_window_ms": 3000},
        {"nonce": nonce, "answer": "pong", "sum": 5},
        {"branch": "verified", "reason": "agent_matches_deterministic_result"},
    ]
    for step, name, output in zip(steps, ("prepare", "agent", "verify"), outputs, strict=True):
        if (
            set(step) != {"step", "status", "duration_ms", "result"}
            or step["step"] != name
            or step["status"] != "passed"
            or type(step["duration_ms"]) is not int
            or not 0 <= step["duration_ms"] <= 210000
            or step["result"] != output
        ):
            raise ValueError("Invalid step result")


def perform(group, path, scope, connection_id, extension=EXTENSION, *, expected_cli_version="1.0.97", pinned_cli=False):
    UUID(connection_id)
    nonce = uuid4().hex
    labels = {"owner": OWNER, "smoke-run": nonce}
    evidence = {
        "run_id": nonce,
        "group": scope,
        "sdk_version": SDK_VERSION,
        "disk": "copilot",
        "credential_connection_id": connection_id,
        "expected_cli_version": expected_cli_version,
        "pinned_cli_requested": pinned_cli,
        "labels": labels,
        "status": "running",
        "create_requests": 0,
        "cleanup": "not_required",
        "stage": "preflight",
        "observations": [],
    }
    sandbox = None
    creation_requested = creation_returned = False
    before = set()
    started = time.monotonic()

    def checkpoint(stage):
        evidence["stage"] = stage
        save(path, evidence)
        print(json.dumps({"stage": stage, "sandbox_id": evidence.get("sandbox_id")}), flush=True)

    def execute(command, seconds=20):
        result = sandbox.exec(f"timeout --kill-after=5s {seconds}s sh -c {shlex.quote(command)}")
        if result.exit_code != 0:
            evidence["failed_exec_exit_code"] = result.exit_code
            raise RuntimeError("SDK command failed; raw output withheld")
        return result

    try:
        with deadline(400):
            images = list(group.list_public_disk_images())
            if not any(image.name == "copilot" and image.status.state == "Ready" for image in images):
                raise RuntimeError("Built-in copilot disk not Ready")
            records = list(group.list_sandboxes())
            before = {r.id for r in records}
            evidence["before"] = [{"id": r.id, "state": r.state} for r in records]
            if any((r.labels or {}).get("owner") == OWNER for r in records):
                raise RuntimeError("Previous smoke sandbox exists; resolve it before retrying")
            evidence["create_requests"] = 1
            creation_requested = True
            checkpoint("create")
            t = time.monotonic()
            sandbox = group.begin_create_sandbox(
                disk="copilot",
                connections=[connection_id],
                cpu="1000m",
                memory="2048Mi",
                labels=labels,
                ports=[],
                entrypoint=["/bin/sh", "-c"],
                cmd=["exec sleep infinity"],
                auto_suspend_seconds=300,
                polling_timeout=80,
                polling_interval=2,
            ).result(timeout=90)
            creation_returned = True
            evidence["sandbox_id"] = sandbox.sandbox_id
            evidence["creation_seconds"] = round(time.monotonic() - t, 3)
            if sandbox.sandbox_id in before:
                raise RuntimeError("Creation returned a pre-existing sandbox")
            model = sandbox.get()
            if model.ports or connection_id not in (model.connections or []):
                raise RuntimeError("Unexpected ports or missing provider connection")
            checkpoint("capabilities")
            control = f"/tmp/aca-smoke-{nonce}"
            execute(f"mkdir -p {control}/.github/extensions/smoke && git -C {control} init -q")
            sandbox.write_file(f"{control}/runner.py", REMOTE_RUNNER.read_text())
            if pinned_cli:
                checkpoint("prepare_pinned_cli")
                prepared = execute(f"cd {control} && python3 runner.py prepare-cli", 80)
                evidence["cli_preparation"] = json.loads(prepared.stdout)
            probe = execute(f"cd {control} && python3 runner.py capabilities", 70)
            capabilities = json.loads(probe.stdout)
            evidence["capabilities"] = capabilities  # Helper redacts before SDK transfer.
            match = re.search(r"\b([0-9]+\.[0-9]+\.[0-9]+)\b", capabilities["version"]["stdout"])
            if not match or capabilities["version"]["exit_code"] != 0:
                raise RuntimeError("Copilot version unavailable")
            evidence["copilot_cli_version"] = match.group(1)
            if match.group(1) != expected_cli_version:
                raise RuntimeError("Copilot version differs from explicitly reviewed target")
            if not capabilities["environment"]["COPILOT_GITHUB_TOKEN"]:
                raise RuntimeError("Provider credential was not injected")
            if not all(flag in capabilities["workflow_help"]["stdout"] for flag in ("--args", "--result-file")):
                raise RuntimeError("Experimental direct Dynamic Workflow command not exposed")
            if not all(
                flag in capabilities["help"]["stdout"]
                for flag in (
                    "--no-auto-update",
                    "--no-custom-instructions",
                    "--disable-builtin-mcps",
                    "--available-tools",
                    "--deny-tool",
                )
            ):
                raise RuntimeError("Required CLI safety flags unavailable")
            checkpoint("upload")
            source = extension.read_text()
            remote_extension = f"{control}/.github/extensions/smoke/extension.mjs"
            sandbox.write_file(remote_extension, source)
            if text_file(sandbox, remote_extension, 20000) != source:
                raise RuntimeError("Extension upload verification failed")
            evidence["file_transfer_verified"] = True
            sandbox.write_file(f"{control}/input.json", json.dumps({"nonce": nonce}))
            sandbox.write_file(f"{control}/smoke-events.jsonl", "")
            sandbox.write_file(f"{control}/status.json", json.dumps({"state": "pending"}))
            launch = (
                "import subprocess; subprocess.Popen(['python3','runner.py','workflow'], "
                "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, "
                "start_new_session=True); print('started')"
            )
            checkpoint("workflow")
            t = time.monotonic()
            execute(f"cd {control} && python3 -c {shlex.quote(launch)}")
            evidence["live_progress_observed"] = False
            evidence["poll_count"] = 0
            last_count = -1
            while time.monotonic() - t < 235:
                status = json.loads(text_file(sandbox, f"{control}/status.json", 12000))
                events = read_events(sandbox, control, nonce)
                after = json.loads(text_file(sandbox, f"{control}/status.json", 12000))
                evidence["poll_count"] += 1
                if len(events) != last_count:
                    during = status["state"] == after["state"] == "running"
                    evidence["observations"].append(
                        {
                            "elapsed_seconds": round(time.monotonic() - t, 3),
                            "event_count": len(events),
                            "runner_running_before_and_after": during,
                            "last_step": events[-1]["step"] if events else None,
                            "last_status": events[-1]["status"] if events else None,
                        }
                    )
                    if during and events:
                        evidence["live_progress_observed"] = True
                    last_count = len(events)
                    checkpoint("workflow")
                if after["state"] == "finished":
                    status = after
                    break
                time.sleep(1)
            else:
                raise TimeoutError("Workflow observation deadline exceeded")
            evidence["workflow_seconds"] = status.get("seconds")
            evidence["workflow_command"] = status.get("command")
            evidence["exit_code"] = status.get("exit_code")
            evidence["cli_log"] = text_file(sandbox, f"{control}/command.sanitized.log", 100000)
            evidence["events"] = read_events(sandbox, control, nonce, final=True)
            if status.get("exit_code") != 0:
                raise RuntimeError("Genuine workflow command failed")
            checkpoint("results")
            result = json.loads(text_file(sandbox, f"{control}/result.json", 20000))
            validate_result(result, nonce, evidence["events"])
            evidence["result"] = result
            evidence["authentication"] = "workflow_agent_succeeded_without_login"
            evidence["output_transport"] = (
                "SDK file polling during detached workflow; exec itself returns completed output"
            )
            evidence["status"] = "passed"
            checkpoint("complete")
    except BaseException as exc:
        evidence["status"] = "failed"
        evidence["error_type"] = type(exc).__name__
        # Only locally defined fixed messages are safe to retain.
        if type(exc) in (RuntimeError, ValueError, TimeoutError) and exc.args:
            allowed = (
                "Experimental direct Dynamic Workflow command not exposed",
                "Genuine workflow command failed",
                "Provider credential was not injected",
                "Copilot version differs from explicitly reviewed target",
                "Invalid workflow result or provenance",
                "Missing real workflow boundaries",
                "Invalid step result",
                "Workflow observation deadline exceeded",
                "Required CLI safety flags unavailable",
            )
            if str(exc) in allowed:
                evidence["error"] = str(exc)
    finally:
        if creation_requested:
            # A full/read-only local disk must not bypass cloud cleanup.
            try:
                checkpoint("cleanup")
            except OSError:
                evidence["evidence_persistence_failed"] = True
                evidence["status"] = "failed"
            t = time.monotonic()
            try:
                with deadline(100):
                    cleanup(group, sandbox, labels, creation_returned, budget=80, protected_ids=before)
                    remaining = list(group.list_sandboxes())
                    evidence["after"] = [{"id": r.id, "state": r.state} for r in remaining]
                    if any(r.id == evidence.get("sandbox_id") for r in remaining):
                        raise RuntimeError("Deleted sandbox remains listed")
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as exc:
                evidence["cleanup"] = "unconfirmed"
                evidence["cleanup_error_type"] = type(exc).__name__
                evidence["status"] = "failed"
            evidence["cleanup_seconds"] = round(time.monotonic() - t, 3)
        evidence["total_seconds"] = round(time.monotonic() - started, 3)
        checkpoint("finished")
    return evidence


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--subscription-id", required=True)
    p.add_argument("--tenant-id", required=True)
    p.add_argument("--resource-group", required=True)
    p.add_argument("--sandbox-group", required=True)
    p.add_argument("--region", required=True)
    p.add_argument(
        "--credential-connection-id", help="Existing Ready github-copilot group connection UUID (not a token)"
    )
    p.add_argument(
        "--expected-cli-version", default="1.0.97", help="Exact statically reviewed version; never auto-update"
    )
    p.add_argument(
        "--pinned-cli",
        action="store_true",
        help="Download checksum-pinned official 1.0.97 into the owned disposable Sandbox control directory",
    )
    p.add_argument("--execute", action="store_true", help="Create/run/delete one bounded Sandbox within the authorized group")
    p.add_argument("--confirm-group", help="Exact approved Sandbox Group ARM ID")
    p.add_argument("--output", type=Path, default=ROOT / ".local/smoke-evidence.json")
    p.add_argument("--telemetry-config", type=Path, help="Terraform-exported non-secret telemetryConfig JSON")
    return p


def main(argv=None, *, performer=perform):
    args = parser().parse_args(argv)
    UUID(args.subscription_id)
    UUID(args.tenant_id)
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.expected_cli_version):
        raise ValueError("Invalid CLI version")
    if args.pinned_cli and args.expected_cli_version != "1.0.97":
        raise ValueError("Pinned artifact is CLI 1.0.97 only")
    if not re.fullmatch(r"[a-z0-9]+", args.region):
        raise ValueError("Invalid region")
    for value in (args.resource_group, args.sandbox_group):
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,90}", value):
            raise ValueError("Invalid resource name")
    scope = (
        f"/subscriptions/{args.subscription_id}/resourceGroups/{args.resource_group}"
        f"/providers/Microsoft.App/sandboxGroups/{args.sandbox_group}"
    )
    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": "plan_only",
                    "scope": scope,
                    "disk": "copilot",
                    "action": "create one sandbox, run real workflow, collect result, delete",
                    "credential_connection_id": args.credential_connection_id,
                    "expected_cli_version": args.expected_cli_version,
                    "pinned_cli_requested": args.pinned_cli,
                    "azure_calls": 0,
                }
            )
        )
        return 0
    if args.confirm_group != scope:
        raise ValueError("--confirm-group must match the approved ARM scope exactly")
    if not args.credential_connection_id:
        raise ValueError("--credential-connection-id is required for live execution")
    UUID(args.credential_connection_id)
    if not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Run this bounded smoke on Linux or macOS")
    if args.output.exists():
        raise ValueError("Use a fresh evidence path; preserve previous ownership records")
    if version("azure-containerapps-sandbox") != SDK_VERSION:
        raise RuntimeError("Install the exact pinned sandbox SDK")
    # Lazy imports ensure plan-only mode and unit tests never contact Azure.
    from azure.containerapps.sandbox import endpoint_for_region
    from azure.core.pipeline.transport import RequestsTransport
    from azure.identity import DefaultAzureCredential

    sys.path.insert(0, str(ROOT / "backend"))
    from app.sandbox_telemetry import TelemetrySandboxGroupClient

    if not args.telemetry_config:
        raise ValueError("--telemetry-config is required for every live Sandbox")

    account = json.loads(subprocess.check_output(["az", "account", "show", "-o", "json"], timeout=20))
    if account["id"] != args.subscription_id or account["tenantId"] != args.tenant_id:
        raise ValueError("Select the approved cached Azure CLI subscription/tenant before execution")
    metadata = subprocess.run(
        [
            "aca",
            "sandboxgroup",
            "credential",
            "list",
            "--subscription",
            args.subscription_id,
            "--resource-group",
            args.resource_group,
            "--group",
            args.sandbox_group,
            "--region",
            args.region,
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=40,
    )
    if metadata.returncode != 0:
        raise RuntimeError("Read-only credential status check failed; output withheld")
    if not any(
        r["id"] == args.credential_connection_id and r["type"] == "github-copilot" and r["state"] == "Ready"
        for r in json.loads(metadata.stdout)
    ):
        raise ValueError("Expected Ready github-copilot credential connection not found")
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_workload_identity_credential=True,
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=True,
        exclude_powershell_credential=True,
        exclude_developer_cli_credential=True,
        exclude_interactive_browser_credential=True,
        exclude_broker_credential=True,
        process_timeout=15,
    )
    group = TelemetrySandboxGroupClient(
        endpoint_for_region(args.region),
        credential,
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        sandbox_group=args.sandbox_group,
        telemetry_config=json.loads(args.telemetry_config.read_text()),
        transport=RequestsTransport(connection_timeout=10, read_timeout=90),
        retry_total=0,
    )

    def terminate(_signum, _frame):
        raise KeyboardInterrupt("Termination requested")

    signal.signal(signal.SIGTERM, terminate)
    try:
        evidence = performer(
            group,
            args.output,
            scope,
            args.credential_connection_id,
            expected_cli_version=args.expected_cli_version,
            pinned_cli=args.pinned_cli,
        )
    finally:
        group.close()
        credential.close()
    print(json.dumps({"status": evidence["status"], "cleanup": evidence["cleanup"], "evidence": str(args.output)}))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "blocked", "error_type": type(exc).__name__}), file=sys.stderr)
        sys.exit(2)
