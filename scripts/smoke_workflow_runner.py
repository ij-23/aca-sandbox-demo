#!/usr/bin/env python3
"""Trusted helper uploaded to the disposable sandbox; never run Copilot locally."""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tarfile
import time
from pathlib import Path

CLI_URL = 'https://github.com/github/copilot-cli/releases/download/v1.0.97/copilot-linux-x64.tar.gz'
CLI_SHA256 = '07f3f63cb361e911268e8a4b010e06eeced8d4f2d898d13a8180273e34aeff3f'


def cli():
    local = Path('cli/copilot').resolve()
    return str(local) if local.is_file() else 'copilot'


def prepare_cli():
    """Opt-in, disposable-local installation; never change the built-in executable."""
    if os.uname().machine != 'x86_64':
        raise RuntimeError('Pinned artifact requires Linux x64')
    target = Path('cli')
    target.mkdir(exist_ok=False)
    archive = target / 'release.tar.gz'
    subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                    '--proto', '=https', '--connect-timeout', '10', '--max-time', '60',
                    '--max-filesize', '250000000', CLI_URL, '-o', str(archive)],
                   check=True, capture_output=True, timeout=65)
    if hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest() != CLI_SHA256:
        raise RuntimeError('Official artifact checksum mismatch')
    with tarfile.open(archive) as tar:
        tar.extractall(target, filter='data')
    if not (target / 'copilot').is_file():
        raise RuntimeError('Official archive layout differs from reviewed layout')
    (target / 'copilot').chmod(0o700)
    print(json.dumps({'version': '1.0.97', 'source': CLI_URL, 'sha256': CLI_SHA256,
                      'scope': 'disposable_control_directory'}))


def sanitize(text):
    # Redact inside the sandbox before any CLI log crosses the SDK boundary.
    for name, value in os.environ.items():
        if value and re.search(r'token|secret|password|api.?key', name, re.I):
            text = text.replace(value, '[REDACTED]')
    text = re.sub(r'github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+', '[REDACTED]', text)
    text = re.sub(r'(?i)Bearer\s+\S+', 'Bearer [REDACTED]', text)
    text = re.sub(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '[REDACTED]', text)
    return text


def write_status(value):
    p = Path('status.tmp')
    p.write_text(json.dumps(value))
    p.replace('status.json')


def capabilities():
    output = {'environment': {k: bool(os.environ.get(k)) for k in
              ('COPILOT_GITHUB_TOKEN', 'GH_TOKEN', 'GITHUB_TOKEN')}}
    commands = {
        'version': [cli(), '--no-auto-update', '--version'],
        'help': [cli(), '--no-auto-update', '--experimental', '--help'],
        'workflow_help': [cli(), '--no-auto-update', '--experimental', 'workflow', 'run', '--help'],
    }
    for name, command in commands.items():
        p = subprocess.run(command, capture_output=True, text=True, timeout=20,
                           env=dict(os.environ, COPILOT_AUTO_UPDATE='false'))
        output[name] = {'command': command, 'exit_code': p.returncode,
                        'stdout': sanitize(p.stdout)[:20000], 'stderr': sanitize(p.stderr)[:4000]}
    print(json.dumps(output))


def workflow():
    command = ['timeout', '--kill-after=5s', '210s', cli(), '--experimental',
               '--no-auto-update', '--no-custom-instructions', '--disable-builtin-mcps',
               '--available-tools=read', '--deny-tool=read',
               'workflow', 'run', 'aca-viability-smoke', '--args', '@input.json',
               '--result-file', 'result.json', '--output-format', 'json']
    started = time.monotonic()
    state = {'state': 'running', 'command': command, 'started_at': time.time()}
    write_status(state)
    child = None
    try:
        # This opt-in loads only the trusted extension in the fresh control repo.
        env = dict(os.environ, GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS='true', COPILOT_AUTO_UPDATE='false')
        with Path('command.log').open('wb') as log:
            child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, env=env, start_new_session=True)
            try:
                code = child.wait(timeout=220)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)
                code = 124
        state['exit_code'] = code
    except BaseException as exc:
        if child and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
        state['error_type'] = type(exc).__name__
    finally:
        try:
            with Path('command.log').open('rb') as log:
                # Bound retained output. Never export raw command.log.
                log.seek(0, 2)
                log.seek(max(0, log.tell() - 60000))
                raw = log.read().decode('utf-8', errors='replace')
            Path('command.sanitized.log').write_text(sanitize(raw))
        except OSError:
            Path('command.sanitized.log').write_text('CLI log unavailable')
        state.update(state='finished', finished_at=time.time(), seconds=round(time.monotonic()-started, 3))
        write_status(state)


if __name__ == '__main__':
    if sys.argv[1:] == ['prepare-cli']:
        prepare_cli()
    elif sys.argv[1:] == ['capabilities']:
        capabilities()
    elif sys.argv[1:] == ['workflow']:
        workflow()
    else:
        raise SystemExit('Expected capabilities or workflow')
