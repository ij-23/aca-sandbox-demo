"""Private Blob persistence via managed identity; no key or local-data fallback."""

import asyncio
import json
from collections import OrderedDict, deque
from dataclasses import dataclass

from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from azure.identity.aio import ManagedIdentityCredential
from azure.storage.blob.aio import BlobServiceClient

from .contracts import run_id


class BlobStore:
    def __init__(self, account: str, client_id: str):
        if not account.isalnum() or not client_id:
            raise ValueError("Storage and managed identity must be configured")
        self.credential = ManagedIdentityCredential(client_id=client_id)
        self.service = BlobServiceClient(
            f"https://{account}.blob.core.windows.net",
            credential=self.credential,
            connection_timeout=10,
            read_timeout=20,
            retry_total=1,
        )

    async def ready(self):
        for name in ("reports", "events", "diffs", "replay"):
            await self.service.get_container_client(name).get_container_properties()

    async def save_run(self, value: dict):
        key = run_id(value["run_id"]) + "/state.json"
        await self.service.get_blob_client("reports", key).upload_blob(json.dumps(value), overwrite=True)

    async def get_run(self, identifier: str) -> dict:
        blob = self.service.get_blob_client("reports", run_id(identifier) + "/state.json")
        try:
            return json.loads(await (await blob.download_blob()).readall())
        except ResourceNotFoundError:
            raise KeyError(identifier) from None

    async def runs(self) -> list[dict]:
        values = []
        async for blob in self.service.get_container_client("reports").list_blobs():
            if blob.name.endswith("/state.json"):
                values.append(await self.get_run(blob.name.split("/")[0]))
        return values

    async def append_event(self, identifier: str, value: dict):
        blob = self.service.get_blob_client("events", run_id(identifier) + "/events.jsonl")
        try:
            # Default create_append_blob overwrites existing contents. Conditional
            # creation is mandatory, including after process restart.
            await blob.create_append_blob(match_condition=MatchConditions.IfMissing)
        except (ResourceExistsError, ResourceModifiedError):
            pass
        # No SDK retries: ambiguous append must not silently duplicate an event.
        await blob.append_block((json.dumps(value) + "\n").encode(), retry_total=0)

    async def events(self, identifier: str) -> list[dict]:
        blob = self.service.get_blob_client("events", run_id(identifier) + "/events.jsonl")
        try:
            properties = await blob.get_blob_properties()
            if properties.size > 16 * 1024 * 1024:
                raise ValueError("Event log exceeds application retention bound")
            data = await (await blob.download_blob()).readall()
            return [json.loads(line) for line in data.splitlines() if line]
        except ResourceNotFoundError:
            return []

    async def save_report(self, identifier: str, role: str, value: dict):
        if role not in ("security", "build", "remediation"):
            raise ValueError("Invalid report role")
        await self.service.get_blob_client("reports", f"{run_id(identifier)}/{role}.json").upload_blob(
            json.dumps(value), overwrite=True
        )
        if role == "remediation" and value.get("diff"):
            await self.service.get_blob_client("diffs", f"{run_id(identifier)}/remediation.diff").upload_blob(
                value["diff"], overwrite=True
            )

    async def save_ownership(self, record: dict):
        from uuid import UUID

        nonce = UUID(record["nonce"]).hex
        key = f"{run_id(record['run_id'])}/ownership/{nonce}.json"
        await self.service.get_blob_client("reports", key).upload_blob(json.dumps(record), overwrite=True)

    async def ownership(self, identifier: str):
        prefix = f"{run_id(identifier)}/ownership/"
        values = []
        async for blob in self.service.get_container_client("reports").list_blobs(name_starts_with=prefix):
            data = await self.service.get_blob_client("reports", blob.name).download_blob()
            values.append(json.loads(await data.readall()))
        return values

    async def close(self):
        await self.service.close()
        await self.credential.close()


class UnavailableStore:
    """Configuration failure is explicit; never present volatile data as durable."""

    async def ready(self):
        raise RuntimeError("Azure Blob Storage is not configured")

    async def close(self):
        pass

    async def runs(self):
        await self.ready()

    async def get_run(self, identifier):
        await self.ready()


@dataclass
class EventWindow:
    entries: deque
    count: int
    bytes_used: int


class Events:
    def __init__(self, store, limit: int, *, window=256, cached_runs=8, byte_limit=15 * 1024 * 1024):
        self.store = store
        self.limit = limit
        self.window, self.cached_runs, self.byte_limit = window, cached_runs, byte_limit
        self.lock = asyncio.Lock()
        self.changed = asyncio.Event()
        self.cache: OrderedDict[str, EventWindow] = OrderedDict()

    @staticmethod
    def size(value):
        return len((json.dumps(value) + "\n").encode())

    async def _load(self, identifier):
        values = await self.store.events(identifier)
        if any(e["event_id"] != i for i, e in enumerate(values, 1)):
            raise ValueError("Stored event sequence is not contiguous")
        self.cache[identifier] = EventWindow(
            deque(values[-self.window :], maxlen=self.window), len(values), sum(map(self.size, values))
        )
        self.cache.move_to_end(identifier)
        while len(self.cache) > self.cached_runs:
            self.cache.popitem(last=False)
        return values

    async def read(self, identifier: str, after: int = 0) -> list[dict]:
        async with self.lock:
            cached = self.cache.get(identifier)
            if cached is None or (cached.entries and after < cached.entries[0]["event_id"] - 1):
                values = await self._load(identifier)
            else:
                self.cache.move_to_end(identifier)
                values = list(cached.entries)
            return [e for e in values if e["event_id"] > after]

    async def emit(self, identifier: str, role: str, event_type: str, *, sandbox_id=None, step_id=None, **payload):
        from .contracts import Event, now
        from .security import redact

        async with self.lock:
            if identifier not in self.cache:
                await self._load(identifier)
            previous = self.cache[identifier]
            self.cache.move_to_end(identifier)
            if previous.count >= self.limit:
                raise RuntimeError("Per-run event budget exhausted")
            value = Event(
                event_id=previous.count + 1,
                run_id=identifier,
                timestamp=now(),
                sandbox_role=role,
                sandbox_id=sandbox_id,
                type=event_type,
                step_id=step_id,
                payload=redact(payload),
            ).model_dump()
            size = self.size(value)
            if size > 16000:
                raise ValueError("Event exceeds payload budget")
            if previous.bytes_used + size > self.byte_limit:
                raise RuntimeError("Per-run event byte budget exhausted")
            try:
                await self.store.append_event(identifier, value)
            except Exception:
                # Re-read after an ambiguous append; never reuse a cached event ID.
                self.cache.pop(identifier, None)
                raise
            previous.entries.append(value)
            previous.count += 1
            previous.bytes_used += size
            self.changed.set()
            # Console diagnostics follow persistence and cannot break delivery/cleanup.
            try:
                from .telemetry import lifecycle

                lifecycle(value)
            except Exception:
                pass
            return value
