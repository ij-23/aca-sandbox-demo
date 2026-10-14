"""Strict API contracts, independent of the cloud transport."""

from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

SHA = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
Role = Literal["security", "build", "remediation", "system"]
Outcome = Literal["pending", "running", "passed", "failed", "skipped", "timed_out"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class StartRun(StrictModel):
    repository_url: str = Field(max_length=250)


class Remediate(StrictModel):
    finding_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    approved: Literal[True]
    commit_sha: SHA
    destination_owner: str = Field(pattern=r"^[a-zA-Z0-9-]{1,39}$")
    destination_name: str = Field(pattern=r"^[a-zA-Z0-9_.-]{1,100}$")


class Event(StrictModel):
    event_id: int = Field(ge=1)
    run_id: str
    timestamp: str
    sandbox_role: Role
    sandbox_id: str | None = None
    type: str = Field(pattern=r"^[a-z][a-z0-9_.]{0,63}$")
    step_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class Finding(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str = Field(max_length=100)
    file: str = Field(max_length=250)
    line: int = Field(ge=1)
    evidence: str = Field(max_length=2000)
    explanation: str = Field(max_length=2000)
    recommendation: str = Field(max_length=2000)
    confidence: Literal["high", "medium", "low"]
    verification_status: Literal["verified", "unverified", "rejected"]


class Check(StrictModel):
    name: str = Field(max_length=100)
    status: Outcome
    exit_code: int | None = None
    duration_ms: int = Field(ge=0)
    detail: str = Field(default="", max_length=4000)


class ReviewReport(StrictModel):
    commit_sha: SHA
    status: Outcome
    findings: list[Finding] = Field(max_length=100)
    checks: list[Check] = Field(max_length=100)
    limitations: list[str] = Field(max_length=30)


class BuildReport(StrictModel):
    commit_sha: SHA
    status: Outcome
    checks: list[Check] = Field(max_length=100)
    tests_passed: int = Field(ge=0)
    tests_failed: int = Field(ge=0)
    tests_skipped: int = Field(ge=0)
    health: Outcome
    limitations: list[str] = Field(max_length=30)


class RemediationReport(StrictModel):
    commit_sha: SHA
    status: Outcome
    checks: list[Check] = Field(max_length=100)
    publication_status: Literal["skipped", "failed", "partial", "published"]
    fixed_repository_url: (
        Annotated[str, StringConstraints(pattern=r"^https://github\.com/[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{1,100}$")]
        | None
    ) = None
    fixed_commit_sha: SHA | None = None
    diff: str = Field(max_length=100000)
    limitations: list[str] = Field(max_length=30)

    @model_validator(mode="after")
    def publication_evidence(self):
        if self.publication_status == "published":
            if self.status != "passed" or not self.fixed_repository_url or not self.fixed_commit_sha:
                raise ValueError("Published result requires passed validation and verified destination/SHA")
            if not self.checks or any(c.status != "passed" for c in self.checks):
                raise ValueError("All required validation checks must pass before publication")
            required = {"build", "pytest", "localhost.health", "targeted.recheck", "source.integrity"}
            if not required.issubset({c.name for c in self.checks}) or any(c.exit_code != 0 for c in self.checks):
                raise ValueError("Published result lacks required successful validation exit codes")
        return self


def now() -> str:
    return datetime.now(UTC).isoformat()


def run_id(value: str) -> str:
    return str(UUID(value))
