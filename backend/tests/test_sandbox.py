"""Unit doubles for SDK ownership and cancellation; never creates Azure resources."""

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.config import Settings
from app.sandbox import OWNER, SandboxExecutor
from azure.core.exceptions import ResourceNotFoundError


class Ledger:
    def __init__(self, records):
        self.records = records

    async def ownership(self, identifier):
        return self.records

    async def save_ownership(self, record):
        pass


class BrokenEvents:
    async def emit(self, *args, **kwargs):
        raise OSError("Explicit test double: event store unavailable")


def record():
    run, nonce, identifier = str(uuid4()), uuid4().hex, str(uuid4())
    labels = {"owner": OWNER, "run-id": run, "role": "security", "nonce": nonce}
    return dict(run_id=run, nonce=nonce, sandbox_id=identifier, role="security", labels=labels, state="running")


def test_cleanup_survives_event_failure_and_requires_exact_404():
    data = record()

    class Sandbox:
        deleted = False
        gets = 0

        def get(self):
            self.gets += 1
            if self.deleted:
                raise ResourceNotFoundError("Test double 404")
            return SimpleNamespace(labels=data["labels"])

        def delete(self):
            self.deleted = True

    sandbox = Sandbox()
    group = SimpleNamespace(list_sandboxes=lambda: [], get_sandbox_client=lambda _: sandbox)
    executor = SandboxExecutor(Settings(), Ledger([data]), BrokenEvents(), group=group)
    value = {"run_id": data["run_id"]}
    asyncio.run(executor.cleanup(value))
    assert sandbox.deleted and sandbox.gets == 2
    assert data["state"] == "deleted" and value["event_delivery_failed"]


def test_cleanup_refuses_wrong_labels():
    data = record()
    sandbox = SimpleNamespace(
        get=lambda: SimpleNamespace(labels={"owner": "somebody-else"}), delete=lambda: pytest.fail("must not delete")
    )
    group = SimpleNamespace(list_sandboxes=lambda: [], get_sandbox_client=lambda _: sandbox)
    executor = SandboxExecutor(Settings(), Ledger([data]), BrokenEvents(), group=group)
    with pytest.raises(ValueError, match="ownership mismatch"):
        asyncio.run(executor.cleanup({"run_id": data["run_id"]}))


def test_cleanup_failure_does_not_strand_peer():
    first, second = record(), record()
    second["run_id"] = second["labels"]["run-id"] = first["run_id"]

    class Peer:
        deleted = False

        def get(self):
            if self.deleted:
                raise ResourceNotFoundError("Test double 404")
            return SimpleNamespace(labels=second["labels"])

        def delete(self):
            self.deleted = True

    peer = Peer()
    wrong = SimpleNamespace(get=lambda: SimpleNamespace(labels={"owner": "unrelated"}))
    group = SimpleNamespace(
        list_sandboxes=lambda: [],
        get_sandbox_client=lambda identifier: peer if identifier == second["sandbox_id"] else wrong,
    )
    executor = SandboxExecutor(Settings(), Ledger([first, second]), BrokenEvents(), group=group)
    with pytest.raises(ValueError, match="ownership mismatch"):
        asyncio.run(executor.cleanup({"run_id": first["run_id"]}))
    assert peer.deleted and second["state"] == "deleted"
    assert first["state"] == "running"


def test_ambiguous_create_never_claims_empty_list_is_cleanup():
    data = record()
    data["sandbox_id"] = None
    executor = SandboxExecutor(
        Settings(), Ledger([data]), BrokenEvents(), group=SimpleNamespace(list_sandboxes=lambda: [])
    )
    with pytest.raises(RuntimeError, match="Ambiguous creation"):
        asyncio.run(executor.cleanup({"run_id": data["run_id"]}))


