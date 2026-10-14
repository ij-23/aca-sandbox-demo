#!/usr/bin/env python3
"""Verify only the app image locally with no network, Azure identity or fixture code."""

import argparse
import json
import subprocess
import time
from uuid import uuid4

PROBE = """
import json, os, re, urllib.error, urllib.request
def get(path, data=None):
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000'+path, data=data, timeout=3)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, response.read()
assert os.getuid() == 10001
assert get('/api/healthz')[0] == 200
assert get('/api/readyz')[0] == 503
status, html = get('/')
assert status == 200
assets = re.findall(rb'(?:src|href)="(/assets/[^\"]+)"', html)
assert len(assets) >= 2
assert all(get(asset.decode())[0] == 200 for asset in assets)
assert json.loads(get('/api/config')[1])['live_execution_enabled'] is False
assert get('/api/runs')[0] == 401
assert get('/api/runs', b'{}')[0] == 401
assert get('/api/runs/not-a-run/cleanup', b'{}')[0] == 401
assert get('/api/runs/not-a-run/remediate', b'{}')[0] == 401
print(json.dumps({'nonroot_uid':10001,'health':200,'unconfigured_readiness':503,
                  'dashboard':200,'assets':len(assets),'anonymous_operations':401,
                  'live_execution_enabled':False}))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="aca-sandbox-demo:local")
    args = parser.parse_args()
    name = "aca-platform-check-" + uuid4().hex[:12]
    created = False
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "--detach",
                "--rm",
                "--platform",
                "linux/amd64",
                "--network",
                "none",
                "--read-only",
                "--tmpfs",
                "/tmp",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--name",
                name,
                args.image,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        created = True
        end = time.monotonic() + 20
        while time.monotonic() < end:
            result = subprocess.run(
                ["docker", "exec", name, "python", "-c", PROBE], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(result.stdout.strip())
                break
            time.sleep(1)
        else:
            raise RuntimeError("Application container verification failed")
    finally:
        if created:
            subprocess.run(["docker", "stop", "--time", "10", name], check=True, capture_output=True, timeout=20)
            inspected = subprocess.run(["docker", "inspect", name], capture_output=True, timeout=10)
            if inspected.returncode == 0:
                raise RuntimeError("Owned local verification container remains")
            print(json.dumps({"verification_container_removed": True}))


if __name__ == "__main__":
    main()
