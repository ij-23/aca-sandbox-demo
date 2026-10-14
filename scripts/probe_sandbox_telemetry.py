#!/usr/bin/env python3
"""Bounded, owned Sandbox telemetry probe using genuine container stdout."""

import json
import shlex
import time
from uuid import uuid4

import smoke_test_sandbox as smoke


def perform(group, path, scope, connection_id, **kwargs):
    run_id = str(uuid4())
    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    evidence = {
        "test": "telemetry-stdout",
        "group": scope,
        "labels": labels,
        "run_id": run_id,
        "status": "running",
        "cleanup": "not_required",
    }
    sandbox = None
    returned = requested = False
    before = set()
    try:
        with smoke.deadline(180):
            records = list(group.list_sandboxes())
            before = {s.id for s in records}
            evidence["before"] = [{"id": s.id, "state": s.state} for s in records]
            if any((s.labels or {}).get("owner") == smoke.OWNER for s in records):
                raise RuntimeError("Unresolved smoke ownership")
            marker = json.dumps(
                {
                    "source": "academo",
                    "run_id": run_id,
                    "sandbox_id": "creation-marker",
                    "role": "system",
                    "event_type": "telemetry.probe",
                    "step_id": "stdout",
                    "msg": "trusted stdout probe",
                }
            )
            command = f"while true; do printf '%s\\n' {shlex.quote(marker)}; sleep 5; done"
            smoke.save(path, evidence)
            requested = True
            started = time.monotonic()
            sandbox = group.begin_create_sandbox(
                disk="copilot",
                connections=[connection_id],
                cpu="1000m",
                memory="2048Mi",
                ports=[],
                labels=labels,
                entrypoint=["/bin/sh", "-c"],
                cmd=[command],
                auto_suspend_seconds=300,
                polling_timeout=80,
                polling_interval=2,
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=sandbox.sandbox_id, creation_seconds=round(time.monotonic() - started, 3))
            smoke.save(path, evidence)
            evidence["readback"] = group.verify_telemetry(sandbox.sandbox_id)
            probe = sandbox.exec("timeout 5s readlink /proc/1/fd/1")
            evidence["stdout_target"] = probe.stdout.strip()
            # Real container output while collection runs, not synthetic ingestion.
            for _ in range(7):
                time.sleep(10)
                print(json.dumps({"stage": "telemetry_collection", "run_id": run_id}), flush=True)
            evidence["status"] = "emitted_ingestion_not_yet_verified"
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            started = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(group, sandbox, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["cleanup_seconds"] = round(time.monotonic() - started, 3)
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(smoke.main(performer=perform))
