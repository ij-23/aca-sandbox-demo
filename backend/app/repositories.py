"""Public GitHub metadata only. Source parsing and execution belong in workers."""

import asyncio
import json
import re
from typing import Literal

import httpx
from pydantic import Field

from .contracts import SHA, StrictModel
from .security import REPOSITORY

RepositoryMode = Literal["trusted_fixture", "public_analysis", "public_execution"]


class RepositoryError(ValueError):
    """Stable user-facing error without response bodies or request credentials."""


class PublicRepository(StrictModel):
    schema_version: Literal[1] = 1
    repository_id: int = Field(gt=0)
    repository_url: str
    full_name: str
    commit_sha: SHA
    archived: bool
    license_spdx: str | None = Field(max_length=100)
    default_branch: str = Field(max_length=255)
    limitations: list[str]


def public_repository_parts(url: str) -> tuple[str, str]:
    match = REPOSITORY.fullmatch(url)
    if not match or not match[2].strip(".") or match[2].lower().endswith(".git"):
        raise RepositoryError("Use a canonical https://github.com/owner/repository URL")
    return match[1], match[2]


def admit_repository(url: str, mode: RepositoryMode, allowlist: tuple[str, ...]) -> tuple[str, str]:
    parts = public_repository_parts(url)
    if mode not in ("trusted_fixture", "public_analysis", "public_execution"):
        raise RepositoryError("Unknown repository policy")
    if mode == "trusted_fixture" and url.casefold() not in {item.casefold() for item in allowlist}:
        raise RepositoryError("Repository is not an approved trusted fixture")
    return parts


async def _get(client: httpx.AsyncClient, path: str) -> dict:
    # Absolute host is fixed. Never follow redirects or include authentication.
    async with client.stream(
        "GET",
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    ) as response:
        if response.status_code in (301, 302, 307, 308):
            raise RepositoryError("Repository moved; submit its current canonical GitHub URL")
        if response.status_code in (403, 429):
            raise RepositoryError("GitHub access or rate limit prevents lookup; retry later")
        if response.status_code == 404:
            raise RepositoryError("Public repository or commit not found")
        if response.status_code in (409, 422):
            raise RepositoryError("Repository has no resolvable default commit")
        if response.status_code != 200:
            raise RepositoryError("GitHub metadata is temporarily unavailable")
        content = bytearray()
        async for chunk in response.aiter_bytes(chunk_size=65536):
            content.extend(chunk)
            if len(content) > 1048576:
                raise RepositoryError("GitHub metadata exceeded the response limit")
        try:
            result = json.loads(content)
        except (ValueError, UnicodeError):
            raise RepositoryError("GitHub metadata was invalid") from None
        if not isinstance(result, dict):
            raise RepositoryError("GitHub metadata was invalid")
        return result


async def resolve_repository(url: str, *, transport=None) -> PublicRepository:
    owner, repo = public_repository_parts(url)
    try:
        async with (
            asyncio.timeout(25),
            httpx.AsyncClient(timeout=10, follow_redirects=False, trust_env=False, transport=transport) as client,
        ):
            path = f"/repos/{owner}/{repo}"
            data = await _get(client, path)
            if (
                data.get("private") is not False
                or data.get("visibility") != "public"
                or str(data.get("full_name", "")).casefold() != f"{owner}/{repo}".casefold()
                or type(data.get("id")) is not int
                or data["id"] <= 0
                or type(data.get("archived")) is not bool
                or not isinstance(data.get("default_branch"), str)
                or not data["default_branch"]
            ):
                raise RepositoryError("Repository must be public and have the requested identity")
            commit = await _get(client, path + "/commits/HEAD")
            sha = commit.get("sha")
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
                raise RepositoryError("GitHub did not return a full commit SHA")
            license_data = data.get("license")
            license_id = license_data.get("spdx_id") if isinstance(license_data, dict) else None
            if not isinstance(license_id, str) or license_id in ("NOASSERTION", "", "NONE"):
                license_id = None
            return PublicRepository(
                repository_id=data["id"],
                repository_url=f"https://github.com/{data['full_name']}",
                full_name=data["full_name"],
                commit_sha=sha,
                archived=data["archived"],
                license_spdx=license_id,
                default_branch=data["default_branch"],
                limitations=[
                    "Metadata lookup does not execute code or establish build support",
                    "GitHub license metadata does not authorize redistribution; pinned source license review is required",
                ],
            )
    except (TimeoutError, httpx.HTTPError):
        raise RepositoryError("GitHub lookup timed out or is temporarily unavailable") from None
