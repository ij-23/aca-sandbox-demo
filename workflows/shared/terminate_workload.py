"""Stop trusted-fixture workflow processes before retaining their Sandbox.

Runs only in an ownership-verified Sandbox. Does not read process environments,
credentials or source files. The entrypoint/SDK server outside the run is retained.
"""

import os
import re
import signal
import sys
import time
from pathlib import Path


def workload_pids(root, proc=Path("/proc")):
    processes, selected = {}, set()
    for path in proc.iterdir():
        if not path.name.isdigit():
            continue
        pid = int(path.name)
        if pid <= 1 or pid == os.getpid():
            continue
        try:
            stat = (path / "stat").read_text().rsplit(")", 1)[1].split()
            if stat[0] == "Z":
                continue
            processes[pid] = int(stat[1])
            cwd = (path / "cwd").resolve(strict=True)
            if cwd == root or root in cwd.parents:
                selected.add(pid)
        except (OSError, ValueError, IndexError):
            continue
    while True:
        children = {pid for pid, parent in processes.items() if parent in selected}
        if children <= selected:
            return selected
        selected |= children


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"/tmp/academo-[a-f0-9]{32}", sys.argv[1]):
        raise ValueError("Exact run control directory required")
    root = Path(sys.argv[1])
    os.chdir("/")
    for _ in range(20):
        pids = workload_pids(root)
        if not pids:
            return
        # Freeze parents before killing so they cannot spawn replacement children.
        for action in (signal.SIGSTOP, signal.SIGKILL):
            for pid in pids:
                try:
                    os.kill(pid, action)
                except ProcessLookupError:
                    pass
        time.sleep(0.1)
    raise TimeoutError("Workflow processes remain; stop requires operator attention")


if __name__ == "__main__":
    main()
