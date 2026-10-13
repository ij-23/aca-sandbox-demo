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
            await emit("step.completed", step_id="test-double", status="passed")
            common = dict(commit_sha=value["commit_sha"], status="passed", checks=[], limitations=["UNIT TEST DOUBLE"])
            if role == "security":
                return dict(**common, findings=[])
            return dict(**common, tests_passed=1, tests_failed=0, tests_skipped=0, health="skipped")

        async def cleanup(self, value):
            self.cleaned.append(value["run_id"])

    async def scenario():
        async def resolver(*_):
            return "a"*40
        store, executor = MemoryStore(), Executor()
        runtime = Orchestrator(Settings(allowed_repositories=("https://github.com/a/b",)), store, Events(store, 100), executor, resolver)
        value = await runtime.start("https://github.com/a/b", "test-owner")
        with pytest.raises(HTTPException) as error:
            await runtime.start("https://github.com/a/b", "test-owner")
        assert error.value.status_code == 409
        await runtime.tasks[value["run_id"]]
        result = await store.get_run(value["run_id"])
        assert result["status"] == "completed"
        assert set(result["reports"]) == {"security", "build"}
        assert executor.cleaned == [value["run_id"]]
    asyncio.run(scenario())


def test_publication_cannot_claim_success_without_validation():
    with pytest.raises(ValueError):
        RemediationReport(commit_sha="a"*40, status="passed", checks=[], publication_status="published",
                          fixed_repository_url="https://github.com/a/b-fixed", fixed_commit_sha="b"*40,
                          diff="", limitations=[])
    with pytest.raises(ValueError):
        Remediate(finding_id="f1", approved=False, commit_sha="a"*40, destination_owner="a", destination_name="b-fixed")
