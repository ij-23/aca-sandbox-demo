"""Trusted helper unit tests; no fixture execution, network, git push or Copilot."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "workflow_operations", Path(__file__).resolve().parents[2] / "workflows/shared/operations.py"
)
operations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(operations)


def test_publication_without_consent_cannot_access_network(monkeypatch):
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(
        operations.urllib.request, "build_opener", lambda *_: pytest.fail("network must not be constructed")
    )
    with pytest.raises(ValueError, match="not authorized"):
        operations.publish({"report": {}, "publication_enabled": False})


def test_missing_extension_credential_fails_closed(monkeypatch):
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    result = operations.publish(
        {"publication_enabled": True, "approval": {"approved": True}, "report": {"limitations": []}}
    )
    assert result["publication_status"] == "failed"


def test_failed_validation_prevents_api_and_push(monkeypatch):
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(
        operations.urllib.request, "build_opener", lambda *_: pytest.fail("no network after failed tests")
    )
    with pytest.raises(ValueError, match="validation"):
        operations.publish(
            {
                "publication_enabled": True,
                "repository_url": "https://github.com/example/fixture",
                "commit_sha": "a" * 40,
                "approval": {
                    "approved": True,
                    "commit_sha": "a" * 40,
                    "destination_owner": "example",
                    "destination_name": "fixture-fixed",
                },
                "report": {"status": "failed", "checks": []},
            }
        )


def test_patch_rejects_invalid_python_without_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(operations, "SOURCE", tmp_path)
    with pytest.raises(SyntaxError):
        operations.patch({"patch": {"content": "invalid python ?"}})
    assert not (tmp_path / "app.py").exists()


def test_source_manifest_rejects_symlinks(tmp_path, monkeypatch):
    monkeypatch.setattr(operations, "SOURCE", tmp_path)
    (tmp_path / "unsafe").symlink_to("/etc/passwd")
    with pytest.raises(ValueError, match="symlinks"):
        operations.source_manifest()


def publication_input():
    return {
        "publication_enabled": True,
        "run_id": "unit-test",
        "repository_url": "https://github.com/example/fixture",
        "commit_sha": "a" * 40,
        "approval": {
            "approved": True,
            "destination_owner": "example",
            "destination_name": "fixture-fixed",
            "commit_sha": "a" * 40,
        },
        "report": {
            "status": "passed",
            "checks": [
                {"name": n, "status": "passed", "exit_code": 0}
                for n in ["build", "pytest", "localhost.health", "targeted.recheck", "source.integrity"]
            ],
            "limitations": [],
            "fixed_repository_url": None,
        },
    }


@pytest.mark.parametrize("name", ["fixture-fixed", "custom-private-repo"])
def test_publication_collision_never_pushes(monkeypatch, name):
    import io
    import json

    class Response(io.BytesIO):
        status = 200
        headers = {}

    class Opener:
        calls = 0

        def open(self, request, **kwargs):
            self.calls += 1
            assert request.method == "GET"
            body = {"login": "example", "type": "User"} if self.calls == 1 else {"id": 42}
            return Response(json.dumps(body).encode())

    opener = Opener()
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(operations.urllib.request, "build_opener", lambda *_: opener)
    monkeypatch.setattr(operations, "event", lambda *args, **kwargs: None)
    monkeypatch.setattr(operations, "command", lambda *args, **kwargs: pytest.fail("collision must not invoke git"))
    data = publication_input()
    data["approval"]["destination_name"] = name
    report = operations.publish(data)
    assert report["publication_status"] == "failed" and opener.calls == 2


@pytest.mark.parametrize("name", ["fixture-fixed", "My-custom_fix.2026"])
@pytest.mark.parametrize("matching_sha", [True, False])
def test_publication_requires_verified_remote_sha(tmp_path, monkeypatch, name, matching_sha):
    import io
    import json
    import urllib.error

    class Response(io.BytesIO):
        headers = {}

        def __init__(self, body, status=200):
            super().__init__(json.dumps(body).encode())
            self.status = status

    repo = {
        "id": 42,
        "full_name": f"example/{name}",
        "private": True,
        "html_url": f"https://github.com/example/{name}",
    }

    class Opener:
        calls = 0

        def open(self, request, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return Response({"login": "example", "type": "User"})
            if self.calls == 2:
                assert request.full_url == f"https://api.github.com/repos/example/{name}"
                raise urllib.error.HTTPError(request.full_url, 404, "missing", {}, None)
            if self.calls == 3:
                assert request.method == "POST" and json.loads(request.data)["private"] is True
                assert json.loads(request.data)["name"] == name
                return Response(repo, 201)
            if self.calls == 4:
                return Response(repo)
            assert request.full_url == f"https://api.github.com/repos/example/{name}/git/ref/heads/main"
            return Response({"object": {"sha": ("b" if matching_sha else "c") * 40}})

    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(operations, "ROOT", tmp_path)
    monkeypatch.setattr(operations, "SOURCE", tmp_path)
    monkeypatch.setattr(operations, "source_manifest", lambda: {})
    monkeypatch.setattr(operations.urllib.request, "build_opener", lambda *_: Opener())
    monkeypatch.setattr(operations, "event", lambda *args, **kwargs: None)

    def command(data, step, args, *rest):
        if step == "push":
            assert args[-2:] == [f"https://github.com/example/{name}.git", "HEAD:refs/heads/main"]
        return {"exit_code": 0}

    monkeypatch.setattr(operations, "command", command)
    monkeypatch.setattr(operations.subprocess, "check_output", lambda *args, **kwargs: ("b" * 40).encode())
    data = publication_input()
    data["approval"]["destination_name"] = name
    report = operations.publish(data)
    assert report["publication_status"] == ("published" if matching_sha else "partial")
    assert report["status"] == ("passed" if matching_sha else "failed")
    assert report.get("fixed_commit_sha") == ("b" * 40 if matching_sha else None)
    assert report["fixed_repository_url"] == f"https://github.com/example/{name}"
    assert "TEST_DOUBLE_TOKEN" not in (tmp_path / "git-credential-demo.py").read_text()


@pytest.mark.parametrize("name", ["Fixture", "..", "...", "repo.git", "a/b", "a b", "", "x" * 101])
def test_invalid_destination_prevents_network(monkeypatch, name):
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(operations.urllib.request, "build_opener", lambda *_: pytest.fail("no network"))
    data = publication_input()
    data["approval"]["destination_name"] = name
    with pytest.raises(ValueError, match="destination"):
        operations.publish(data)
