"""Sandbox-only fixture tests. Excluded from platform pytest and CI discovery."""

from fastapi.testclient import TestClient

import app as fixture


def test_health():
    with TestClient(fixture.app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}


def test_document_and_missing_document(tmp_path, monkeypatch):
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "hello.txt").write_text("Hello from a trusted fixture.\n")
    monkeypatch.setattr(fixture, "DOCUMENT_ROOT", documents)
    with TestClient(fixture.app) as client:
        assert client.get("/document", params={"name": "hello.txt"}).json() == {
            "content": "Hello from a trusted fixture.\n"
        }
        assert client.get("/document", params={"name": "missing.txt"}).status_code == 404


def test_path_traversal_is_rejected(tmp_path, monkeypatch):
    documents = tmp_path / "documents"
    documents.mkdir()
    (tmp_path / "outside.txt").write_text("Harmless traversal canary; not a secret.\n")
    monkeypatch.setattr(fixture, "DOCUMENT_ROOT", documents)
    with TestClient(fixture.app) as client:
        # Deliberately fails until Sandbox C implements a real containment check.
        assert client.get("/document", params={"name": "../outside.txt"}).status_code == 403


def test_absolute_outside_path_is_rejected(tmp_path, monkeypatch):
    documents = tmp_path / "documents"
    documents.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("Another harmless traversal canary.\n")
    monkeypatch.setattr(fixture, "DOCUMENT_ROOT", documents)
    with TestClient(fixture.app) as client:
        assert client.get("/document", params={"name": str(outside)}).status_code == 403
