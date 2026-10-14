"""P0: genuine Copilot workflow delegates trusted arithmetic to another MicroVM.

Creates one coordinator and one connection-free worker; deletes both in finally.
No repository source, repository creation, publishing identity, or fake AI step.
"""

import json
import time
from uuid import uuid4

import smoke_test_sandbox as smoke
from azure.containerapps.sandbox import EgressPolicy, SandboxGroupClient
from probe_worker_isolation import PROBE, checks_pass


def factory(*args, telemetry_config, **kwargs):
    from app.sandbox_telemetry import TelemetrySandboxGroupClient

    group = TelemetrySandboxGroupClient(*args, telemetry_config=telemetry_config, **kwargs)
    worker_args = {**kwargs, "sandbox_group": kwargs["sandbox_group"] + "-workers"}
    group.worker_group = SandboxGroupClient(*args, **worker_args)
    group.probe_identity_id = telemetry_config["endpoints"][0]["auth"]["identity"]
    return group


def perform(group, path, scope, connection_id, **kwargs):
    worker_group = group.worker_group
    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    worker = None
    requested = returned = False
    before = set()
    evidence = {"test": "genuine-workflow-delegation", "status": "running", "cleanup": "not_required"}
    serviced = False

    def poll(sandbox, control, nonce):
        nonlocal serviced
        if serviced:
            return
        try:
            raw = sandbox.read_file(f"{control}/work-request.json")
        except Exception as error:
            if getattr(error, "status_code", None) == 404:
                return
            raise
        if not isinstance(raw, bytes) or len(raw) > 2000:
            raise ValueError("Invalid delegation envelope")
        request = json.loads(raw)
        if request != {"schema_version": 1, "nonce": nonce, "sequence": 1, "operation": "sum", "values": [2, 3]}:
            raise ValueError("Unapproved work request")
        serviced = True
        started = time.monotonic()
        # Fixed operator-authored code, never a shell command from the extension.
        result = worker.exec("timeout --kill-after=2s 5s python3 -c 'import json; print(json.dumps({\"sum\": 2 + 3}))'")
        if result.exit_code != 0 or json.loads(result.stdout) != {"sum": 5}:
            raise RuntimeError("Delegated operation failed")
        receipt = {"nonce": nonce, "sequence": 1, "operation": "sum", "exit_code": result.exit_code, "sum": 5}
        sandbox.write_file(f"{control}/work-response.tmp", json.dumps(receipt))
        moved = sandbox.exec(f"timeout 5s mv {control}/work-response.tmp {control}/work-response.json")
        if moved.exit_code != 0:
            raise RuntimeError("Response delivery failed")
        evidence["delegation"] = {
            "worker_sandbox_id": worker.sandbox_id,
            "exit_code": result.exit_code,
            "seconds": round(time.monotonic() - started, 3),
            "sum": 5,
        }

    try:
        with smoke.deadline(160):
            records = list(worker_group.list_sandboxes())
            before = {record.id for record in records}
            if any((record.labels or {}).get("owner") == smoke.OWNER for record in records):
                raise RuntimeError("Unresolved worker probe ownership")
            evidence["worker_labels"] = labels
            smoke.save(path, evidence)
            requested = True
            started = time.monotonic()
            worker = worker_group.begin_create_sandbox(
                disk="copilot",
                connections=[],
                ports=[],
                labels=labels,
                cpu="1000m",
                memory="2048Mi",
                auto_suspend_seconds=300,
                polling_timeout=80,
                polling_interval=2,
                entrypoint=["/bin/sh", "-c"],
                cmd=["exec sleep infinity"],
                egress_policy=EgressPolicy(default_action="Deny", traffic_inspection="Full", rules=[]),
            ).result(timeout=90)
            returned = True
            evidence.update(
                worker_sandbox_id=worker.sandbox_id, worker_creation_seconds=round(time.monotonic() - started, 3)
            )
            smoke.save(path, evidence)
            if worker.sandbox_id in before or worker.get().connections or worker.get().ports:
                raise RuntimeError("Unexpected worker ownership or configuration")
            worker.write_file("/tmp/worker-probe.py", PROBE)
            worker.write_file(
                "/tmp/worker-probe-settings.json", json.dumps({"identity_resource_id": group.probe_identity_id})
            )
            probe = worker.exec("timeout --kill-after=5s 40s python3 /tmp/worker-probe.py")
            if probe.exit_code != 0:
                raise RuntimeError("Worker isolation probe failed")
            evidence["worker_checks"] = json.loads(probe.stdout)
            if not checks_pass(evidence["worker_checks"]):
                raise RuntimeError("Worker credential boundary failed")
        coordinator_path = path.with_name(path.stem + "-coordinator.json")
        if coordinator_path.exists():
            raise ValueError("Preserve previous coordinator evidence")
        coordinator = smoke.perform(
            group,
            coordinator_path,
            scope,
            connection_id,
            extension=smoke.ROOT / "workflows/smoke-delegation/extension.mjs",
            poll_hook=poll,
            **kwargs,
        )
        evidence.update(
            coordinator_evidence=str(coordinator_path),
            coordinator_sandbox_id=coordinator.get("sandbox_id"),
            coordinator_status=coordinator["status"],
            coordinator_cleanup=coordinator["cleanup"],
        )
        if coordinator["status"] != "passed" or not serviced:
            raise RuntimeError("Genuine delegation workflow failed")
        evidence["status"] = "passed"
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            started = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(worker_group, worker, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["worker_cleanup_seconds"] = round(time.monotonic() - started, 3)
        worker_group.close()
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(
        smoke.main(
            performer=perform,
            client_factory=factory,
            plan_description="Create one coordinator and one connection-free worker in GROUP-workers; delegate trusted arithmetic through a genuine workflow; delete both",
        )
    )
