"""Explicit unit doubles for retention policy, restart and manual deletion."""

import asyncio
from uuid import uuid4

import pytest
from app.config import Settings
from app.orchestrator import Orchestrator
from app.store import Events
from conftest import MemoryStore


class Executor:
    def __init__(self, failure=False):
        self.stopped = []
        self.deleted = []
        self.failure = failure

    async def retain(self, value):
        self.stopped.append(value["run_id"])
        if self.failure:
            raise OSError("TEST DOUBLE: stop failed")
        return ["test-owned-sandbox"]

    async def cleanup(self, value):
        self.deleted.append(value["run_id"])


@pytest.mark.parametrize("outcome", ["completed", "failed", "timed_out", "cancelled"])
def test_all_automatic_outcomes_retain_and_explicit_cleanup_deletes(outcome):
    async def scenario():
        store, executor = MemoryStore(), Executor()
        runtime = Orchestrator(Settings(), store, Events(store, 100), executor)
        value = dict(run_id=str(uuid4()), status=outcome, retain_sandboxes=True, cleanup_pending=True)
        await runtime._finalize(value)
        assert value["status"] == outcome and not value["cleanup_pending"]
        assert value["retained_sandbox_ids"] == ["test-owned-sandbox"]
        assert executor.deleted == []
        # A fresh host leaves completed retained runs alone.
        fresh = Orchestrator(Settings(), store, Events(store, 100), executor)
        await fresh.reconcile()
        assert executor.stopped == [value["run_id"]]
        await fresh.cancel(value)
        saved = await store.get_run(value["run_id"])
        assert executor.deleted == [value["run_id"]]
        assert not saved["retained_sandbox_ids"] and saved["cleanup_requested"]

    asyncio.run(scenario())


def test_interrupted_retention_retries_stop_without_deleting_or_reopening_admission():
    async def scenario():
        store, executor = MemoryStore(), Executor(failure=True)
        value = dict(run_id=str(uuid4()), status="running", retain_sandboxes=True, cleanup_pending=True)
        await store.save_run(value)
        runtime = Orchestrator(Settings(), store, Events(store, 100), executor)
        with pytest.raises(RuntimeError):
            await runtime.reconcile()
        assert runtime.cleanup_failed and not executor.deleted
        saved = await store.get_run(value["run_id"])
        assert saved["status"] == "retention_failed" and saved["cleanup_pending"]
        executor.failure = False
        await runtime.reconcile()
        assert not runtime.cleanup_failed and not executor.deleted
        assert (await store.get_run(value["run_id"]))["status"] == "interrupted"

    asyncio.run(scenario())


def test_legacy_and_explicit_deletion_intents_keep_deletion_on_restart():
    async def scenario():
        store, executor = MemoryStore(), Executor()
        for extra in ({}, {"retain_sandboxes": True, "cleanup_requested": True}):
            await store.save_run(dict(run_id=str(uuid4()), status="running", cleanup_pending=True, **extra))
        await Orchestrator(Settings(), store, Events(store, 100), executor).reconcile()
        assert len(executor.deleted) == 2 and not executor.stopped

    asyncio.run(scenario())


def test_new_run_snapshots_default_retention_and_finishes_without_deletion():
    class RunningExecutor(Executor):
        async def run(self, value, role, emit):
            common = dict(commit_sha=value["commit_sha"], status="failed", checks=[], limitations=["TEST DOUBLE"])
            if role == "security":
                return dict(**common, findings=[])
            return dict(**common, tests_passed=0, tests_failed=1, tests_skipped=0, health="skipped")

    async def scenario():
        async def resolver(*args):
            return "a" * 40

        store, executor = MemoryStore(), RunningExecutor()
        runtime = Orchestrator(
            Settings(allowed_repositories=("https://github.com/a/b",)), store, Events(store, 100), executor, resolver
        )
        value = await runtime.start("https://github.com/a/b", "owner")
        assert value["retain_sandboxes"] is True
        await runtime.tasks[value["run_id"]]
        saved = await store.get_run(value["run_id"])
        assert saved["status"] == "completed" and saved["finished_at"]
        assert saved["reports"]["build"]["status"] == "failed"
        assert saved["retained_sandbox_ids"] and not saved["cleanup_pending"]
        assert executor.stopped == [value["run_id"]] and executor.deleted == []

    asyncio.run(scenario())
