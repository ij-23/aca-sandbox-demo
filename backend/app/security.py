"""Input guards and redaction. Never run repository code in this module."""

import re
from typing import Any

import httpx

REPOSITORY = re.compile(r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9_.-]{1,100})\Z")
SECRET_KEY = re.compile(r"token|secret|password|authorization|cookie|api.?key", re.I)
TOKENS = re.compile(
    r"github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|(?i:Bearer)\s+\S+|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"
)


def redact(value: Any, depth: int = 0) -> Any:
    if depth > 12:
        return "[TRUNCATED]"
    if isinstance(value, str):
        return TOKENS.sub("[REDACTED]", value)[:100000]
    if isinstance(value, dict):
        return {
            str(k)[:100]: "[REDACTED]" if SECRET_KEY.search(str(k)) else redact(v, depth + 1)
            for k, v in list(value.items())[:100]
        }
    if isinstance(value, list):
        return [redact(v, depth + 1) for v in value[:200]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return "[UNSUPPORTED]"


def repository_parts(url: str, allowlist: tuple[str, ...]) -> tuple[str, str]:
    match = REPOSITORY.fullmatch(url)
    if not match or match[2] in (".", "..") or match[2].endswith(".git"):
        raise ValueError("Use a canonical https://github.com/owner/repository URL")
    if url.casefold() not in {v.casefold() for v in allowlist}:
        raise ValueError("Repository is not an approved trusted fixture")
    return match[1], match[2]


async def resolve_public_sha(url: str, allowlist: tuple[str, ...]) -> str:
    owner, repo = repository_parts(url, allowlist)
    async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False) as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
        )
        response.raise_for_status()
        data = response.json()
        if data.get("private") is not False or data.get("full_name", "").casefold() != f"{owner}/{repo}".casefold():
            raise ValueError("Repository must be public and have the requested identity")
        # HEAD resolves the default branch without embedding an untrusted branch name in a URL.
        response = await client.get(f"https://api.github.com/repos/{owner}/{repo}/commits/HEAD")
        response.raise_for_status()
        sha = response.json().get("sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("GitHub did not return a full commit SHA")
        return sha
