"""Project-authored inert archive tests; never download or execute repository code."""

import importlib.util
import io
import tarfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "public_source", Path(__file__).parents[2] / "workflows/shared/public_source.py"
)
source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source)


def archive(tmp_path, entries):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        for name, text, kind in entries:
            item = tarfile.TarInfo(name)
            item.type = kind
            item.size = len(text) if kind == tarfile.REGTYPE else 0
            item.linkname = "../../outside" if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE) else ""
            tar.addfile(item, io.BytesIO(text) if kind == tarfile.REGTYPE else None)
    return path


def unpack(tmp_path, entries):
    return source.unpack(archive(tmp_path, entries), tmp_path / "tree", "project-sha")


def test_python_node_unknown_and_license_are_detected_without_execution(tmp_path):
    contents = {
        "pyproject.toml": b'[project]\nrequires-python=">=3.11"',
        "ui/package.json": b'{"scripts":{"test":"node test.js"},"engines":{"node":">=20"}}',
        "ui/package-lock.json": b"{}",
        "LICENSE": b"Test license text",
        "test.py": b'raise RuntimeError("MUST NEVER EXECUTE")',
        "main.rs": b"// inert source",
    }
    inventory = unpack(tmp_path, [(f"project-sha/{name}", text, tarfile.REGTYPE) for name, text in contents.items()])
    result = source.discover(tmp_path / "tree", inventory)
    assert len(result["components"]) == 2
    assert {c["adapter_candidate"] for c in result["components"]} == {"python-pytest-v1", "node-npm-v1"}
    assert all(c["execution_status"] == "blocked" for c in result["components"])
    assert result["license_files"] == ["LICENSE"]
    assert result["redistribution_status"] == "requires_review"
    assert "test.py" in result["review_files"]


@pytest.mark.parametrize(
    "path",
    [
        "../escape",
        "/absolute",
        "project-sha/../escape",
        "project-sha/.git/config",
        "project-sha/.GIT/config",
        "project-sha/a\\b",
        "project-sha/a:b",
        "other-root/file",
        "project-sha/a\nforged-event",
    ],
)
def test_unsafe_archive_paths_are_rejected(tmp_path, path):
    with pytest.raises(source.SourceRejected):
        unpack(tmp_path, [(path, b"inert", tarfile.REGTYPE)])


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE])
def test_links_and_special_files_rejected(tmp_path, kind):
    with pytest.raises(source.SourceRejected):
        unpack(tmp_path, [("project-sha/file", b"", kind)])


def test_duplicate_and_case_collision_rejected(tmp_path):
    with pytest.raises(source.SourceRejected):
        unpack(tmp_path, [("project-sha/A", b"one", tarfile.REGTYPE), ("project-sha/a", b"two", tarfile.REGTYPE)])


def test_existing_destination_not_overwritten(tmp_path):
    (tmp_path / "tree").mkdir()
    with pytest.raises(FileExistsError):
        unpack(tmp_path, [])


def test_internal_symlink_is_omitted_and_never_materialized(tmp_path):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        item = tarfile.TarInfo("project-sha/docs/license")
        item.type = tarfile.SYMTYPE
        item.linkname = "../LICENSE"
        tar.addfile(item)
    inventory = source.unpack(path, tmp_path / "tree", "project-sha")
    assert not (tmp_path / "tree/docs/license").exists()
    assert inventory["omissions"] == [{"path": "docs/license", "reason": "internal_symlink_not_materialized"}]


def test_expansion_bomb_is_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(source, "MAX_EXPANDED", 20000)
    with pytest.raises(source.SourceRejected, match="limit"):
        unpack(tmp_path, [("project-sha/a", b"a" * 30000, tarfile.REGTYPE)])


def test_oversized_text_binary_and_review_omissions_are_explicit(tmp_path, monkeypatch):
    monkeypatch.setattr(source, "MAX_TEXT", 20)
    monkeypatch.setattr(source, "MAX_REVIEW", 4)
    inventory = unpack(
        tmp_path,
        [
            ("project-sha/big", b"x" * 21, tarfile.REGTYPE),
            ("project-sha/binary", b"\0", tarfile.REGTYPE),
            ("project-sha/source", b"abcdx", tarfile.REGTYPE),
        ],
    )
    result = source.discover(tmp_path / "tree", inventory)
    assert {o["reason"] for o in result["omissions"]} == {"text_file_limit", "binary_or_non_utf8", "review_budget"}
    assert not result["review_files"]


def test_manifest_cannot_claim_verified_adapter(tmp_path):
    inventory = unpack(tmp_path, [("project-sha/package.json", b'{"engines": "bad"}', tarfile.REGTYPE)])
    result = source.discover(tmp_path / "tree", inventory)
    assert result["components"][0]["execution_status"] == "blocked"
    assert "invalid or unsupported manifest" in result["components"][0]["reasons"]


def test_tampered_source_rejected(tmp_path):
    inventory = unpack(tmp_path, [("project-sha/code", b"abcd", tarfile.REGTYPE)])
    (tmp_path / "tree/code").write_text("efgh")
    with pytest.raises(source.SourceRejected, match="digest"):
        source.discover(tmp_path / "tree", inventory)
