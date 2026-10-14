"""Harmless same-PAT creation/push probe; execute only in an owned Sandbox."""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

owner = "ij-23"
name = "academo-pat-check-20261014"
token = os.environ["COPILOT_GITHUB_TOKEN"]
result = {"published": False, "created": False, "http_status": None}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def api(method, path, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "User-Agent": "academo-credential-probe",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as response:
            result["http_status"] = response.status
            result["accepted_permissions"] = response.headers.get("X-Accepted-GitHub-Permissions", "")[:300]
            return response.status, json.loads(response.read(100000))
    except urllib.error.HTTPError as error:
        result["http_status"] = error.code
        result["accepted_permissions"] = error.headers.get("X-Accepted-GitHub-Permissions", "")[:300]
        return error.code, None


try:
    status, user = api("GET", "/user")
    if status != 200 or user["login"] != owner or user["type"] != "User":
        raise ValueError("Owner mismatch")
    status, existing = api("GET", f"/repos/{owner}/{name}")
    retry_owned = sys.argv[1:] == ["retry-owned-empty"]
    if retry_owned:
        if (
            status != 200
            or existing["id"] != 1418649119
            or existing["full_name"] != f"{owner}/{name}"
            or existing["private"] is not True
            or existing["size"] != 0
        ):
            raise ValueError("Owned empty repository not verified")
        ref_status, _ = api("GET", f"/repos/{owner}/{name}/git/ref/heads/main")
        if ref_status not in (404, 409):
            raise ValueError("Ref already exists; refusing overwrite")
    elif status != 404:
        raise ValueError("Destination collision or access error")
    directory = Path("harmless-publication").resolve()
    directory.mkdir(exist_ok=False)
    (directory / "README.md").write_text(
        "# Academo credential verification\n\nHarmless test push from a disposable ACA Sandbox.\n"
    )
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")

    def git(*args):
        return (
            subprocess.check_output(
                ["git", "-c", "core.hooksPath=/dev/null", *args],
                cwd=directory,
                env=env,
                stderr=subprocess.PIPE,
                timeout=40,
            )
            .decode()
            .strip()
        )

    git("init", "-b", "main")
    git("add", "README.md")
    git(
        "-c",
        "user.name=Academo demo",
        "-c",
        "user.email=academo@users.noreply.github.com",
        "commit",
        "-m",
        "Verify harmless Sandbox publication",
    )
    sha = git("rev-parse", "HEAD")
    result["creation_attempted"] = not retry_owned
    if retry_owned:
        repo = existing
    else:
        status, repo = api("POST", "/user/repos", {"name": name, "private": True, "auto_init": False})
        if status != 201:
            raise ValueError("Creation rejected or ambiguous")
    result.update(created=True, repository_url=repo["html_url"])
    if repo["private"] is not True or repo["full_name"] != f"{owner}/{name}":
        raise ValueError("Remote mismatch")
    helper = Path("git-probe-helper.py").resolve()
    helper.write_text(
        'import os,sys\nif sys.argv[1]=="get":\n print("username=x-access-token")\n print("password="+os.environ["COPILOT_GITHUB_TOKEN"])\n'
    )
    git(
        "-c",
        "credential.helper=",
        "-c",
        f"credential.helper=!python3 {helper}",
        "push",
        f"https://github.com/{owner}/{name}.git",
        "HEAD:refs/heads/main",
    )
    status, ref = api("GET", f"/repos/{owner}/{name}/git/ref/heads/main")
    if status != 200 or ref["object"]["sha"] != sha:
        raise ValueError("Remote SHA mismatch")
    status, verified = api("GET", f"/repos/{owner}/{name}")
    if status != 200 or verified["id"] != repo["id"] or verified["private"] is not True:
        raise ValueError("Privacy mismatch")
    result.update(published=True, private=True, commit_sha=sha)
except Exception as error:
    result["error_type"] = type(error).__name__
    if isinstance(error, subprocess.CalledProcessError):
        result["git_exit_code"] = error.returncode
        result["git_error"] = (error.stderr or b"").decode(errors="replace").replace(token, "[REDACTED]")[:4000]
print(json.dumps(result))
