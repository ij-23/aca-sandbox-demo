"""Trusted source inventory helper for credential-free workers ONLY.

No imports, hooks, repository instructions or configuration code are executed.
Unit tests use project-authored inert archives. Never invoke acquisition on the host.
"""

import gzip
import hashlib
import json
import re
import tarfile
import time
import urllib.request
from pathlib import Path, PurePosixPath

try:
    import tomllib
except ImportError:  # Built-in worker Python may predate 3.11; do not execute setup.py.
    tomllib = None

MAX_DOWNLOAD = 32 * 1024 * 1024
MAX_EXPANDED = 100 * 1024 * 1024
MAX_FILES = 10000
MAX_TEXT = 1024 * 1024
MAX_REVIEW = 512 * 1024
MAX_PATH = 250


class SourceRejected(ValueError):
    pass


def safe_path(name: str) -> PurePosixPath:
    if (
        not name
        or len(name) > MAX_PATH
        or "\\" in name
        or ":" in name
        or any(ord(char) < 32 or ord(char) == 127 for char in name)
        or name.startswith("/")
        or any(part.casefold() in ("", ".", "..", ".git") for part in name.split("/"))
    ):
        raise SourceRejected("Unsafe archive path")
    return PurePosixPath(name)


class LimitedReader:
    def __init__(self, source, maximum):
        self.source, self.remaining = source, maximum

    def read(self, size=-1):
        value = self.source.read(min(size if size >= 0 else self.remaining + 1, self.remaining + 1))
        self.remaining -= len(value)
        if self.remaining < 0:
            raise SourceRejected("Expanded archive exceeded limit")
        return value


def unpack(archive: Path, destination: Path, expected_root: str) -> dict:
    """Bound expansion including headers, reject all links/special/duplicate paths.

    Called before submitted code can run. Require a new directory; never merge
    into an existing worktree. Preserve bytes; do not copy archive permissions.
    """
    if archive.stat().st_size > MAX_DOWNLOAD:
        raise SourceRejected("Download exceeded limit")
    safe_path(expected_root)
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    inventory, seen, omissions = [], set(), []
    total, headers = 0, 0
    with gzip.open(archive, "rb") as compressed:
        with tarfile.open(fileobj=LimitedReader(compressed, MAX_EXPANDED), mode="r|") as tar:
            for entry in tar:
                headers += 1
                if headers > MAX_FILES * 2:
                    raise SourceRejected("Archive header count exceeded limit")
                name = entry.name.rstrip("/") if entry.isdir() else entry.name
                path = safe_path(name)
                if path.parts[0] != expected_root:
                    raise SourceRejected("Archive root differs from pinned source")
                if len(path.parts) == 1:
                    if not entry.isdir():
                        raise SourceRejected("Invalid archive root")
                    continue
                relative = PurePosixPath(*path.parts[1:]).as_posix()
                if relative.casefold() in seen:
                    raise SourceRejected("Duplicate or case-colliding archive path")
                seen.add(relative.casefold())
                if entry.issym():
                    # Do not materialize even an internal link. Validate its target
                    # lexically within the source root and disclose the omission.
                    link = entry.linkname
                    if (
                        not link
                        or len(link) > MAX_PATH
                        or link.startswith("/")
                        or "\\" in link
                        or ":" in link
                        or any(ord(char) < 32 or ord(char) == 127 for char in link)
                    ):
                        raise SourceRejected("Unsafe archive link")
                    target_parts = list(PurePosixPath(relative).parent.parts)
                    for part in link.split("/"):
                        if part == "..":
                            if not target_parts:
                                raise SourceRejected("Escaping archive link")
                            target_parts.pop()
                        elif part not in ("", "."):
                            if part.casefold() == ".git":
                                raise SourceRejected("Unsafe archive link")
                            target_parts.append(part)
                    omissions.append({"path": relative, "reason": "internal_symlink_not_materialized"})
                    continue
                if not entry.isfile() and not entry.isdir():
                    raise SourceRejected("Links and special archive files are unsupported")
                if entry.isdir():
                    continue
                total += entry.size
                if entry.size < 0 or total > MAX_EXPANDED or len(inventory) >= MAX_FILES:
                    raise SourceRejected("Source size or file count exceeded limit")
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                source = tar.extractfile(entry)
                if source is None:
                    raise SourceRejected("Missing archive content")
                digest = hashlib.sha256()
                with target.open("xb") as output:
                    while block := source.read(65536):
                        output.write(block)
                        digest.update(block)
                inventory.append({"path": relative, "bytes": entry.size, "sha256": digest.hexdigest()})
    return {"files": inventory, "total_bytes": total, "omissions": omissions}


