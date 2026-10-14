"""Pinned SDK compatibility seam for the documented telemetryConfig request field.

SDK 0.1.0b4 silently drops unknown create kwargs. Preserve its create/poll/read/
delete behavior and augment only the exact create request before serialization.
Remove this seam once the official public method supports telemetry_config.
"""

import json
import re
from copy import deepcopy
from importlib.metadata import version

from azure.containerapps.sandbox import SandboxGroupClient


def validate_config(value):
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict) or set(value) != {"endpoints"} or len(value["endpoints"]) != 1:
        raise ValueError("One explicit Log Analytics endpoint is required")
    endpoint = value["endpoints"][0]
    required = {"kind", "data", "dceEndpoint", "dcrImmutableId", "tableName", "dynamicJsonColumns", "auth"}
    if set(endpoint) != required or endpoint["kind"] != "LogAnalytics":
        raise ValueError("Only managed-identity Log Analytics telemetry is supported")
    if endpoint["data"] != ["ContainerStdoutStderr"] or endpoint["dynamicJsonColumns"] is not True:
        raise ValueError("Structured Sandbox console telemetry required")
    if not re.fullmatch(r"https://[a-z0-9.-]+\.ingest\.monitor\.azure\.com/?", endpoint["dceEndpoint"]):
        raise ValueError("Invalid Azure DCE endpoint")
    if not re.fullmatch(r"dcr-[a-f0-9]{32}", endpoint["dcrImmutableId"]):
        raise ValueError("Invalid DCR immutable ID")
    if endpoint["tableName"] != "Custom-AcademoSandboxLogs_CL":
        raise ValueError("Unexpected telemetry stream")
    auth = endpoint["auth"]
    if set(auth) != {"kind", "identity"} or auth["kind"] != "ManagedIdentity":
        raise ValueError("Telemetry requires ingestion-only group identity")
    if not re.fullmatch(
        r"/subscriptions/[a-f0-9-]{36}/resourceGroups/[A-Za-z0-9_.-]+/providers/Microsoft.ManagedIdentity/userAssignedIdentities/[A-Za-z0-9_-]+",
        auth["identity"],
    ):
        raise ValueError("Invalid telemetry identity ARM ID")
    return deepcopy(value)


class TelemetrySandboxGroupClient(SandboxGroupClient):
    def __init__(self, *args, telemetry_config, **kwargs):
        if version("azure-containerapps-sandbox") != "0.1.0b4":
            raise RuntimeError("Reverify telemetry adapter against the installed SDK")
        self.telemetry_config = validate_config(telemetry_config)
        super().__init__(*args, **kwargs)

    def verify_telemetry(self, sandbox_id):
        # SDK's Sandbox model currently omits telemetryConfig; inspect only this field.
        value = self._dp_get(f"{self._group_path}/sandboxes/{sandbox_id}")
        actual = value.get("telemetryConfig", {}).get("endpoints", [])
        expected = self.telemetry_config["endpoints"][0]
        self.telemetry_readback = {
            "present": "telemetryConfig" in value,
            "endpoint_count": len(actual),
            "mismatched_fields": [key for key, val in expected.items() if not actual or actual[0].get(key) != val],
            "top_level_keys": sorted(value),
        }
        if "telemetryConfig" not in value:
            # Production GET omits the field. Actual Log Analytics ingestion is
            # the acceptance test; never label this read-back as verified.
            return "not_exposed_by_get"
        if len(actual) != 1 or self.telemetry_readback["mismatched_fields"]:
            raise RuntimeError("Sandbox telemetryConfig read-back mismatch")
        return "matched"

    def _dp_put(self, path, body=None, *, headers=None, params=None):
        if path == f"{self._group_path}/sandboxes":
            if not isinstance(body, dict) or "telemetryConfig" in body:
                raise ValueError("Unexpected SDK create payload")
            body = {**body, "telemetryConfig": deepcopy(self.telemetry_config)}
        return super()._dp_put(path, body, headers=headers, params=params)