def test_cancel_drains_thread_before_returning():
    import threading

    started, finish, done = threading.Event(), threading.Event(), threading.Event()

    def operation():
        started.set()
        finish.wait(2)
        done.set()

    async def scenario():
        executor = SandboxExecutor(Settings(), None, None, group=object())
        task = asyncio.create_task(executor.call(operation))
        await asyncio.to_thread(started.wait, 1)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
        finish.set()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert done.is_set()

    asyncio.run(scenario())


def test_egress_requires_explicit_domains_and_full_inspection():
    executor = SandboxExecutor(Settings(), None, None, group=object())
    policy = executor.egress_policy()
    assert policy.default_action == "Deny" and policy.traffic_inspection == "Full"
    executor.settings = Settings(sandbox_egress_hosts=("*",))
    with pytest.raises(ValueError):
        executor.egress_policy()


def test_event_failure_before_create_has_no_orphan(monkeypatch):
    data = record()
    data.update(state="prepared", sandbox_id=None)
    executor = SandboxExecutor(Settings(), Ledger([data]), BrokenEvents(), group=object())
    asyncio.run(executor.cleanup({"run_id": data["run_id"]}))
    assert data["state"] == "deleted"


def test_retention_stops_and_verifies_without_deletion_even_if_events_fail():
    data = record()

    class Sandbox:
        state = "Running"
        stops = 0

        def get(self):
            return SimpleNamespace(labels=data["labels"], state=self.state)

        def stop(self):
            self.stops += 1
            self.state = "Stopped"

        def delete(self):
            pytest.fail("Retention must never delete")

    sandbox = Sandbox()
    group = SimpleNamespace(list_sandboxes=lambda: [], get_sandbox_client=lambda _: sandbox)
    executor = SandboxExecutor(Settings(), Ledger([data]), BrokenEvents(), group=group)
    value = {"run_id": data["run_id"]}
    assert asyncio.run(executor.retain(value)) == [data["sandbox_id"]]
    assert data["state"] == "retained" and sandbox.stops == 1
    assert value["event_delivery_failed"]
    assert asyncio.run(executor.retain(value)) == [data["sandbox_id"]]
    assert sandbox.stops == 1


def test_retention_refuses_unrelated_sandbox_and_preserves_stop_failure():
    data = record()
    sandbox = SimpleNamespace(
        get=lambda: SimpleNamespace(labels={}, state="Running"),
        stop=lambda: pytest.fail("Must not stop unrelated Sandbox"),
        delete=lambda: pytest.fail("Must not delete"),
    )
    executor = SandboxExecutor(
        Settings(),
        Ledger([data]),
        BrokenEvents(),
        group=SimpleNamespace(list_sandboxes=lambda: [], get_sandbox_client=lambda _: sandbox),
    )
    with pytest.raises(ValueError, match="ownership mismatch"):
        asyncio.run(executor.retain({"run_id": data["run_id"]}))
    sandbox.get = lambda: SimpleNamespace(labels=data["labels"], state="Running")

    def failed_stop():
        raise OSError("TEST DOUBLE: stop unavailable")

    sandbox.stop = failed_stop
    with pytest.raises(OSError):
        asyncio.run(executor.retain({"run_id": data["run_id"]}))
    assert data["state"] == "running"


def test_explicit_cleanup_deletes_previously_retained_sandbox():
    data = record()
    data["state"] = "retained"

    class Sandbox:
        deleted = False

        def get(self):
            if self.deleted:
                raise ResourceNotFoundError("TEST DOUBLE")
            return SimpleNamespace(labels=data["labels"], state="Stopped")

        def delete(self):
            self.deleted = True

    sandbox = Sandbox()
    executor = SandboxExecutor(
        Settings(),
        Ledger([data]),
        BrokenEvents(),
        group=SimpleNamespace(list_sandboxes=lambda: [], get_sandbox_client=lambda _: sandbox),
    )
    asyncio.run(executor.cleanup({"run_id": data["run_id"]}))
    assert sandbox.deleted and data["state"] == "deleted"
