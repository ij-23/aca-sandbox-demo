import asyncio
from uuid import uuid4

import pytest
from app.config import Settings
from app.contracts import Remediate, RemediationReport
from app.orchestrator import Orchestrator
from app.store import Events
from conftest import MemoryStore
from fastapi import HTTPException


def test_events_persist_before_delivery_and_resume():
    async def scenario():
        store = MemoryStore()
        identifier = str(uuid4())
        bus = Events(store, 100)
        await asyncio.gather(*(bus.emit(identifier, "system", "test.event", index=i) for i in range(10)))
        assert [e["event_id"] for e in await bus.read(identifier)] == list(range(1, 11))
        fresh = Events(store, 100)
        await fresh.emit(identifier, "system", "test.event", token="hidden")
        assert store.logs[identifier][-1]["event_id"] == 11
        assert store.logs[identifier][-1]["payload"]["token"] == "[REDACTED]"

    asyncio.run(scenario())


def test_no_event_is_delivered_after_failed_persistence():
    class Broken(MemoryStore):
        async def append_event(self, *args):
            raise OSError("TEST DOUBLE")

    async def scenario():
        bus = Events(Broken(), 100)
        with pytest.raises(OSError):
            await bus.emit(str(uuid4()), "system", "test.event")
        assert not bus.cache

    asyncio.run(scenario())


def test_concurrent_roles_and_single_run_admission():
    class Executor:
        def __init__(self):
            self.roles = set()
            self.both = asyncio.Event()
            self.cleaned = []

        async def run(self, value, role, emit):
            self.roles.add(role)
            if len(self.roles) == 2:
                self.both.set()
            await asyncio.wait_for(self.both.wait(), timeout=1)
            await emit("step.completed", step_id="test-double", status="passed", kind="deterministic")
            common = dict(commit_sha=value["commit_sha"], status="passed", checks=[], limitations=["UNIT TEST DOUBLE"])
            if role == "security":
                return dict(**common, findings=[])
            return dict(**common, tests_passed=1, tests_failed=0, tests_skipped=0, health="skipped")

        async def cleanup(self, value):
            self.cleaned.append(value["run_id"])

    async def scenario():
        async def resolver(*_):
            return "a" * 40

        store, executor = MemoryStore(), Executor()
        runtime = Orchestrator(
            Settings(allowed_repositories=("https://github.com/a/b",), retain_sandboxes=False),
            store,
            Events(store, 100),
            executor,
            resolver,
        )
        value = await runtime.start("https://github.com/a/b", "test-owner")
        with pytest.raises(HTTPException) as error:
            await runtime.start("https://github.com/a/b", "test-owner")
        assert error.value.status_code == 409
        await runtime.tasks[value["run_id"]]
        result = await store.get_run(value["run_id"])
        assert result["status"] == "completed"
        assert set(result["reports"]) == {"security", "build"}
        assert executor.cleaned == [value["run_id"]]
        steps = [e for e in store.logs[value["run_id"]] if e["type"] == "step.completed"]
        assert len(steps) == 2
        assert all(e["payload"]["kind"] == "deterministic" for e in steps)

    asyncio.run(scenario())


def test_publication_cannot_claim_success_without_validation():
    with pytest.raises(ValueError):
        RemediationReport(
            commit_sha="a" * 40,
            status="passed",
            checks=[],
            publication_status="published",
            fixed_repository_url="https://github.com/a/b-fixed",
            fixed_commit_sha="b" * 40,
            diff="",
            limitations=[],
        )
    with pytest.raises(ValueError):
        Remediate(
            finding_id="f1", approved=False, commit_sha="a" * 40, destination_owner="a", destination_name="b-fixed"
        )


@pytest.mark.parametrize("destination_name", ["b-fixed", "My-custom_fix.2026"])
def test_stale_remediation_approval_cannot_launch_a_second_attempt(destination_name):
    class Executor:
        calls = 0

        async def run(self, value, role, emit):
            assert value.get("finished_at") is None
            assert value["approval"]["destination_name"] == destination_name
            self.calls += 1
            return dict(
                commit_sha=value["commit_sha"],
                status="failed",
                checks=[],
                publication_status="skipped",
                diff="",
                limitations=["UNIT TEST DOUBLE"],
            )

        async def cleanup(self, value):
            pass

    async def scenario():
        store, executor = MemoryStore(), Executor()
        value = dict(
            run_id=str(uuid4()),
            owner_id="owner",
            repository_url="https://github.com/a/b",
            commit_sha="a" * 40,
            status="completed",
            finished_at="2026-10-14T10:00:00+00:00",
            remediation_attempted=False,
            reports={"security": {"findings": [{"id": "f1", "verification_status": "verified"}]}},
        )
        await store.save_run(value)
        runtime = Orchestrator(
            Settings(allowed_repositories=(value["repository_url"],), publication_owner="a"),
            store,
            Events(store, 100),
            executor,
        )
        approval = Remediate(
            finding_id="f1",
            approved=True,
            commit_sha="a" * 40,
            destination_owner="a",
            destination_name=destination_name,
        )
        for changes in ({"destination_owner": "other"}, {"destination_name": "B"}):
            with pytest.raises(HTTPException) as rejected:
                await runtime.remediate(value, approval.model_copy(update=changes))
            assert rejected.value.status_code == 409
        assert executor.calls == 0
        await runtime.remediate(value, approval)
        assert (await store.get_run(value["run_id"]))["approval"]["destination_name"] == destination_name
        with pytest.raises(HTTPException) as failure:
            await runtime.remediate(value, approval)  # Same stale pre-approval snapshot.
        assert failure.value.status_code == 409
        await runtime.tasks[value["run_id"]]
        with pytest.raises(HTTPException):
            await runtime.remediate(value, approval)
        assert executor.calls == 1

    asyncio.run(scenario())


@pytest.mark.parametrize("name", ["", ".", "..", "...", "repo.git", "repo.GIT", "a/b", "a b", "x\n", "x" * 101])
def test_invalid_publication_name_is_rejected(name):
    with pytest.raises(ValueError):
        Remediate(finding_id="f1", approved=True, commit_sha="a" * 40, destination_owner="a", destination_name=name)


def test_wrong_publication_destination_is_rejected_before_persistence():
    class Executor:
        async def run(self, value, role, emit):
            return dict(
                commit_sha=value["commit_sha"],
                status="passed",
                publication_status="published",
                fixed_repository_url="https://github.com/other/repo-fixed",
                fixed_commit_sha="b" * 40,
                diff="",
                limitations=[],
                checks=[
                    dict(name=name, status="passed", exit_code=0, duration_ms=1)
                    for name in ("build", "pytest", "localhost.health", "targeted.recheck", "source.integrity")
                ],
            )

    async def scenario():
        store = MemoryStore()
        runtime = Orchestrator(Settings(), store, Events(store, 100), Executor())
        value = dict(
            run_id=str(uuid4()),
            commit_sha="a" * 40,
            reports={},
            approval={"destination_owner": "a", "destination_name": "b-fixed"},
        )
        with pytest.raises(ValueError, match="approved destination"):
            await runtime._role(value, "remediation")
        assert store.reports == {}

    asyncio.run(scenario())
