"""Host-owned delegation contracts. Untrusted output cannot choose authority.

These contracts are preparation for the isolated executor, not a public run
implementation. No subprocess or network call belongs in this module.
"""

import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator

from .contracts import SHA, StrictModel

Digest = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
Nonce = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{32}$")]


class WorkRequest(StrictModel):
    schema_version: Literal[1] = 1
    nonce: Nonce
    sequence: int = Field(ge=1, le=100)
    operation: Literal["inventory", "static_review", "validate_python", "validate_node", "apply_patch"]
    commit_sha: SHA
    component: str = Field(default=".", max_length=250)
    artifact_digest: Digest | None = None

    @field_validator("component")
    @classmethod
    def component_path(cls, value):
        if value == ".":
            return value
        if any(part.casefold() in ("", ".", "..", ".git") for part in value.split("/")) or any(
            char in "\\:" or ord(char) < 32 or ord(char) == 127 for char in value
        ):
            raise ValueError("Invalid component path")
        return value


def authorize_work(
    request: WorkRequest,
    *,
    nonce: str,
    sequence: int,
    sha: str,
    operations: frozenset[str],
    components: frozenset[str],
    artifact_digest: str | None,
):
    """All policy arguments originate from the host's persisted run, never the worker."""
    if (
        request.nonce != nonce
        or request.sequence != sequence
        or request.commit_sha != sha
        or request.operation not in operations
        or request.component not in components
        or request.artifact_digest != artifact_digest
    ):
        raise ValueError("Delegated request differs from host policy")


class RequiredCheck(StrictModel):
    name: Literal["build", "tests", "targeted_recheck", "source_integrity", "license", "artifact_sanitization"]
    status: Literal["passed", "failed", "skipped", "timed_out", "blocked"]
    exit_code: int | None


class ValidationReceipt(StrictModel):
    """Only the host may issue/store a receipt after independent verification.

    Model validation alone is never authentication. Publisher must compare this
    exact receipt to its protected host-side record, not trust a posted receipt.
    """

    schema_version: Literal[1] = 1
    attempt: Nonce
    source_sha: SHA
    artifact_digest: Digest
    policy_version: Literal["public-publication-v1"] = "public-publication-v1"
    adapter: Literal["python-pytest-v1", "node-npm-v1"]
    checks: list[RequiredCheck] = Field(min_length=6, max_length=6)


def publication_gate(receipt: ValidationReceipt, *, expected_sha: str, expected_digest: str, expected_attempt: str):
    required = {"build", "tests", "targeted_recheck", "source_integrity", "license", "artifact_sanitization"}
    if (
        receipt.source_sha != expected_sha
        or receipt.artifact_digest != expected_digest
        or receipt.attempt != expected_attempt
        or {c.name for c in receipt.checks} != required
        or any(check.status != "passed" or check.exit_code != 0 for check in receipt.checks)
    ):
        raise ValueError("Publication requires every independent check on the exact approved artifact")
    # A digest is an identifier, not an authorization credential/signature.
    return hashlib.sha256(json.dumps(receipt.model_dump(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
