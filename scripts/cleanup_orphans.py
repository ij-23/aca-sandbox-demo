#!/usr/bin/env python3
"""Inspect/reconcile one smoke ownership record. Inert by default; deletion needs exact reviewed IDs.

This tool handles smoke evidence only. It does not infer application ownership,
delete groups, or delete a sandbox merely because it is old or stopped.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

from smoke_test_sandbox import OWNER, SDK_VERSION, SmokeDeadline, deadline

SCOPE = re.compile(
    r"^/subscriptions/([0-9a-f-]{36})/resourceGroups/([A-Za-z0-9_-]{1,90})"
    r"/providers/Microsoft.App/sandboxGroups/([A-Za-z0-9_-]{1,90})$"
)


def ownership(evidence):
    scope = SCOPE.fullmatch(evidence["group"])
    if not scope or evidence.get("create_requests") != 1:
        raise ValueError("Expected one attempted creation and an exact group scope")
    UUID(scope[1])
    nonce = evidence["run_id"]
    if not re.fullmatch(r"[0-9a-f]{32}", nonce):
        raise ValueError("Invalid smoke nonce")
    labels = {"owner": OWNER, "smoke-run": nonce}
    if evidence["labels"] != labels or not isinstance(evidence.get("before"), list):
        raise ValueError("Missing exact smoke labels or pre-existing inventory")
    protected = {item["id"] for item in evidence["before"]}
    if evidence.get("sandbox_id") in protected:
        raise ValueError("Evidence points to a pre-existing sandbox")
    return scope, labels, protected


def candidates(group, evidence):
    _, labels, protected = ownership(evidence)
    return [
        item.id
        for item in group.list_sandboxes()
        if item.id not in protected and all((item.labels or {}).get(k) == v for k, v in labels.items())
    ]


def delete_exact(group, evidence, identifiers):
    _, labels, protected = ownership(evidence)
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError("Specify distinct reviewed sandbox IDs")
    for identifier in identifiers:
        if identifier in protected:
            raise ValueError("Refuse deleting a pre-existing sandbox")
    verified = []
    for identifier in identifiers:
        client = group.get_sandbox_client(identifier)
        try:
            value = client.get()
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                verified.append(identifier)
                continue
            raise
        if not all((value.labels or {}).get(k) == v for k, v in labels.items()):
            raise ValueError("Live ownership does not match the reviewed evidence")
        client.delete()
        end = time.monotonic() + 60
        while time.monotonic() < end:
            try:
                client.get()
            except Exception as exc:
                if getattr(exc, "status_code", None) == 404:
                    verified.append(identifier)
                    break
                raise
            time.sleep(2)
        else:
            raise TimeoutError("Exact sandbox deletion is unconfirmed")
    return verified


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--region")
    parser.add_argument("--tenant-id")
    parser.add_argument("--inspect", action="store_true", help="Read-only Azure inventory")
    parser.add_argument("--delete-id", action="append", default=[], help="Exact ID; only after explicit approval")
    parser.add_argument("--confirm-group", help="Exact reviewed ARM scope required for deletion")
    args = parser.parse_args(argv)
    evidence = json.loads(args.evidence.read_text())
    scope, _, _ = ownership(evidence)
    if not args.inspect and not args.delete_id:
        print(json.dumps({"mode": "plan_only", "group": evidence["group"], "azure_calls": 0}))
        return
    if not args.tenant_id or not args.region or not re.fullmatch(r"[a-z0-9]+", args.region):
        raise ValueError("Explicit tenant and valid region are required")
    UUID(args.tenant_id)
    if args.delete_id and args.confirm_group != evidence["group"]:
        raise ValueError("Deletion requires the exact approved group scope")
    for identifier in args.delete_id:
        UUID(identifier)
    account = json.loads(subprocess.check_output(["az", "account", "show", "-o", "json"], timeout=20))
    if account["id"] != scope[1] or account["tenantId"] != args.tenant_id:
        raise ValueError("Select the approved cached Azure CLI context first")
    if version("azure-containerapps-sandbox") != SDK_VERSION:
        raise RuntimeError("Unexpected SDK version")
    from azure.containerapps.sandbox import SandboxGroupClient, endpoint_for_region
    from azure.core.pipeline.transport import RequestsTransport
    from azure.identity import AzureCliCredential

    with AzureCliCredential(tenant_id=args.tenant_id, process_timeout=15) as credential:
        with SandboxGroupClient(
            endpoint_for_region(args.region),
            credential,
            subscription_id=scope[1],
            resource_group=scope[2],
            sandbox_group=scope[3],
            transport=RequestsTransport(connection_timeout=10, read_timeout=20),
            retry_total=0,
        ) as group:
            with deadline(100):
                if args.delete_id:
                    removed = delete_exact(group, evidence, args.delete_id)
                    print(json.dumps({"exact_id_404_verified": removed}))
                else:
                    print(json.dumps({"mode": "read_only", "owned_candidates": candidates(group, evidence)}))


if __name__ == "__main__":
    try:
        main()
    except (Exception, SmokeDeadline, KeyboardInterrupt) as exc:
        print(json.dumps({"status": "unconfirmed", "error_type": type(exc).__name__}), file=sys.stderr)
        sys.exit(1)
