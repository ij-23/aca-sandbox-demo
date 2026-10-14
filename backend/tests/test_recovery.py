"""Local doubles exercise failure recovery; no cloud execution or repository code."""

import asyncio
from uuid import uuid4

import pytest
from app.config import Settings
from app.orchestrator import Orchestrator
from app.store import Events
from conftest import MemoryStore
from fastapi import HTTPException


def test_event_window_and_eviction_preserve_durable_resume():
    async def scenario():
        store = MemoryStore()
        bus = Events(store, 100, window=3, cached_runs=2)
        identifier = str(uuid4())
        for i in range(10):
            await bus.emit(identifier, "system", "test.event", index=i)
        assert len(bus.cache[identifier].entries) == 3
        assert [e["event_id"] for e in await bus.read(identifier, after=8)] == [9, 10]
        assert [e["event_id"] for e in await bus.read(identifier, after=1)] == list(range(2, 11))
        for _ in range(3):
            await bus.emit(str(uuid4()), "system", "test.event")
        assert len(bus.cache) == 2
        await bus.emit(identifier, "system", "test.event")
        assert store.logs[identifier][-1]["event_id"] == 11

    asyncio.run(scenario())


def test_ambiguous_append_reloads_ids_and_byte_limit_blocks_before_write():
    class Ambiguous(MemoryStore):
        failed = False

        async def append_event(self, identifier, value):
            await super().append_event(identifier, value)
            if not self.failed:
                self.failed = True
                raise OSError("TEST DOUBLE: append committed but acknowledgement lost")

    async def scenario():
        store = Ambiguous()
        bus = Events(store, 100, byte_limit=1000)
        identifier = str(uuid4())
        with pytest.raises(OSError):
            await bus.emit(identifier, "system", "test.event")
        await bus.emit(identifier, "system", "test.event")
        assert [e["event_id"] for e in store.logs[identifier]] == [1, 2]
        with pytest.raises(RuntimeError, match="byte budget"):
            await bus.emit(identifier, "system", "test.event", text="x" * 700)
        assert len(store.logs[identifier]) == 2

    asyncio.run(scenario())


def test_restart_continues_cleanup_and_retry_releases_only_resolved_failure():
    class Executor:
        failing = set()
        attempted = []

        async def cleanup(self, value):
            self.attempted.append(value["run_id"])
            if value["run_id"] in self.failing:
                raise RuntimeError("TEST DOUBLE: failed cleanup")

    async def scenario():
        store, executor = MemoryStore(), Executor()
        identifiers = [str(uuid4()) for _ in range(3)]
        for identifier in identifiers:
            await store.save_run({"run_id": identifier, "status": "running", "cleanup_pending": True})
        executor.failing = set(identifiers[:2])
        runtime = Orchestrator(Settings(), store, Events(store, 100), executor)
        with pytest.raises(RuntimeError, match="reconciliation"):
            await runtime.reconcile()
        assert executor.attempted == identifiers
        assert runtime.cleanup_failed
        assert not (await store.get_run(identifiers[2]))["cleanup_pending"]
        executor.failing.remove(identifiers[0])
        result = await runtime.cancel(await store.get_run(identifiers[0]))
        assert result["status"] == "interrupted"
        assert not result["cleanup_pending"]
        assert runtime.cleanup_failed  # The other failure still owns the admission block.
        with pytest.raises(HTTPException):
            await runtime._claim()
        executor.failing.clear()
        await runtime.cancel(await store.get_run(identifiers[1]))
        assert not runtime.cleanup_failed
        await runtime._claim()
        assert runtime.active

    asyncio.run(scenario())


def test_event_persistence_failure_does_not_skip_restart_cleanup():
    class Broken(MemoryStore):
        async def append_event(self, *args):
            raise OSError("TEST DOUBLE")

    class Executor:
        cleaned = False

        async def cleanup(self, value):
            self.cleaned = True

    async def scenario():
        store, executor = Broken(), Executor()
        await store.save_run({"run_id": str(uuid4()), "status": "running"})
        runtime = Orchestrator(Settings(), store, Events(store, 100), executor)
        await runtime.reconcile()
        assert executor.cleaned
        assert not runtime.cleanup_failed
        saved = (await store.runs())[0]
        assert saved["event_delivery_failed"]
        assert not saved["cleanup_pending"]  # Deletion evidence survives in state when the event log fails.

    asyncio.run(scenario())
