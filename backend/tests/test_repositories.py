"""Explicit GitHub transport doubles; no repositories are downloaded/executed."""

import asyncio

import httpx
import pytest
from app.repositories import RepositoryError, admit_repository, resolve_repository

URL = "https://github.com/example/library"
SHA = "a" * 40
METADATA = {
    "id": 12,
    "private": False,
    "visibility": "public",
    "full_name": "example/library",
    "archived": False,
    "default_branch": "main",
    "license": {"spdx_id": "MIT"},
}


def lookup(metadata=None, commit=None, status=200):
    def serve(request):
        assert request.url.host == "api.github.com"
        assert "authorization" not in request.headers
        if request.url.path.endswith("/commits/HEAD"):
            return httpx.Response(200, json=commit if commit is not None else {"sha": SHA})
        return httpx.Response(status, json=metadata if metadata is not None else METADATA)

    return asyncio.run(resolve_repository(URL, transport=httpx.MockTransport(serve)))


def test_public_admission_is_explicit_and_does_not_broaden_fixture_mode():
    for mode in ("public_analysis", "public_execution"):
        assert admit_repository(URL, mode, ()) == ("example", "library")
    for mode in ("trusted_fixture", "", "anything"):
        with pytest.raises(RepositoryError):
            admit_repository(URL, mode, ())


@pytest.mark.parametrize("suffix", [".git", ".GIT", "/", "?x=1", "#x", "%2f.."])
def test_noncanonical_urls_are_rejected(suffix):
    with pytest.raises(RepositoryError):
        admit_repository(URL + suffix, "public_analysis", ())


def test_metadata_has_immutable_identity_and_does_not_authorize_publication():
    result = lookup()
    assert (result.repository_id, result.commit_sha, result.license_spdx) == (12, SHA, "MIT")
    assert "redistribution" in result.limitations[1]
    assert lookup({**METADATA, "license": None}).license_spdx is None


@pytest.mark.parametrize(
    "changes",
    [
        {"private": True},
        {"visibility": "private"},
        {"full_name": "other/repo"},
        {"id": True},
        {"id": -1},
        {"default_branch": ""},
    ],
)
def test_identity_mismatch_fails(changes):
    with pytest.raises(RepositoryError):
        lookup({**METADATA, **changes})


@pytest.mark.parametrize("status", [301, 302, 307, 308, 403, 404, 409, 422, 429, 500])
def test_errors_are_explicit_and_do_not_follow_redirects(status):
    with pytest.raises(RepositoryError):
        lookup(status=status)


@pytest.mark.parametrize("sha", [None, "main", "A" * 40, "a" * 39, 1])
def test_invalid_sha_rejected(sha):
    with pytest.raises(RepositoryError):
        lookup(commit={"sha": sha})


def test_metadata_size_bounded():
    with pytest.raises(RepositoryError, match="response limit"):
        lookup({**METADATA, "padding": "x" * 1048576})


def test_metadata_endpoint_requires_entra_authentication():
    from test_security import client, token

    with client() as c:
        assert c.post("/api/repositories/inspect", json={"repository_url": URL}).status_code == 401
        # Invalid URLs are rejected locally and still consume the cooldown.
        headers = {"Authorization": "Bearer " + token()}
        assert (
            c.post(
                "/api/repositories/inspect", headers=headers, json={"repository_url": "http://localhost"}
            ).status_code
            == 422
        )
        assert c.post("/api/repositories/inspect", headers=headers, json={"repository_url": URL}).status_code == 429
