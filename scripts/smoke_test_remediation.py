#!/usr/bin/env python3
"""Prepared M0-C-FAIL: one approved Sandbox, genuine C, mandatory failed test, no GitHub writes.

Default is plan-only. Uses the original smoke's CLI context/connection preflight.
"""

import json
import shlex
import sys
import time
from pathlib import Path
from uuid import uuid4

import smoke_test_sandbox as smoke

ROOT = Path(__file__).resolve().parents[1]


def perform(group, path, scope, connection_id, **kwargs):
    nonce = uuid4().hex
    run_id = str(uuid4())
    labels = {"owner": smoke.OWNER, "smoke-run": nonce}
    evidence = {
        "test": "M0-C-FAIL",
        "run_id": run_id,
        "group": scope,
        "status": "running",
        "cleanup": "not_required",
        "create_requests": 0,
    }
    sandbox = None
    requested = returned = False
    before = set()
    started = time.monotonic()

    def execute(command, seconds=20):
        result = sandbox.exec(f"timeout --kill-after=5s {seconds}s sh -c {shlex.quote(command)}")
        if result.exit_code:
            raise RuntimeError("Trusted command failed; raw output withheld")
        return result.stdout

    try:
        with smoke.deadline(850):
            if not any(
                image.name == "copilot" and image.status.state == "Ready" for image in group.list_public_disk_images()
            ):
                raise RuntimeError("Built-in Copilot disk is not Ready")
            before = {r.id for r in group.list_sandboxes()}
            if any((r.labels or {}).get("owner") == smoke.OWNER for r in group.list_sandboxes()):
                raise RuntimeError("Previous smoke ownership requires cleanup")
            evidence["create_requests"] = 1
            requested = True
            smoke.save(path, evidence)
            t = time.monotonic()
            sandbox = group.begin_create_sandbox(
                disk="copilot",
                connections=[connection_id],
                cpu="1000m",
                memory="2048Mi",
                ports=[],
                labels=labels,
                auto_suspend_seconds=300,
                polling_timeout=80,
                polling_interval=2,
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=sandbox.sandbox_id, creation_seconds=round(time.monotonic() - t, 3))
            model = sandbox.get()
            if sandbox.sandbox_id in before or model.ports or connection_id not in (model.connections or []):
                raise RuntimeError("Unexpected sandbox scope")
            control = f"/tmp/academo-c-fail-{nonce}"
            execute(f"mkdir -p {control}/.github/extensions/remediation {control}/source && git -C {control} init -q")
            files = {
                ".github/extensions/remediation/extension.mjs": ROOT / "workflows/remediation/extension.mjs",
                ".github/runtime.mjs": ROOT / "workflows/shared/runtime.mjs",
                "operations.py": ROOT / "workflows/shared/operations.py",
                "runner.py": ROOT / "workflows/shared/runner.py",
                "cli_setup.py": ROOT / "scripts/smoke_workflow_runner.py",
            }
            for local in (ROOT / "demo-repo").rglob("*"):
                if local.is_file():
                    files["source/" + str(local.relative_to(ROOT / "demo-repo"))] = local
            for remote, local in files.items():
                sandbox.write_file(f"{control}/{remote}", local.read_bytes())
            execute(f"cd {control} && python3 cli_setup.py prepare-cli", 80)
            args = {
                "run_id": run_id,
                "role": "remediation",
                "publication_enabled": False,
                "fixture_upload": True,
                "repository_url": "uploaded:trusted-project-fixture",
                "finding": {"file": "app.py", "explanation": "Reject paths outside DOCUMENT_ROOT"},
                "approval": None,
            }
            sandbox.write_file(f"{control}/input.json", json.dumps(args))
            result = json.loads(execute(f"cd {control} && python3 operations.py prepare_fixture < input.json", 60))
            args["commit_sha"] = result["commit_sha"]
            sandbox.write_file(f"{control}/input.json", json.dumps(args))
            sandbox.write_file(f"{control}/events.jsonl", "")
            sandbox.write_file(f"{control}/status.json", '{"state":"pending"}')
            launch = "import subprocess; subprocess.Popen(['python3','runner.py'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)"
            execute(f"cd {control} && python3 -c {shlex.quote(launch)}")
            t = time.monotonic()
            count = 0
            while time.monotonic() - t < 750:
                status = json.loads(smoke.text_file(sandbox, f"{control}/status.json", 3000))
                events = [
                    json.loads(line)
                    for line in smoke.text_file(sandbox, f"{control}/events.jsonl", 2000000).split("\n")[:-1]
                    if line
                ]
                if len(events) != count:
                    print(
                        json.dumps(
                            {
                                "stage": "workflow",
                                "events": len(events),
                                "last_step": events[-1]["step_id"] if events else None,
                            }
                        ),
                        flush=True,
                    )
                    count = len(events)
                if status["state"] == "finished":
                    break
                time.sleep(1)
            else:
                raise TimeoutError("Workflow deadline")
            evidence.update(
                command=status, events=events, cli_log=smoke.text_file(sandbox, f"{control}/cli.sanitized.log", 100000)
            )
            if status.get("exit_code") != 0:
                raise RuntimeError("Genuine C workflow failed to complete")
            report = json.loads(smoke.text_file(sandbox, f"{control}/result.json", 200000))
            evidence["report"] = report
            tests = next((c for c in report["checks"] if c["name"] == "pytest"), {})
            if report["publication_status"] != "skipped" or report["status"] != "failed" or tests.get("exit_code") != 1:
                raise RuntimeError("Expected actual pytest failure and skipped publication")
            if any(
                e["step_id"] in ("create_repo", "push", "verify_remote") and e["type"] != "step.skipped" for e in events
            ):
                raise RuntimeError("Unexpected publication stage")
            if not any(e["step_id"] == "agent.fix" and e["type"] == "step.completed" for e in events):
                raise RuntimeError("Missing genuine Copilot fix step")
            evidence["status"] = "passed"
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            t = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(group, sandbox, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["cleanup_seconds"] = round(time.monotonic() - t, 3)
        evidence["total_seconds"] = round(time.monotonic() - started, 3)
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    if "--execute" not in sys.argv:
        print(
            json.dumps({"mode": "plan_only", "test": "M0-C-FAIL", "creates": 1, "github_writes": 0, "azure_calls": 0})
        )
    else:
        raise SystemExit(smoke.main(performer=perform))
