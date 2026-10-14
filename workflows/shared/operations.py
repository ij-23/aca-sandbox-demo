"""Trusted operations executed ONLY inside disposable ACA Sandboxes.

Never import or invoke this module to execute fixture code on a host or in CI.
"""

import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "source"
SECRET = re.compile(r"github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|eyJ[\w-]+\.[\w-]+\.[\w-]+")


def redact(value):
    text = str(value)
    for name, secret in os.environ.items():
        if secret and re.search(r"token|secret|password|api.?key", name, re.I):
            text = text.replace(secret, "[REDACTED]")
    return SECRET.sub("[REDACTED]", text)


def event(data, kind, step, **payload):
    with (ROOT / "events.jsonl").open("a") as file:
        file.write(
            json.dumps(
                {
                    "run_id": data["run_id"],
                    "workflow_run_id": data.get("workflow_run_id", "operation"),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "type": kind,
                    "step_id": step,
                    "payload": json.loads(redact(json.dumps(payload))),
                }
            )
            + "\n"
        )


def clean_env():
    # Build processes do not need publishing credentials. This is defense in depth,
    # not a security boundary against malicious code sharing this sandbox.
    return {k: v for k, v in os.environ.items() if not re.search(r"token|secret|password|api.?key", k, re.I)} | {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "PYTHONPATH": "",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PIP_CONFIG_FILE": "/dev/null",
    }


def command(data, name, args, timeout=60, cwd=SOURCE, env=None):
    started = time.monotonic()
    log = ROOT / "operation.log"
    with log.open("wb") as output:
        child = subprocess.Popen(
            args,
            cwd=cwd,
            env=env or clean_env(),
            stdout=output,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
            code = 124
    with log.open("rb") as output:
        raw = output.read(12000).decode(errors="replace")
    detail = redact(raw)
    check = {
        "name": name,
        "status": "passed" if code == 0 else "timed_out" if code == 124 else "failed",
        "exit_code": code,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "detail": detail[:4000],
    }
    event(data, "command.output", name, command=args, **check)
    return check


def source_manifest():
    files = {}
    for path in SOURCE.rglob("*"):
        rel = path.relative_to(SOURCE)
        if any(p in {".git", "__pycache__", ".pytest_cache", ".venv"} for p in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError("Source symlinks are not supported")
        if path.is_file():
            if path.stat().st_size > 200000 or len(files) >= 100:
                raise ValueError("Fixture exceeds source limits")
            files[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def checkout(data):
    if data.get("fixture_upload") is True:
        # Smoke-only trusted file upload; never accepted by the public backend API.
        actual = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, env=clean_env(), timeout=10)
            .decode()
            .strip()
        )
        if actual != data["commit_sha"] or data.get("publication_enabled") is not False:
            raise ValueError("Uploaded-fixture smoke scope mismatch")
        return {"status": "passed", "commit_sha": actual, "source": "trusted_uploaded_fixture"}
    url, sha = data["repository_url"], data["commit_sha"]
    if not re.fullmatch(r"https://github.com/[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{1,100}", url):
        raise ValueError("Invalid repository")
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Invalid SHA")
    SOURCE.mkdir(exist_ok=False)
    for name, args in [
        ("git.init", ["git", "init", "-q"]),
        (
            "git.fetch",
            [
                "git",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "protocol.file.allow=never",
                "fetch",
                "--depth=1",
                url,
                sha,
            ],
        ),
        ("git.checkout", ["git", "-c", "core.hooksPath=/dev/null", "checkout", "--detach", "FETCH_HEAD"]),
    ]:
        if command(data, name, args, 60)["exit_code"] != 0:
            raise ValueError("Pinned checkout failed")
    actual = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, env=clean_env(), timeout=10).decode().strip()
    )
    if actual != sha:
        raise ValueError("Checkout SHA mismatch")
    manifest = source_manifest()
    if not {"app.py", "test_app.py", "requirements.txt"}.issubset(manifest):
        raise ValueError("Only the reviewed Python/FastAPI fixture layout is supported")
    (ROOT / "manifest.json").write_text(json.dumps(manifest))
    return {"status": "passed", "commit_sha": actual, "file_count": len(manifest)}


def prepare_fixture(data):
    # Only the separate, explicitly approved M0 harness invokes this action.
    if data.get("fixture_upload") is not True or data.get("publication_enabled") is not False:
        raise ValueError("Fixture preparation is smoke-only")
    with (SOURCE / "test_app.py").open("a") as file:
        file.write(
            '\n\ndef test_m0_required_validation_failure():\n    assert False, "Deliberate M0 no-publication branch"\n'
        )
    for args in (
        ["git", "init", "-q"],
        ["git", "add", "--all"],
        [
            "git",
            "-c",
            "user.name=Academo smoke",
            "-c",
            "user.email=academo@users.noreply.github.com",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-qm",
            "Trusted M0 fixture",
        ],
    ):
        if command(data, "fixture.prepare", args, 20)["exit_code"] != 0:
            raise ValueError("Fixture preparation failed")
    sha = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, env=clean_env(), timeout=10).decode().strip()
    )
    (ROOT / "manifest.json").write_text(json.dumps(source_manifest()))
    return {"commit_sha": sha}


