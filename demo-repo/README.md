# Sandbox-only trusted FastAPI fixture

This small fixture is intentionally vulnerable to document path traversal. It is
for a dedicated disposable demonstration account and isolated ACA Sandboxes only.
Do not deploy it publicly or run its app/tests on the developer computer, backend
host or CI runner. It has no external calls, startup hooks or credential handling.

The source serves `/healthz` and `/document?name=hello.txt`. The document route joins
an input path without enforcing containment. Sandbox A can identify this through
non-executing source inspection. Sandbox B's pytest run should expose two failing
containment regressions, using temporary harmless canary files. It must report the
actual result and skip runtime testing after test failure. The remediation smoke executed these tests inside an ACA Sandbox on 2026-10-14.
A genuine Copilot fix passed the original cases; the deliberately added smoke-only
failure prevented publication. Full deployed A/B/C acceptance remains separate.

Sandbox C should resolve the requested path, require it to remain under the
resolved document root, return 403 on escape and preserve valid-file/404 behavior.
The workflow must run the unchanged tests and targeted recheck before publication.
Never weaken/delete tests to make validation pass. The final private repository
must include tests, documents, dependency lock and this explanation.

This directory is published as the vetted `ij-23/academo-fastapi-fixture` source
under the project authorization. The dashboard allowlist must use that exact URL.
The original source remains unchanged when C creates a separate private fixed repository.

Dependencies are pinned in `requirements.in`; `requirements.txt` is the generated
SHA256 lock. These commands are **for execution inside a purpose-created Sandbox**:

```sh
python3 -m venv .venv  # requires ensurepip; the workflow bootstraps pinned pip if absent
.venv/bin/pip install --require-hashes -r requirements.txt
.venv/bin/python -m pytest -q
# Only after successful validation, if the workflow selects the runtime branch:
.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080 --no-access-log
```

The application is never exposed through Sandbox public ingress. Copy the project
license when separately publishing this fixture; preserve attribution in fixes.
