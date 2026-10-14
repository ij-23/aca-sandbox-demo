# Sandbox-only trusted FastAPI fixture

This small fixture is intentionally vulnerable to document path traversal. It is
for a dedicated disposable demonstration account and isolated ACA Sandboxes only.
Do not deploy it publicly or run its app/tests on the developer computer, backend
host or CI runner. It has no external calls, startup hooks or credential handling.

The source serves `/healthz` and `/document?name=hello.txt`. The document route joins
an input path without enforcing containment. Sandbox A can identify this through
non-executing source inspection. Sandbox B's pytest run should expose two failing
containment regressions, using temporary harmless canary files. It must report the
actual result and skip runtime testing after test failure. The fixture tests have
**not been run** yet; those expected outcomes are design intent, not evidence.

Sandbox C should resolve the requested path, require it to remain under the
resolved document root, return 403 on escape and preserve valid-file/404 behavior.
The workflow must run the unchanged tests and targeted recheck before publication.
Never weaken/delete tests to make validation pass. The final private repository
must include tests, documents, dependency lock and this explanation.

Publish this directory as a standalone public fixture repository only after the
owner and publication are explicitly approved. The dashboard allowlist must use
that exact URL. No fixture repository has been created or cloned by the agent.

Dependencies are pinned in `requirements.in`; `requirements.txt` is the generated
SHA256 lock. These commands are **for execution inside a purpose-created Sandbox**:

```sh
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.txt
.venv/bin/python -m pytest -q
# Only after successful validation, if the workflow selects the runtime branch:
.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080 --no-access-log
```

The application is never exposed through Sandbox public ingress. Copy the project
license when separately publishing this fixture; preserve attribution in fixes.