def acquire(repository_url: str, sha: str, destination: Path) -> dict:
    """Sandbox-only network acquisition; immutable URL, no git hooks or redirects."""
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9-]{1,39})/([A-Za-z0-9_.-]{1,100})", repository_url)
    if not match or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SourceRejected("Invalid pinned repository identity")
    owner, repo = match.groups()
    safe_path(owner)
    safe_path(repo)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    # The archive lives in a separate fresh control directory owned by the worker.
    archive = destination.parent / "source.tar.gz"
    started, size = time.monotonic(), 0
    with opener.open(f"https://codeload.github.com/{owner}/{repo}/tar.gz/{sha}", timeout=15) as response:
        if response.status != 200:
            raise SourceRejected("Pinned source download unavailable")
        with archive.open("xb") as output:
            while block := response.read(65536):
                size += len(block)
                if size > MAX_DOWNLOAD or time.monotonic() - started > 60:
                    raise SourceRejected("Source download exceeded size or time budget")
                output.write(block)
    return unpack(archive, destination, f"{repo}-{sha}")


def discover(root: Path, inventory: dict) -> dict:
    """Detect candidates, never imply that a manifest proves runnable support."""
    manifests, licenses, sample, omissions, components = {}, [], {}, list(inventory.get("omissions", [])), []
    budget = MAX_REVIEW
    for item in sorted(inventory["files"], key=lambda item: item["path"]):
        path = item["path"]
        safe_path(path)
        file = root / path
        if file.is_symlink() or not file.is_file() or file.stat().st_size != item["bytes"]:
            raise SourceRejected("Source inventory changed")
        if item["bytes"] > MAX_TEXT:
            omissions.append({"path": path, "reason": "text_file_limit"})
            continue
        raw = file.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise SourceRejected("Source digest changed")
        try:
            if b"\0" in raw:
                raise UnicodeError
            text = raw.decode("utf-8")
        except UnicodeError:
            omissions.append({"path": path, "reason": "binary_or_non_utf8"})
            continue
        name = PurePosixPath(path).name
        if name.upper().startswith(("LICENSE", "COPYING", "NOTICE")):
            licenses.append(path)
        if name in (
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
        ):
            manifests[path] = text
        if raw.startswith(b"version https://git-lfs.github.com/spec/"):
            omissions.append({"path": path, "reason": "lfs_pointer_not_fetched"})
        if len(raw) <= budget:
            sample[path] = text
            budget -= len(raw)
        else:
            omissions.append({"path": path, "reason": "review_budget"})
    for path, text in manifests.items():
        name = PurePosixPath(path).name
        parent = str(PurePosixPath(path).parent)
        if name not in ("requirements.txt", "pyproject.toml", "package.json"):
            continue
        adapter = "node-npm-v1" if name == "package.json" else "python-pytest-v1"
        reasons = []
        runtime = None
        try:
            if name == "package.json":
                data = json.loads(text)
                lock = str(PurePosixPath(parent) / "package-lock.json")
                if lock not in manifests:
                    reasons.append("npm lockfile required by initial adapter")
                scripts = data.get("scripts", {})
                if not isinstance(scripts, dict) or not scripts.get("test"):
                    reasons.append("no test script declared")
                runtime = data.get("engines", {}).get("node")
                if data.get("workspaces"):
                    reasons.append("workspace selection is not yet supported")
            elif name == "pyproject.toml":
                if tomllib is None:
                    reasons.append("TOML parsing requires Python 3.11 or a verified parser")
                else:
                    data = tomllib.loads(text)
                    runtime = data.get("project", {}).get("requires-python")
        except (ValueError, TypeError, AttributeError, RecursionError):
            reasons.append("invalid or unsupported manifest")
        components.append(
            {
                "root": parent,
                "manifest": path,
                "adapter_candidate": adapter,
                "declared_runtime": runtime if isinstance(runtime, str) else None,
                "execution_status": "blocked",
                "reasons": reasons + ["adapter live verification pending"],
            }
        )
    return {
        "schema_version": 1,
        "files_total": len(inventory["files"]),
        "bytes_total": inventory["total_bytes"],
        "review_files": sample,
        "review_bytes": MAX_REVIEW - budget,
        "components": components,
        "license_files": licenses,
        "redistribution_status": "requires_review",
        "omissions": omissions,
        "limitations": [
            "Bounded source sample; no claim of complete review",
            "Submodules and LFS objects are not fetched",
            "Manifest detection does not execute configuration or prove build/test support",
        ],
    }
