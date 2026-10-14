"""P0: one owned connection-free Sandbox; fixed booleans only, mandatory deletion.

Uses the existing smoke harness context/ownership/timeout safeguards. No target
repository is fetched or executed. This probe does not certify hostile-code safety.
"""

import json
import time
from uuid import uuid4

import smoke_test_sandbox as smoke
from azure.containerapps.sandbox import EgressPolicy, SandboxGroupClient


def without_telemetry(*args, telemetry_config, **kwargs):
    """P0 comparison only: retain harness safety checks, omit telemetry injection."""
    group = SandboxGroupClient(*args, **kwargs)
    group.probe_identity_id = telemetry_config["endpoints"][0]["auth"]["identity"]
    return group


def checks_pass(probe):
    """Narrow probe gate. Endpoint-variable presence is not token issuance.

    A positive control in an identity-bearing group is required separately.
    This does not certify all network/process/isolation properties.
    """
    return (
        not any(
            value
            for name, value in probe["environment_present"].items()
            if name not in ("IDENTITY_ENDPOINT", "IDENTITY_HEADER")
        )
        and not any(probe["credential_files_present"].values())
        and probe.get("platform_identity_http_status") == {"arm": 401, "storage": 401, "telemetry": 401}
        and probe.get("external_http_status") == 403
        and probe.get("metadata_http_status") is None
        and probe.get("identity_http_status") is None
    )


PROBE = """import json,os,urllib.request,urllib.error,urllib.parse
names=['COPILOT_GITHUB_TOKEN','GH_TOKEN','GITHUB_TOKEN','IDENTITY_ENDPOINT','IDENTITY_HEADER','MSI_ENDPOINT','MSI_SECRET','AZURE_CLIENT_SECRET','AZURE_FEDERATED_TOKEN_FILE']
result={'environment_present':{name:bool(os.environ.get(name)) for name in names}}
# Do not read or print credential values or credential files.
result['credential_files_present']={path:os.path.exists(path) for path in ['/root/.git-credentials','/root/.config/gh/hosts.yml','/root/.azure/accessTokens.json']}
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for name,url,headers in [
 ('metadata','http://169.254.169.254/metadata/instance?api-version=2021-02-01',{'Metadata':'true'}),
 ('identity','http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F',{'Metadata':'true'}),
 ('external','https://example.com/',{})]:
 try:
  with opener.open(urllib.request.Request(url,headers=headers),timeout=4) as response:
   result[name+'_http_status']=response.status
 except urllib.error.HTTPError as error:
  result[name+'_http_status']=error.code
 except Exception:
  result[name+'_http_status']=None
# Probe the actual platform endpoint, not only IMDS. Never read a response body,
# use a returned credential, follow redirects, or print URL/header values.
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): return None
identity_opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
endpoint=os.environ.get('IDENTITY_ENDPOINT')
header=os.environ.get('IDENTITY_HEADER')
result['platform_identity_http_status']={}
if endpoint and header:
 identity_id=json.load(open('/tmp/worker-probe-settings.json'))['identity_resource_id']
 for name,resource,selector in [('arm','https://management.azure.com/',{}),('storage','https://storage.azure.com/',{}),('telemetry','https://monitor.azure.com/',{'mi_res_id':identity_id})]:
  query=urllib.parse.urlencode({'resource':resource,'api-version':'2019-08-01',**selector})
  try:
   request=urllib.request.Request(endpoint+('\\u0026' if '?' in endpoint else '?')+query,headers={'X-IDENTITY-HEADER':header})
   with identity_opener.open(request,timeout=4) as response:
    result['platform_identity_http_status'][name]=response.status
  except urllib.error.HTTPError as error:
   result['platform_identity_http_status'][name]=error.code
  except Exception:
   result['platform_identity_http_status'][name]=None
print(json.dumps(result))
"""


def perform(group, path, scope, connection_id, **kwargs):
    labels = {"owner": smoke.OWNER, "smoke-run": uuid4().hex}
    evidence = {
        "test": "connection-free-worker",
        "group": scope,
        "labels": labels,
        "status": "running",
        "cleanup": "not_required",
    }
    sandbox = None
    requested = returned = False
    before = set()
    try:
        with smoke.deadline(150):
            records = list(group.list_sandboxes())
            before = {r.id for r in records}
            if any((r.labels or {}).get("owner") == smoke.OWNER for r in records):
                raise RuntimeError("Unresolved smoke ownership")
            smoke.save(path, evidence)
            requested = True
            started = time.monotonic()
            sandbox = group.begin_create_sandbox(
                disk="copilot",
                connections=[],
                ports=[],
                cpu="1000m",
                memory="2048Mi",
                labels=labels,
                auto_suspend_seconds=300,
                polling_timeout=80,
                polling_interval=2,
                entrypoint=["/bin/sh", "-c"],
                cmd=["exec sleep infinity"],
                egress_policy=EgressPolicy(default_action="Deny", traffic_inspection="Full", rules=[]),
            ).result(timeout=90)
            returned = True
            evidence.update(sandbox_id=sandbox.sandbox_id, creation_seconds=round(time.monotonic() - started, 3))
            smoke.save(path, evidence)
            model = sandbox.get()
            evidence["connections_empty"] = not model.connections
            evidence["ports_empty"] = not model.ports
            sandbox.write_file(
                "/tmp/worker-probe-settings.json", json.dumps({"identity_resource_id": group.probe_identity_id})
            )
            sandbox.write_file("/tmp/worker-probe.py", PROBE)
            result = sandbox.exec("timeout --kill-after=5s 40s python3 /tmp/worker-probe.py")
            if result.exit_code != 0:
                raise RuntimeError("Worker probe failed; output withheld")
            probe = json.loads(result.stdout)
            evidence["checks"] = probe
            if not evidence["connections_empty"] or not evidence["ports_empty"]:
                raise RuntimeError("Unexpected worker binding")
            if not checks_pass(probe):
                raise RuntimeError("Worker isolation boundary failed")
            evidence["status"] = "passed"
            evidence["limitations"] = [
                "Initial connection/identity/network probe only; delegation, telemetry identity, malicious config and worker process isolation remain gates"
            ]
    except BaseException as error:
        evidence.update(status="failed", error_type=type(error).__name__)
    finally:
        if requested:
            started = time.monotonic()
            try:
                with smoke.deadline(100):
                    smoke.cleanup(group, sandbox, labels, returned, budget=80, protected_ids=before)
                evidence["cleanup"] = "deleted_and_exact_id_404_verified"
            except BaseException as error:
                evidence.update(status="failed", cleanup="unconfirmed", cleanup_error_type=type(error).__name__)
            evidence["cleanup_seconds"] = round(time.monotonic() - started, 3)
        smoke.save(path, evidence)
    return evidence


if __name__ == "__main__":
    raise SystemExit(
        smoke.main(
            performer=perform,
            client_factory=without_telemetry,
            require_connection=False,
            plan_description="Create one connection-free Sandbox; inspect credential presence and HTTP statuses only; delete",
        )
    )
