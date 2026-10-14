"""Verdict tests using explicit authored probe data; no Azure calls."""

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from probe_worker_isolation import checks_pass


def probe():
    return {
        "environment_present": {
            "IDENTITY_ENDPOINT": True,
            "IDENTITY_HEADER": True,
            "COPILOT_GITHUB_TOKEN": False,
            "GH_TOKEN": False,
            "GITHUB_TOKEN": False,
        },
        "credential_files_present": {"credential-file": False},
        "platform_identity_http_status": {"arm": 401, "storage": 401, "telemetry": 401},
        "external_http_status": 403,
        "metadata_http_status": None,
        "identity_http_status": None,
    }


def test_endpoint_presence_alone_is_not_successful_identity_access():
    assert checks_pass(probe())


def test_success_timeout_or_unexpected_identity_response_cannot_pass():
    original = probe()
    for key in ("arm", "storage", "telemetry"):
        for status in (200, 400, 403, 500, None):
            value = copy.deepcopy(original)
            value["platform_identity_http_status"][key] = status
            assert not checks_pass(value)


def test_any_provider_credential_or_external_access_fails():
    for name in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        value = probe()
        value["environment_present"][name] = True
        assert not checks_pass(value)
    for key in ("external_http_status", "metadata_http_status", "identity_http_status"):
        value = probe()
        value[key] = 200
        assert not checks_pass(value)
    value = probe()
    value["credential_files_present"]["credential-file"] = True
    assert not checks_pass(value)
