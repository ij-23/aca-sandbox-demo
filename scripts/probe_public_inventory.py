"""Read-only public corpus inventory inside ONE connection-free disposable VM.

Metadata on the host, all archive download/parsing in the worker. Never build,
import, install, clone, run hooks, call Copilot or publish submitted code here.
"""

import asyncio
import json
import sys
import time
from uuid import uuid4

import smoke_test_sandbox as smoke
from azure.containerapps.sandbox import EgressPolicy, EgressRule, EgressRuleAction, EgressRuleMatch
from probe_worker_isolation import PROBE, checks_pass, without_telemetry

RUNNER_BODY = """import json
from pathlib import Path
from public_source import acquire,discover
corpus=json.loads(Path('/tmp/inventory-probe/input.json').read_text())
results=[]
for index,repo in enumerate(corpus):
 control=Path('/tmp/inventory-probe')/str(index)
 control.mkdir()
 inventory=acquire(repo['repository_url'],repo['commit_sha'],control/'source')
 report=discover(control/'source',inventory)
 # Source text remains in this worker. Export counts and detected capability only.
 results.append({'repository_url':repo['repository_url'],'commit_sha':repo['commit_sha'],
 'files_total':report['files_total'],'bytes_total':report['bytes_total'],
 'review_file_count':len(report['review_files']),'review_bytes':report['review_bytes'],
 'omission_count':len(report['omissions']),'components':report['components'],
 'license_file_count':len(report['license_files']),'redistribution_status':report['redistribution_status']})
Path('/tmp/inventory-probe/result.json').write_text(json.dumps(results))
"""


RUNNER = (
    "import json,sys\ntry:\n"
    + "".join(" " + line + "\n" for line in RUNNER_BODY.splitlines())
    + "except BaseException as error:\n print(json.dumps({'error_type':type(error).__name__,'reason':str(error) if type(error).__name__=='SourceRejected' else None}))\n sys.exit(1)\n"
)


def perform(group, path, scope, connection_id, **kwargs):
    sys.path.insert(0, str(smoke.ROOT / "backend"))
    from app.repositories import resolve_repository

    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    evidence = {"test": "public-source-inventory", "status": "running", "cleanup": "not_required", "labels": labels}
    worker = None
    requested = returned = False
    before = set()
    try:
        with smoke.deadline(280):
            corpus = [
                asyncio.run(resolve_repository(url)).model_dump()
                for url in ("https://github.com/pallets/flask", "https://github.com/sindresorhus/is")
            ]
            evidence["corpus"] = [
                {key: repo[key] for key in ("repository_id", "repository_url", "commit_sha")} for repo in corpus
            ]
            records = list(group.list_sandboxes())
            before = {record.id for record in records}
            if any((record.labels or {}).get("owner") == smoke.OWNER for record in records):
                raise RuntimeError("Unresolved probe ownership")
            smoke.save(path, evidence)
            requested = True
            started = time.monotonic()
            worker = group.begin_create_sandbox(
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
                egress_policy=EgressPolicy(
                    default_action="Deny",
                    traffic_inspection="Full",
                    rules=[
                        EgressRule(
                            name="source",
                            match=EgressRuleMatch(host="codeload.github.com"),
                            action=EgressRuleAction(type="Allow"),
                        )
                    ],
                ),
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=worker.sandbox_id, creation_seconds=round(time.monotonic() - started, 3))
            smoke.save(path, evidence)
            if worker.sandbox_id in before or worker.get().connections or worker.get().ports:
                raise RuntimeError("Unexpected worker binding")
            worker.write_file("/tmp/worker-probe.py", PROBE)
            worker.write_file(
                "/tmp/worker-probe-settings.json", json.dumps({"identity_resource_id": group.probe_identity_id})
            )
            result = worker.exec("timeout --kill-after=5s 40s python3 /tmp/worker-probe.py")
            if result.exit_code != 0 or not checks_pass(json.loads(result.stdout)):
                raise RuntimeError("Worker credential/network gate failed")
            evidence["worker_checks"] = json.loads(result.stdout)
            if worker.exec("timeout 5s mkdir /tmp/inventory-probe").exit_code != 0:
                raise RuntimeError("Control directory creation failed")
            worker.write_file(
                "/tmp/inventory-probe/public_source.py", (smoke.ROOT / "workflows/shared/public_source.py").read_text()
            )
            worker.write_file("/tmp/inventory-probe/run.py", RUNNER)
            worker.write_file("/tmp/inventory-probe/input.json", json.dumps(corpus))
            started = time.monotonic()
            result = worker.exec("timeout --kill-after=5s 140s python3 /tmp/inventory-probe/run.py")
            evidence.update(exit_code=result.exit_code, inventory_seconds=round(time.monotonic() - started, 3))
            if result.exit_code != 0:
                diagnostic = json.loads(result.stdout)
                evidence["worker_error_type"] = diagnostic.get("error_type")
                evidence["worker_error_reason"] = diagnostic.get("reason")
                raise RuntimeError("Source inventory failed; raw output withheld")
            raw = worker.read_file("/tmp/inventory-probe/result.json")
            if not isinstance(raw, bytes) or len(raw) > 100000:
                raise ValueError("Invalid inventory result")
            evidence["results"] = json.loads(raw)
            if len(evidence["results"]) != 2:
                raise ValueError("Incomplete corpus result")
            evidence["status"] = "passed"
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            started = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(group, worker, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["cleanup_seconds"] = round(time.monotonic() - started, 3)
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(
        smoke.main(
            performer=perform,
            client_factory=without_telemetry,
            require_connection=False,
            plan_description="Resolve two public repository SHAs; create one credential-free worker; inventory source without executing it; delete",
        )
    )
