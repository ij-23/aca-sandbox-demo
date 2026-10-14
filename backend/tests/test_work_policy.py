"""Policy-only tests. No GitHub calls, fake successful runs or repository execution."""

import pytest
from app.work_policy import ValidationReceipt, WorkRequest, authorize_work, publication_gate
from pydantic import ValidationError

SHA, DIGEST, ATTEMPT = "a" * 40, "b" * 64, "c" * 32


def request(**changes):
    return WorkRequest.model_validate(dict(nonce=ATTEMPT, sequence=1, operation="inventory", commit_sha=SHA, **changes))


def authorize(value, **changes):
    policy = dict(
        nonce=ATTEMPT,
        sequence=1,
        sha=SHA,
        operations=frozenset({"inventory"}),
        components=frozenset({"."}),
        artifact_digest=None,
    )
    authorize_work(value, **{**policy, **changes})


def receipt():
    return ValidationReceipt.model_validate(
        dict(
            attempt=ATTEMPT,
            source_sha=SHA,
            artifact_digest=DIGEST,
            adapter="python-pytest-v1",
            checks=[
                dict(name=name, status="passed", exit_code=0)
                for name in (
                    "build",
                    "tests",
                    "targeted_recheck",
                    "source_integrity",
                    "license",
                    "artifact_sanitization",
                )
            ],
        )
    )


def gate(value, **changes):
    return publication_gate(
        value, **{**dict(expected_sha=SHA, expected_digest=DIGEST, expected_attempt=ATTEMPT), **changes}
    )


def test_envelope_has_no_shell_or_publisher_authority():
    for changes in (
        {"command": "anything"},
        {"destination_owner": "attacker"},
        {"event_id": 1},
        {"sandbox_id": "other"},
    ):
        with pytest.raises(ValidationError):
            request(**changes)
    authorize(request())


@pytest.mark.parametrize(
    "changes",
    [
        {"nonce": "d" * 32},
        {"sequence": 2},
        {"sha": "d" * 40},
        {"operations": frozenset()},
        {"components": frozenset({"other"})},
        {"artifact_digest": DIGEST},
    ],
)
def test_host_policy_rejects_mismatch_and_replay(changes):
    with pytest.raises(ValueError):
        authorize(request(), **changes)


@pytest.mark.parametrize("component", ["/tmp", "../a", "a/../b", "a\\b", "a\nb", "a//b", ".git/config"])
def test_unsafe_component_rejected(component):
    with pytest.raises(ValidationError):
        request(component=component)


def test_every_check_required_on_exact_artifact():
    valid = receipt()
    assert len(gate(valid)) == 64
    for changes in ({"expected_sha": "d" * 40}, {"expected_digest": "d" * 64}, {"expected_attempt": "d" * 32}):
        with pytest.raises(ValueError):
            gate(valid, **changes)
    for status in ("failed", "skipped", "timed_out", "blocked"):
        for check in valid.checks:
            changed = receipt()
            changed.checks[valid.checks.index(check)].status = status
            with pytest.raises(ValueError):
                gate(changed)
    changed = receipt()
    changed.checks[0].exit_code = None
    with pytest.raises(ValueError):
        gate(changed)


def test_duplicate_pass_cannot_replace_missing_required_check():
    value = receipt()
    value.checks[1] = value.checks[0]
    with pytest.raises(ValueError):
        gate(value)