def inspect_source(data):
    files = {}
    for name in source_manifest():
        if name.endswith(".py"):
            content = (SOURCE / name).read_text()
            if SECRET.search(content):
                raise ValueError("Potential credential in source; review stopped")
            files[name] = content
    if sum(map(len, files.values())) > 50000:
        raise ValueError("Source review budget exceeded")
    return {"status": "passed", "files": files}


def review(data):
    candidates = data["candidate"]["findings"]
    if not isinstance(candidates, list) or len(candidates) > 20:
        raise ValueError("Invalid review result")
    files = inspect_source(data)["files"]
    findings = []
    for index, candidate in enumerate(candidates):
        name, line, evidence = candidate["file"], candidate["line"], candidate["evidence"]
        content = files.get(name, "").splitlines()
        verified = (
            type(line) is int
            and 1 <= line <= len(content)
            and bool(evidence.strip())
            and evidence.strip() in content[line - 1]
        )
        findings.append(
            {
                "id": f"source-{index + 1}",
                "severity": "high",
                "category": "source-review",
                "file": name,
                "line": line,
                "evidence": evidence,
                "explanation": candidate["explanation"],
                "recommendation": candidate["recommendation"],
                "confidence": "medium",
                "verification_status": "verified" if verified else "unverified",
            }
        )
    return {
        "commit_sha": data["commit_sha"],
        "status": "passed",
        "findings": findings,
        "checks": [
            {
                "name": "source-evidence",
                "status": "passed",
                "exit_code": 0,
                "duration_ms": 0,
                "detail": "Exact quoted line correspondence checked; exploitability is not established",
            },
            {
                "name": "semgrep-gitleaks",
                "status": "skipped",
                "exit_code": None,
                "duration_ms": 0,
                "detail": "No pinned scanner installed; no scan claimed",
            },
        ],
        "limitations": [
            "Static Copilot review; no repository code executed in A",
            "Verified means matching source evidence, not proven exploitability",
        ],
    }


def patch(data):
    content = data["patch"]["content"]
    if not isinstance(content, str) or len(content) > 30000 or SECRET.search(content):
        raise ValueError("Invalid patch content")
    ast.parse(content)
    (SOURCE / "app.py").write_text(content)
    return {"status": "passed", "file": "app.py"}


