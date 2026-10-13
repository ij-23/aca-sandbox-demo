#!/usr/bin/env python3
"""Read-only local/optional Azure preflight; never registers providers or grants roles."""
import argparse
import inspect
import json
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from uuid import UUID


def az_json(*arguments):
    result = subprocess.run(["az", *arguments, "--only-show-errors", "-o", "json"],
                            capture_output=True, text=True, timeout=60, check=False)
    if result.returncode:
        # Avoid recording CLI errors that might contain authentication details.
        raise RuntimeError(f"Azure CLI read failed (exit {result.returncode})")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azure", action="store_true", help="Read target subscription provider metadata and role definitions")
    parser.add_argument("--subscription-id")
    parser.add_argument("--tenant-id")
    parser.add_argument("--region")
    args = parser.parse_args()
    checks = {"python_supported": sys.version_info >= (3, 13),
              "terraform_installed": shutil.which("terraform") is not None,
              "azure_cli_installed": shutil.which("az") is not None}
    details = {}
    try:
        details["sandbox_sdk_version"] = version("azure-containerapps-sandbox")
        checks["sandbox_sdk_pinned"] = details["sandbox_sdk_version"] == "0.1.0b4"
        from azure.containerapps.sandbox import SandboxGroupClient, endpoint_for_region
        methods = ["begin_create_sandbox", "list_sandboxes", "list_public_disk_images", "get_sandbox_client"]
        checks["documented_sdk_methods"] = all(callable(getattr(SandboxGroupClient, name, None)) for name in methods)
        details["sdk_signatures"] = {name: str(inspect.signature(getattr(SandboxGroupClient, name)))
                                     for name in methods if hasattr(SandboxGroupClient, name)}
        checks["endpoint_helper"] = callable(endpoint_for_region)
    except (PackageNotFoundError, ImportError):
        checks["sandbox_sdk_pinned"] = False
    if args.azure:
        if not all((args.subscription_id, args.tenant_id, args.region)):
            parser.error("--azure requires explicit --subscription-id, --tenant-id and --region")
        UUID(args.subscription_id)
        UUID(args.tenant_id)
        account = az_json("account", "show", "--subscription", args.subscription_id)
        checks["target_tenant_matches"] = account["tenantId"].lower() == args.tenant_id.lower()
        checks["subscription_enabled"] = account["state"] == "Enabled"
        if not checks["target_tenant_matches"]:
            raise RuntimeError("Target tenant mismatch; no further Azure reads performed")
        contracts = {
            "Microsoft.App": {"sandboxGroups": "2026-07-01", "managedEnvironments": "2025-07-01"},
            "Microsoft.Storage": {"storageAccounts": "2025-06-01"},
            "Microsoft.OperationalInsights": {"workspaces": "2025-07-01"},
            "Microsoft.ContainerRegistry": {"registries": "2025-11-01"},
            "Microsoft.ManagedIdentity": {"userAssignedIdentities": "2024-11-30"},
            "Microsoft.Insights": {"components": "2020-02-02"},
        }
        for namespace, types in contracts.items():
            provider = az_json("provider", "show", "--namespace", namespace, "--subscription", args.subscription_id)
            checks[f"{namespace}:registered"] = provider["registrationState"] == "Registered"
            for name, api in types.items():
                metadata = next((t for t in provider["resourceTypes"] if t["resourceType"].lower() == name.lower()), {})
                if api:
                    checks[f"{namespace}/{name}:api"] = api in metadata.get("apiVersions", [])
                locations = {s.replace(" ", "").lower() for s in metadata.get("locations", [])}
                checks[f"{namespace}/{name}:region"] = args.region.lower() in locations
        scope = f"/subscriptions/{args.subscription_id}"
        for role in ["AcrPull", "Container Apps SandboxGroup Data Owner", "Storage Blob Data Contributor", "Monitoring Metrics Publisher"]:
            found = az_json("role", "definition", "list", "--name", role, "--scope", scope,
                            "--subscription", args.subscription_id)
            checks[f"role:{role}"] = any(item["roleName"] == role for item in found)
        details["unverified"] = ["effective deployer/RBAC permissions", "subscription quota/capacity",
                                 "Copilot entitlement", "actual provider calls and live smoke"]
    print(json.dumps({"status": "passed" if all(checks.values()) else "blocked", "checks": checks, "details": details}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "blocked", "error_type": type(exc).__name__}), file=sys.stderr)
        sys.exit(2)
