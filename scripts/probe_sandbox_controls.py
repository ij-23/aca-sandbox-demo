"""Live timeout/egress probe; trusted commands only, with mandatory owned cleanup."""

import time
from uuid import uuid4

import smoke_test_sandbox as smoke
from azure.containerapps.sandbox import EgressPolicy, EgressRule, EgressRuleAction, EgressRuleMatch


def perform(group, path, scope, connection_id, **kwargs):
    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    evidence = {"test": "sandbox-controls", "group": scope, "labels": labels, "status": "running"}
    sandbox = None
    requested = returned = False
    before = set()
    try:
        with smoke.deadline(150):
            records = list(group.list_sandboxes())
            before = {r.id for r in records}
            if any((r.labels or {}).get("owner") == smoke.OWNER for r in records):
                raise RuntimeError("Unresolved smoke ownership")
            evidence["before"] = [{"id": r.id, "state": r.state} for r in records]
            requested = True
            smoke.save(path, evidence)
            start = time.monotonic()
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
                egress_policy=EgressPolicy(
                    default_action="Deny",
                    traffic_inspection="Full",
                    rules=[
                        EgressRule(
                            name="github",
                            match=EgressRuleMatch(host="github.com"),
                            action=EgressRuleAction(type="Allow"),
                        )
                    ],
                ),
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=sandbox.sandbox_id, creation_seconds=round(time.monotonic() - start, 3))
            smoke.save(path, evidence)
            result = sandbox.exec("timeout --kill-after=1s 1s sleep 10")
            evidence["timeout_exit_code"] = result.exit_code
            for name, host in (("allowed", "github.com"), ("denied", "example.com")):
                result = sandbox.exec(
                    f"timeout 20s curl -sS --max-time 12 -o /tmp/{name}.txt -w '%{{http_code}}' https://{host}/"
                )
                evidence[name] = {"exit_code": result.exit_code, "http_status": result.stdout.strip()}
            evidence["denied_response"] = smoke.text_file(sandbox, "/tmp/denied.txt", 10000)
            if evidence["timeout_exit_code"] != 124 or evidence["allowed"]["http_status"] != "200":
                raise RuntimeError("Timeout or allow control failed")
            if evidence["denied"]["http_status"] != "403":
                raise RuntimeError("Expected explicit egress rejection was not observed")
            evidence["status"] = "passed"
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            start = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(group, sandbox, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["cleanup_seconds"] = round(time.monotonic() - start, 3)
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(smoke.main(performer=perform))
