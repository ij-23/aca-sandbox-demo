"""No Azure calls: assert the serialized SDK request carries required telemetry."""

from copy import deepcopy

import pytest
from app.sandbox_telemetry import TelemetrySandboxGroupClient, validate_config
from azure.containerapps.sandbox import SandboxGroupClient


def config():
    return {
        "endpoints": [
            {
                "kind": "LogAnalytics",
                "data": ["ContainerStdoutStderr"],
                "dceEndpoint": "https://dce-demo.swedencentral-1.ingest.monitor.azure.com",
                "dcrImmutableId": "dcr-" + "a" * 32,
                "tableName": "Custom-AcademoSandboxLogs_CL",
                "dynamicJsonColumns": True,
                "auth": {
                    "kind": "ManagedIdentity",
                    "identity": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-demo/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-telemetry",
                },
            }
        ]
    }


def test_sdk_creation_serializes_telemetry_and_preserves_binding(monkeypatch):
    sent = []

    def capture(self, path, body=None, **kwargs):
        sent.append(deepcopy(body))
        return {"id": "00000000-0000-0000-0000-000000000001", "state": "Running"}

    monkeypatch.setattr(SandboxGroupClient, "_dp_put", capture)
    client = TelemetrySandboxGroupClient(
        "https://management.swedencentral.azuredevcompute.io",
        object(),
        subscription_id="00000000-0000-0000-0000-000000000000",
        resource_group="rg-demo",
        sandbox_group="sbg-demo",
        telemetry_config=config(),
    )
    try:
        client.begin_create_sandbox(disk="copilot", connections=["existing-connection"], ports=[]).result(timeout=1)
        assert len(sent) == 1
        assert sent[0]["telemetryConfig"] == config()
        assert sent[0]["connections"] == ["existing-connection"]
        assert sent[0]["sourcesRef"]["diskImage"]["name"] == "copilot"
    finally:
        client.close()


def test_telemetry_rejects_inline_credentials():
    value = config()
    value["endpoints"][0]["auth"] = {"kind": "Secret", "token": "test-only-placeholder"}
    with pytest.raises(ValueError, match="identity"):
        validate_config(value)


def test_telemetry_does_not_accept_arbitrary_ingestion_host():
    value = config()
    value["endpoints"][0]["dceEndpoint"] = "https://unrelated.example"
    with pytest.raises(ValueError, match="DCE"):
        validate_config(value)
