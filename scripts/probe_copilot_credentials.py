#!/usr/bin/env python3
"""One disposable Sandbox: read-only official Copilot SDK credential grant probe."""

import json
import shlex
import time
from pathlib import Path
from uuid import uuid4

import smoke_test_sandbox as smoke

ROOT = Path(__file__).resolve().parents[1]


def perform(group, path, scope, connection_id, **kwargs):
    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    evidence = {
        "test": "M0-credential-sdk",
        "group": scope,
        "labels": labels,
        "status": "running",
        "cleanup": "not_required",
    }
    sandbox = None
    requested = returned = False
    before = set()
    try:
        with smoke.deadline(350):
            records = list(group.list_sandboxes())
            before = {s.id for s in records}
            evidence["before"] = [{"id": s.id, "state": s.state} for s in records]
            if any((s.labels or {}).get("owner") == smoke.OWNER for s in records):
                raise RuntimeError("Existing smoke ownership")
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
                entrypoint=["/bin/sh", "-c"],
                cmd=["exec sleep infinity"],
                polling_timeout=80,
                polling_interval=2,
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=sandbox.sandbox_id, creation_seconds=round(time.monotonic() - t, 3))
            smoke.save(path, evidence)
            control = "/tmp/academo-credential-probe"

            def execute(cmd, seconds):
                result = sandbox.exec(f"timeout --kill-after=5s {seconds}s sh -c {shlex.quote(cmd)}")
                if result.exit_code:
                    raise RuntimeError("Trusted setup command failed")
                return result.stdout

            execute(
                f"mkdir -p {control}/.github/extensions/credential-probe {control}/sdk && git -C {control} init -q", 10
            )
            for remote, local in {
                "cli_setup.py": "scripts/smoke_workflow_runner.py",
                "host.mjs": "workflows/copilot-host/host.mjs",
                ".github/extensions/credential-probe/extension.mjs": "workflows/copilot-host/credential-probe.mjs",
                "sdk/package.json": "workflows/copilot-host/package.json",
                "sdk/package-lock.json": "workflows/copilot-host/package-lock.json",
                "publication-probe.py": "workflows/copilot-host/publication-probe.py",
            }.items():
                sandbox.write_file(f"{control}/{remote}", (ROOT / local).read_bytes())
            sandbox.write_file(
                f"{control}/input.json",
                json.dumps(
                    {
                        "workflow_name": "credential-probe",
                        "publication_probe": kwargs.get("publication_probe", False),
                        "retry_owned_empty": kwargs.get("retry_owned_empty", False),
                    }
                ),
            )
            execute(f"cd {control} && python3 cli_setup.py prepare-cli", 80)
            execute(
                f"cd {control} && npm ci --prefix sdk --ignore-scripts --omit=optional --fetch-timeout=15000 --fetch-retries=0 > install.log 2>&1",
                80,
            )
            # Output is sanitized in the Sandbox by the same trusted helper.
            sandbox.write_file(
                f"{control}/invoke.py",
                'import subprocess,os,json\nfrom pathlib import Path\nfrom cli_setup import sanitize\np=subprocess.run(["timeout","--kill-after=5s","90s","node","host.mjs"],capture_output=True,text=True,env=dict(os.environ,GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS="true",COPILOT_AUTO_UPDATE="false"),timeout=100)\nPath("probe.sanitized.json").write_text(json.dumps({"exit_code":p.returncode,"stdout":sanitize(p.stdout)[-20000:],"stderr":sanitize(p.stderr)[-10000:]}))\n',
            )
            execute(f"cd {control} && python3 invoke.py", 110)
            evidence["execution"] = json.loads(smoke.text_file(sandbox, f"{control}/probe.sanitized.json", 40000))
            if evidence["execution"]["exit_code"]:
                raise RuntimeError("SDK credential probe failed")
            evidence["result"] = json.loads(smoke.text_file(sandbox, f"{control}/result.json", 3000))
            passed = (
                evidence["result"].get("published") is True
                if kwargs.get("publication_probe")
                else evidence["result"].get("http_status") == 200
            )
            evidence["status"] = "passed" if passed else "failed"
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
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(smoke.main(performer=perform))
