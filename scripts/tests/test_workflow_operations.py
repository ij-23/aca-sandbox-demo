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


def test_publication_collision_never_pushes(monkeypatch):
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
    report = operations.publish(publication_input())
    assert report["publication_status"] == "failed" and opener.calls == 2


def test_publication_requires_verified_remote_sha(tmp_path, monkeypatch):
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
        "full_name": "example/fixture-fixed",
        "private": True,
        "html_url": "https://github.com/example/fixture-fixed",
    }

    class Opener:
        calls = 0

        def open(self, request, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return Response({"login": "example", "type": "User"})
            if self.calls == 2:
                raise urllib.error.HTTPError(request.full_url, 404, "missing", {}, None)
            if self.calls == 3:
                assert request.method == "POST" and json.loads(request.data)["private"] is True
                return Response(repo, 201)
            if self.calls == 4:
                return Response(repo)
            return Response({"object": {"sha": "c" * 40}})  # Deliberate remote mismatch.

    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "TEST_DOUBLE_TOKEN")
    monkeypatch.setattr(operations, "ROOT", tmp_path)
    monkeypatch.setattr(operations, "SOURCE", tmp_path)
    monkeypatch.setattr(operations, "source_manifest", lambda: {})
    monkeypatch.setattr(operations.urllib.request, "build_opener", lambda *_: Opener())
    monkeypatch.setattr(operations, "event", lambda *args, **kwargs: None)
    monkeypatch.setattr(operations, "command", lambda *args, **kwargs: {"exit_code": 0})
    monkeypatch.setattr(operations.subprocess, "check_output", lambda *args, **kwargs: ("b" * 40).encode())
    report = operations.publish(publication_input())
    assert report["publication_status"] == "partial" and report["status"] == "failed"
    assert report.get("fixed_commit_sha") is None
    assert "TEST_DOUBLE_TOKEN" not in (tmp_path / "git-credential-demo.py").read_text()
