"""Live deployed-runtime drills; invoke only inside the project Container App.

Runs real A/B Sandboxes and real Blob persistence, never fixture code on the host.
This verifies runtime cancellation/reconciliation, not browser authentication.
Run during a quiet demo window. No remediation or GitHub publication is performed.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.config import Settings
from app.orchestrator import Orchestrator
from app.sandbox import SandboxExecutor
from app.store import BlobStore, Events


def components(identifier=None):
    settings = Settings.from_env()
    if not settings.live_execution_enabled or not settings.managed_identity_client_id:
        raise RuntimeError("Requires the configured Azure host managed identity")

    class ScopedStore(BlobStore):
        async def runs(self):
            if identifier:
                return [await self.get_run(identifier)]
            return await super().runs()

    store = ScopedStore(settings.storage_account, settings.managed_identity_client_id)
    events = Events(store, settings.event_retention_limit)
    executor = SandboxExecutor(settings, store, events)
    return settings, store, events, executor, Orchestrator(settings, store, events, executor)


async def worker(mode, marker):
    settings, store, events, executor, runtime = components()
    value = None
    try:
        if any(r.get("cleanup_pending") for r in await store.runs()):
            raise RuntimeError("Another run needs cleanup; refuse drill")
        value = await runtime.start(settings.allowed_repositories[0], settings.authorized_users[0])
        marker.write_text(value["run_id"])
        async with asyncio.timeout(70):
            while True:
                records = await store.ownership(value["run_id"])
                observed = await store.events(value["run_id"])
                started_roles = {e["sandbox_role"] for e in observed if e["type"] == "step.started"}
                if (
                    len(records) == 2
                    and all(r["state"] == "running" for r in records)
                    and started_roles >= {"security", "build"}
                ):
                    break
                if value["status"] != "running":
                    raise RuntimeError("Run ended before interruption boundary")
                await asyncio.sleep(0.2)
        if mode == "interrupt":
            # Deliberately terminate only this owned drill worker. The supervising
            # process uses durable ownership to reconcile the actual Sandboxes.
            os._exit(73)
        await runtime.cancel(value)
    finally:
        await runtime.shutdown()
        if value:
            await runtime._cleanup(await store.get_run(value["run_id"]))
        await executor.close()
        await store.close()


async def recover_and_verify(identifier, mode):
    settings, store, events, executor, runtime = components(identifier)
    try:
        await runtime.reconcile()
        value = await store.get_run(identifier)
        records = await store.ownership(identifier)
        observed = await store.events(identifier)
        inventory = await executor.call(lambda: list(executor.group.list_sandboxes()))
        present = {s.id for s in inventory}
        expected = "interrupted" if mode == "interrupt" else "cancelled"
        result = {
            "mode": mode,
            "run_id": identifier,
            "status": value["status"],
            "finished_at": value.get("finished_at"),
            "sandbox_ids": [r["sandbox_id"] for r in records],
            "deleted_records": all(r["state"] == "deleted" for r in records),
            "absent_from_inventory": all(r["sandbox_id"] not in present for r in records),
            "cleanup_pending": value.get("cleanup_pending"),
            "events_contiguous": all(e["event_id"] == n for n, e in enumerate(observed, 1)),
            "interruption_event": any(e["type"] == "run.interrupted" for e in observed),
            "workflow_started_roles": sorted({e["sandbox_role"] for e in observed if e["type"] == "step.started"}),
            "event_count": len(observed),
        }
        result["passed"] = (
            value["status"] == expected
            and len(records) == 2
            and result["deleted_records"]
            and result["absent_from_inventory"]
            and not result["cleanup_pending"]
            and result["events_contiguous"]
            and bool(result["finished_at"])
            and result["workflow_started_roles"] == ["build", "security"]
            and (mode != "interrupt" or result["interruption_event"])
        )
        return result
    finally:
        await executor.close()
        await store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("cancel", "interrupt"))
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        asyncio.run(worker(args.mode, args.worker))
        return 0
    started = time.monotonic()
    result = {"mode": args.mode, "passed": False}
    with tempfile.TemporaryDirectory(prefix="academo-recovery-") as directory:
        marker = Path(directory) / "run-id"
        process = subprocess.Popen(
            [sys.executable, __file__, args.mode, "--worker", str(marker)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            result["worker_exit"] = process.wait(timeout=150)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
            result["worker_timeout"] = True
        finally:
            if marker.exists():
                identifier = marker.read_text().strip()
                # Always reconcile only this real run, even if its worker failed.
                try:
                    with_cleanup = asyncio.run(asyncio.wait_for(recover_and_verify(identifier, args.mode), 120))
                    result.update(with_cleanup)
                    result["passed"] = result["passed"] and result.get("worker_exit") == (
                        73 if args.mode == "interrupt" else 0
                    )
                except Exception as error:
                    result.update(run_id=identifier, cleanup_error_type=type(error).__name__, passed=False)
        result["duration_seconds"] = round(time.monotonic() - started, 3)
        print(json.dumps(result), flush=True)
        return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
