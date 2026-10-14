"""Regression for the Azure append-blob initialization behavior (unit double)."""

import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

from app.store import BlobStore
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError


def test_append_does_not_reinitialize_existing_event_history():
    class AzureAppendBlobDouble:
        data = None

        async def create_append_blob(self, **kwargs):
            if self.data is not None and kwargs.get("match_condition") == MatchConditions.IfMissing:
                raise ResourceModifiedError("Unit double: conditional create rejected")
            self.data = b""  # Real SDK's default behavior is destructive reinitialization.

        async def append_block(self, data, **kwargs):
            assert kwargs["retry_total"] == 0
            self.data += data

    async def scenario():
        blob = AzureAppendBlobDouble()
        service = SimpleNamespace(get_blob_client=lambda *args: blob)
        identifier = str(uuid4())
        for index in (1, 2, 3):
            store = object.__new__(BlobStore)  # A fresh process must preserve history too.
            store.service = service
            await store.append_event(identifier, {"event_id": index})
        assert [json.loads(line)["event_id"] for line in blob.data.splitlines()] == [1, 2, 3]

    asyncio.run(scenario())
