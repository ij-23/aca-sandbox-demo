"""Detached workflow launcher; runs only inside the disposable Sandbox."""

import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

from cli_setup import sanitize


def status(value):
    Path("status.tmp").write_text(json.dumps(value))
    Path("status.tmp").replace("status.json")


inputs = json.loads(Path("input.json").read_text())
names = {"security": "security-review", "build": "build-validation", "remediation": "remediation"}
command = [
    "timeout",
    "--kill-after=5s",
    "720s",
    str(Path("cli/copilot").resolve()),
    "--experimental",
    "--no-auto-update",
    "--no-custom-instructions",
    "--disable-builtin-mcps",
    "--available-tools=view",
    "--deny-tool=view",
    "workflow",
    "run",
    names[inputs["role"]],
    "--args",
    "@input.json",
    "--result-file",
    "result.json",
    "--output-format",
    "json",
]
if inputs["role"] == "remediation" and inputs["publication_enabled"]:
    # The official SDK grants only this trusted extension's named credential
    # request; no blanket CLI tool approval or manual token injection.
    command = ["timeout", "--kill-after=5s", "720s", "node", "host.mjs"]
started = time.monotonic()
status({"state": "running"})
code = 1
try:
    env = dict(
        os.environ,
        GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS="true",
        COPILOT_AUTO_UPDATE="false",
        ACA_PUBLICATION_ENABLED="true" if inputs["publication_enabled"] else "false",
    )
    with Path("cli.raw.log").open("wb") as log:
        child = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=env, start_new_session=True
        )
        try:
            code = child.wait(timeout=730)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
            code = 124
finally:
    with Path("cli.raw.log").open("rb") as log:
        log.seek(0, 2)
        log.seek(max(0, log.tell() - 60000))
        raw = log.read().decode(errors="replace")
    # Only process diagnostic logs explicitly named by this invocation; sanitize
    # inside the Sandbox before retrieval, never read credential/config files.
    diagnostics = []
    for name in sorted(set(re.findall(r"/root/\.copilot/logs/process-[0-9-]+\.log", raw)))[:4]:
        try:
            with Path(name).open("rb") as log:
                log.seek(0, 2)
                log.seek(max(0, log.tell() - 12000))
                diagnostics.append(log.read().decode(errors="replace"))
        except OSError:
            diagnostics.append("Extension diagnostic unavailable")
    Path("cli.sanitized.log").write_text(sanitize(raw + "\n" + "\n".join(diagnostics)))
    status({"state": "finished", "exit_code": code, "seconds": round(time.monotonic() - started, 3)})
