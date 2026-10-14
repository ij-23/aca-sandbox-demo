"""Explicit in-memory test double; never imported by deployed application."""

import copy


class MemoryStore:
    def __init__(self):
        self.records = {}
        self.logs = {}
        self.reports = {}

    async def ready(self):
        pass

    async def close(self):
        pass

    async def save_run(self, value):
        self.records[value["run_id"]] = copy.deepcopy(value)

    async def get_run(self, identifier):
        return copy.deepcopy(self.records[identifier])

    async def runs(self):
        return copy.deepcopy(list(self.records.values()))

    async def events(self, identifier):
        return copy.deepcopy(self.logs.get(identifier, []))

    async def append_event(self, identifier, value):
        self.logs.setdefault(identifier, []).append(copy.deepcopy(value))

    async def save_report(self, identifier, role, value):
        self.reports[identifier, role] = copy.deepcopy(value)
