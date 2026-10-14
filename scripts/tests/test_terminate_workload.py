"""Synthetic /proc tests; never execute fixture code or send process signals."""

import importlib.util
from pathlib import Path


def test_workload_selection_includes_descendants_but_not_unrelated_or_zombies(tmp_path):
    path = Path(__file__).resolve().parents[2] / "workflows/shared/terminate_workload.py"
    spec = importlib.util.spec_from_file_location("terminate_workload", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root, outside, proc = tmp_path / "control", tmp_path / "outside", tmp_path / "proc"
    for folder in (root, outside, proc, root / "source"):
        folder.mkdir()
    for pid, parent, state, cwd in (
        (910001, 1, "S", root),
        (910002, 910001, "S", outside),
        (910003, 1, "S", root / "source"),
        (910004, 1, "S", outside),
        (910005, 910001, "Z", root),
    ):
        folder = proc / str(pid)
        folder.mkdir()
        (folder / "stat").write_text(f"{pid} (test process) {state} {parent} 0 0")
        (folder / "cwd").symlink_to(cwd)
    assert module.workload_pids(root, proc) == {910001, 910002, 910003}
