"""Private Blob persistence via managed identity; no key or local-data fallback."""
import json
from typing import Any

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity.aio import ManagedIdentityCredential
from azure.storage.blob.aio import BlobServiceClient

from .contracts import run_id


class BlobStore:
    def __init__(self, account: str, client_id: str):
        if not account.isalnum() or not client_id:
            raise ValueError("Storage and managed identity must be configured")
        self.credential = ManagedIdentityCredential(client_id=client_id)
        self.service = BlobServiceClient(f"https://{account}.blob.core.windows.net", credential=self.credential,
                                        connection_timeout=10, read_timeout=20, retry_total=1)

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
            await blob.create_append_blob()
        except ResourceExistsError:
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
            json.dumps(value), overwrite=True)
        if role == "remediation" and value.get("diff"):
            await self.service.get_blob_client("diffs", f"{run_id(identifier)}/remediation.diff").upload_blob(
                value["diff"], overwrite=True)

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


class Events:
    def __init__(self, store, limit: int):
        import asyncio
        self.store = store
        self.limit = limit
        self.locks: dict[str, Any] = {}
        self.signals: dict[str, Any] = {}
        self.cache: dict[str, list[dict]] = {}
        self.asyncio = asyncio

    async def read(self, identifier: str) -> list[dict]:
        if identifier not in self.cache:
            self.cache[identifier] = await self.store.events(identifier)
        return self.cache[identifier]

    async def emit(self, identifier: str, role: str, kind: str, *, sandbox_id=None, step_id=None, **payload):
        from .contracts import Event, now
        from .security import redact
        lock = self.locks.setdefault(identifier, self.asyncio.Lock())
        async with lock:
            previous = await self.read(identifier)
            if len(previous) >= self.limit:
                raise RuntimeError("Per-run event budget exhausted")
            value = Event(event_id=len(previous) + 1, run_id=identifier, timestamp=now(), sandbox_role=role,
                          sandbox_id=sandbox_id, type=kind, step_id=step_id, payload=redact(payload)).model_dump()
            if len(json.dumps(value).encode()) > 16000:
                raise ValueError("Event exceeds payload budget")
            try:
                await self.store.append_event(identifier, value)
            except Exception:
                # Re-read after an ambiguous append; never reuse a cached event ID.
                self.cache.pop(identifier, None)
                raise
            previous.append(value)
            self.signals.setdefault(identifier, self.asyncio.Event()).set()
            return value