def validate(data):
    checks = []
    counts = {"tests_passed": 0, "tests_failed": 0, "tests_skipped": 0}
    python = str(ROOT / "venv/bin/python")
    steps = [
        ("venv", ["python3", "-m", "venv", str(ROOT / "venv")], 30),
        (
            "dependencies",
            [
                python,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--require-hashes",
                "--only-binary=:all:",
                "--index-url",
                "https://pypi.org/simple/",
                "-r",
                "requirements.txt",
            ],
            120,
        ),
        ("build", [python, "-c", "import app; assert app.app is not None"], 20),
        ("pytest", [python, "-m", "pytest", "test_app.py", "-q", f"--junitxml={ROOT / 'pytest.xml'}"], 45),
    ]
    for name, args, timeout in steps:
        result = command(data, name, args, timeout)
        checks.append(result)
        if name == "pytest" and (ROOT / "pytest.xml").exists():
            suites = ET.parse(ROOT / "pytest.xml").getroot()
            cases = list(suites.iter("testcase"))
            counts["tests_failed"] = sum(c.find("failure") is not None or c.find("error") is not None for c in cases)
            counts["tests_skipped"] = sum(c.find("skipped") is not None for c in cases)
            counts["tests_passed"] = len(cases) - counts["tests_failed"] - counts["tests_skipped"]
        if result["status"] != "passed":
            break
    health = "skipped"
    if len(checks) == 4 and all(c["status"] == "passed" for c in checks) and counts["tests_passed"]:
        with (ROOT / "health.log").open("wb") as log:
            server = subprocess.Popen(
                [python, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8765"],
                cwd=SOURCE,
                env=clean_env(),
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
            started = time.monotonic()
            try:
                for _ in range(30):
                    try:
                        with urllib.request.urlopen("http://127.0.0.1:8765/healthz", timeout=1) as response:
                            if response.status == 200 and json.loads(response.read(1000)) == {"status": "ok"}:
                                health = "passed"
                                break
                    except (OSError, ValueError):
                        pass
                    time.sleep(0.2)
                else:
                    health = "failed"
            finally:
                if server.poll() is None:
                    os.killpg(server.pid, signal.SIGTERM)
                    try:
                        server.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(server.pid, signal.SIGKILL)
                        server.wait(timeout=5)
            checks.append(
                {
                    "name": "localhost.health",
                    "status": health,
                    "exit_code": 0 if health == "passed" else 1,
                    "duration_ms": round((time.monotonic() - started) * 1000),
                    "detail": "127.0.0.1:8765/healthz; server stopped",
                }
            )
    return {
        "commit_sha": data["commit_sha"],
        "status": "passed" if health == "passed" else "failed",
        "checks": checks,
        **counts,
        "health": health,
        "limitations": [
            "Only reviewed app.py/test_app.py fixture layout",
            "No public ingress or destructive runtime tests",
        ],
    }


def gate(data):
    validation = data["validation"]
    original = json.loads((ROOT / "manifest.json").read_text())
    current = source_manifest()
    unchanged = set(current) == set(original) and all(current[k] == v for k, v in original.items() if k != "app.py")
    checks = list(validation["checks"])
    target = (
        command(
            data,
            "targeted.recheck",
            [
                str(ROOT / "venv/bin/python"),
                "-m",
                "pytest",
                "test_app.py",
                "-q",
                "-k",
                "path_traversal or absolute_outside",
            ],
            30,
        )
        if validation["status"] == "passed"
        else {
            "name": "targeted.recheck",
            "status": "skipped",
            "exit_code": None,
            "duration_ms": 0,
            "detail": "Required validation failed",
        }
    )
    checks.append(target)
    checks.append(
        {
            "name": "source.integrity",
            "status": "passed" if unchanged else "failed",
            "exit_code": 0 if unchanged else 1,
            "duration_ms": 0,
            "detail": "Only app.py may change; tests/dependencies preserved",
        }
    )
    diff = subprocess.check_output(
        ["git", "--no-pager", "diff", "--no-ext-diff", "--", "app.py"], cwd=SOURCE, env=clean_env(), timeout=10
    ).decode()
    passed = (
        unchanged
        and bool(diff)
        and validation["status"] == "passed"
        and validation["tests_passed"] > 0
        and all(c["status"] == "passed" for c in checks)
    )
    return {
        "commit_sha": data["commit_sha"],
        "status": "passed" if passed else "failed",
        "checks": checks,
        "publication_status": "skipped",
        "fixed_repository_url": None,
        "fixed_commit_sha": None,
        "diff": redact(diff)[:100000],
        "limitations": ["Publication requires explicit authorization and supported extension credential access"],
    }


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def publish(data):
    report = data["report"]
    approval = data.get("approval") or {}
    # No token is accepted in request data; only the supported extension grant.
    token = os.environ.get("COPILOT_GITHUB_TOKEN")
    if not data.get("publication_enabled") or approval.get("approved") is not True:
        raise ValueError("Publication not authorized")
    if not token:
        report.update(status="failed", publication_status="failed")
        report["limitations"].append("Copilot extension did not receive approved provider credential access")
        return report
    owner, name = approval.get("destination_owner", ""), approval.get("destination_name", "")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", owner) or name != data["repository_url"].rsplit("/", 1)[1] + "-fixed":
        raise ValueError("Destination does not match explicit approval")
    if (
        approval.get("commit_sha") != data["commit_sha"]
        or report["status"] != "passed"
        or not {"build", "pytest", "localhost.health", "targeted.recheck", "source.integrity"}.issubset(
            {c["name"] for c in report["checks"]}
        )
        or not all(c["status"] == "passed" and c["exit_code"] == 0 for c in report["checks"])
    ):
        raise ValueError("Required validation/approval gate failed")
    destination = f"https://github.com/{owner}/{name}"
    opener = urllib.request.build_opener(NoRedirect())

    def api(method, path, body=None):
        request = urllib.request.Request(
            "https://api.github.com" + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "academo-trusted-demo",
            },
        )
        try:
            with opener.open(request, timeout=20) as response:
                content = response.read(200001)
                if len(content) > 200000:
                    raise ValueError("GitHub response exceeds limit")
                permission = response.headers.get("X-Accepted-GitHub-Permissions", "")
                event(
                    data,
                    "workflow.log",
                    "publication.gate",
                    accepted_permissions=permission[:300],
                    http_status=response.status,
                )
                return response.status, json.loads(content)
        except urllib.error.HTTPError as error:
            event(
                data,
                "workflow.log",
                "publication.gate",
                http_status=error.code,
                accepted_permissions=error.headers.get("X-Accepted-GitHub-Permissions", "")[:300],
            )
            return error.code, None

    post_started = False
    try:
        code, user = api("GET", "/user")
        if code != 200 or user["login"].lower() != owner.lower() or user.get("type") != "User":
            raise ValueError("PAT personal owner mismatch")
        code, _ = api("GET", f"/repos/{owner}/{name}")
        if code != 404:
            raise ValueError("Destination already exists or cannot be safely checked")
        # Export clean source before any remote mutation. No old history or hidden config.
        export = ROOT / "publish-source"
        export.mkdir(exist_ok=False)
        for relative in source_manifest():
            parts = Path(relative).parts
            if any(part.startswith(".") for part in parts) or relative.endswith((".pem", ".key", ".pfx")):
                continue
            source = SOURCE / relative
            content = source.read_bytes()
            if SECRET.search(content.decode(errors="replace")) or token.encode() in content:
                raise ValueError("Sensitive content rejected before publication")
            target = export / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        # Commit before creating the remote, so local preparation cannot leave an empty repo.
        for args in (
            ["git", "init", "-b", "main"],
            ["git", "add", "--all"],
            [
                "git",
                "-c",
                "user.name=Academo demo",
                "-c",
                "user.email=academo@users.noreply.github.com",
                "-c",
                "core.hooksPath=/dev/null",
                "commit",
                "-m",
                "Fix validated demo vulnerability",
            ],
        ):
            if command(data, "publication.prepare", args, 20, export)["exit_code"] != 0:
                raise ValueError("Clean publication commit failed")
        sha = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=export, env=clean_env(), timeout=10)
            .decode()
            .strip()
        )
        event(data, "step.started", "create_repo", status="running", destination=destination)
        post_started = True
        code, repo = api(
            "POST",
            "/user/repos",
            {
                "name": name,
                "private": True,
                "auto_init": False,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
            },
        )
        if code != 201:
            if 400 <= code < 500:
                post_started = False  # Definite rejection, including name collision.
            raise ValueError("Repository creation failed or outcome is ambiguous")
        if (
            repo["full_name"].lower() != f"{owner}/{name}".lower()
            or repo["private"] is not True
            or repo["html_url"].lower() != destination.lower()
        ):
            raise ValueError("Created repository identity mismatch")
        report.update(publication_status="partial", fixed_repository_url=destination)
        event(data, "step.completed", "create_repo", status="passed", repository_id=repo["id"], destination=destination)
        event(data, "step.started", "push", status="running")
        # Helper contains no credential; git receives it over its private helper pipe.
        helper = ROOT / "git-credential-demo.py"
        helper.write_text(
            'import os,sys\nif sys.argv[1] == "get":\n print("username=x-access-token")\n print("password=" + os.environ["COPILOT_GITHUB_TOKEN"])\n'
        )
        helper.chmod(0o700)
        env = clean_env() | {"COPILOT_GITHUB_TOKEN": token}
        args = [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            f"credential.helper=!python3 {helper}",
            "-c",
            "core.hooksPath=/dev/null",
            "push",
            destination + ".git",
            "HEAD:refs/heads/main",
        ]
        push = command(data, "push", args, 60, export, env)
        if push["exit_code"] != 0:
            raise ValueError("Push failed; repository may be partially populated")
        event(data, "step.completed", "push", status="passed")
        event(data, "step.started", "verify_remote", status="running")
        code, verify = api("GET", f"/repos/{owner}/{name}")
        ref_code, ref = api("GET", f"/repos/{owner}/{name}/git/ref/heads/main")
        if (
            code != 200
            or verify["id"] != repo["id"]
            or verify["private"] is not True
            or ref_code != 200
            or ref["object"]["sha"] != sha
        ):
            raise ValueError("Remote identity/privacy/SHA verification failed")
        report.update(status="passed", publication_status="published", fixed_commit_sha=sha)
        report["limitations"] = ["Trusted fixture demo; publication identity must be separated for production"]
        event(data, "step.completed", "verify_remote", status="passed", commit_sha=sha)
    except Exception as error:
        report.update(status="failed", publication_status="partial" if post_started else "failed")
        if post_started:
            report["fixed_repository_url"] = destination
        report["limitations"].append(
            "Publication stopped: "
            + type(error).__name__
            + "; inspect destination before any retry; no automatic overwrite or deletion"
        )
        event(data, "workflow.branch", "publication.gate", status="failed", reason=report["limitations"][-1])
    return report


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        action = sys.argv[1]
        functions = {
            "prepare_fixture": prepare_fixture,
            "checkout": checkout,
            "inspect": inspect_source,
            "review": review,
            "patch": patch,
            "validate": validate,
            "gate": gate,
            "publish": publish,
        }
        print(redact(json.dumps(functions[action](data))))
    except Exception as exc:
        # Fixed class only; never propagate exception messages/headers/token-bearing args.
        print(json.dumps({"error_type": type(exc).__name__, "status": "failed"}), file=sys.stderr)
        raise SystemExit(1) from None
