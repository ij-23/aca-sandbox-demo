"""Bounded deterministic orchestration; no model or repository execution here."""

import asyncio
from uuid import uuid4

from fastapi import HTTPException

from .contracts import BuildReport, RemediationReport, ReviewReport, now
from .security import redact, repository_parts, resolve_public_sha


class Orchestrator:
    def __init__(self, settings, store, events, executor, resolver=resolve_public_sha):
        self.settings, self.store, self.events = settings, store, events
        self.executor, self.resolver = executor, resolver
        self.admission = asyncio.Lock()
        self.state_write = asyncio.Lock()
        self.active = False
        self.tasks: dict[str, asyncio.Task] = {}
        self.cleanup_failures: set[str] = set()

    @property
    def cleanup_failed(self):
        return bool(self.cleanup_failures)

    async def reconcile(self):
        # Reports/events survive restart; execution is not resumed.
        failures = []
        for value in await self.store.runs():
            if value.get("cleanup_pending") or value["status"] in (
                "running",
                "remediating",
                "cleanup_failed",
            ):
                value["status"] = "interrupted"
                # This is when interruption was detected, not an invented crash
                # time. Preserve it across cleanup retries so UI timers stop.
                value["finished_at"] = value.get("finished_at") or now()
                try:
                    try:
                        await self.store.save_run(value)
                        await self.events.emit(
                            value["run_id"], "system", "run.interrupted", reason="Host restarted; execution not resumed"
                        )
                    except Exception:
                        value["event_delivery_failed"] = True
                    finally:
                        await self._cleanup(value)
                except Exception:
                    failures.append(value["run_id"])
        if failures:
            raise RuntimeError("Startup reconciliation requires operator attention")

    async def _claim(self):
        if self.active or self.cleanup_failed:
            raise HTTPException(409, "Another run or unresolved cleanup holds the execution slot")
        self.active = True

    async def start(self, url, owner):
        async with self.admission:
            await self._claim()
            try:
                repository_parts(url, self.settings.allowed_repositories)
                sha = await self.resolver(url, self.settings.allowed_repositories)
                value = {
                    "run_id": str(uuid4()),
                    "owner_id": owner,
                    "repository_url": url,
                    "commit_sha": sha,
                    "created_at": now(),
                    "status": "running",
                    "reports": {},
                    "remediation_attempted": False,
                    "cleanup_pending": True,
                }
                await self.store.save_run(value)
                await self.events.emit(value["run_id"], "system", "run.started", commit_sha=sha, repository_url=url)
                self.tasks[value["run_id"]] = asyncio.create_task(self._evaluate(value))
                return value
            except ValueError as exc:
                self.active = False
                raise HTTPException(422, str(exc)) from None
            except BaseException:
                self.active = False
                raise

    async def _role(self, value, role):
        async def emit(event_type, *, sandbox_id=None, step_id=None, **payload):
            await self.events.emit(value["run_id"], role, event_type, sandbox_id=sandbox_id, step_id=step_id, **payload)

        try:
            report = await self.executor.run(value, role, emit)
        except Exception as error:
            # Exception text can contain SDK responses; expose only the class.
            await emit("workflow.failed", error_type=type(error).__name__, status="failed")
            raise
        schema = {"security": ReviewReport, "build": BuildReport, "remediation": RemediationReport}[role]
        report = schema.model_validate(report).model_dump()
        if report["commit_sha"] != value["commit_sha"]:
            raise ValueError("Report commit does not match the pinned run")
        if role == "remediation" and report.get("fixed_repository_url"):
            approval = value["approval"]
            expected = f"https://github.com/{approval['destination_owner']}/{approval['destination_name']}"
            if report["fixed_repository_url"] != expected:
                raise ValueError("Publication report differs from the approved destination")
        report = redact(report)
        await self.store.save_report(value["run_id"], role, report)
        async with self.state_write:
            value["reports"][role] = report
            await self.store.save_run(value)
        # Workflow boundaries must come from the actual sandbox runtime, not report persistence.
        await emit("report.persisted", status=report["status"])

    async def _cleanup(self, value):
        try:
            async with asyncio.timeout(90):
                await self.executor.cleanup(value)
            value["cleanup_pending"] = False
            if value["status"] == "cleanup_failed":
                value["status"] = "interrupted"
            await self.store.save_run(value)
            self.cleanup_failures.discard(value["run_id"])
        except Exception:
            value["status"] = "cleanup_failed"
            value["cleanup_pending"] = True
            self.cleanup_failures.add(value["run_id"])
            await self.store.save_run(value)
            raise
        try:
            await self.events.emit(value["run_id"], "system", "cleanup.completed")
        except Exception:
            # A full event log must not permanently block confirmed cleanup.
            # Deletion evidence has already been saved in durable run state.
            value["event_delivery_failed"] = True
            await self.store.save_run(value)

    async def _evaluate(self, value, remediation=False):
        try:
            async with asyncio.timeout(self.settings.max_run_seconds):
                if remediation:
                    await self._role(value, "remediation")
                else:
                    # TaskGroup cancels the peer on failure; executor owns each sandbox's finally cleanup.
                    async with asyncio.TaskGroup() as group:
                        for role in ("security", "build"):
                            group.create_task(self._role(value, role))
            value["status"] = "completed"
        except TimeoutError:
            value["status"] = "timed_out"
        except asyncio.CancelledError:
            value["status"] = "cancelled"
        except Exception:
            value["status"] = "failed"
        finally:
            try:
                await self._cleanup(value)
            except Exception:
                value["status"] = "cleanup_failed"
                self.cleanup_failures.add(value["run_id"])
            value["finished_at"] = now()
            try:
                await self.store.save_run(value)
                try:
                    await self.events.emit(value["run_id"], "system", "run.finished", status=value["status"])
                except Exception:
                    value["event_delivery_failed"] = True
                    await self.store.save_run(value)
            finally:
                self.tasks.pop(value["run_id"], None)
                self.active = False

    async def remediate(self, value, approval):
        async with self.admission:
            # Re-read under the admission lock: concurrent requests may carry stale snapshots.
            value = await self.store.get_run(value["run_id"])
            if value["remediation_attempted"] or value["status"] != "completed":
                raise HTTPException(409, "Remediation is not available for this run")
            _, repo = repository_parts(value["repository_url"], self.settings.allowed_repositories)
            findings = value["reports"].get("security", {}).get("findings", [])
            finding = next(
                (f for f in findings if f["id"] == approval.finding_id and f["verification_status"] == "verified"), None
            )
            if (
                not finding
                or approval.commit_sha != value["commit_sha"]
                or approval.destination_owner != self.settings.publication_owner
                or approval.destination_name != repo + "-fixed"
            ):
                raise HTTPException(409, "Approval does not match a verified finding and configured destination")
            await self._claim()
            try:
                value.update(
                    remediation_attempted=True,
                    status="remediating",
                    finished_at=None,
                    approval=approval.model_dump(),
                    finding=finding,
                    cleanup_pending=True,
                )
                await self.store.save_run(value)
                await self.events.emit(
                    value["run_id"],
                    "system",
                    "remediation.approved",
                    finding_id=finding["id"],
                    destination=f"{approval.destination_owner}/{approval.destination_name}",
                )
                self.tasks[value["run_id"]] = asyncio.create_task(self._evaluate(value, remediation=True))
            except BaseException:
                self.active = False
                raise
            return value

    async def cancel(self, value):
        task = self.tasks.get(value["run_id"])
        if task:
            task.cancel()
            await task
        else:
            async with self.admission:
                if self.active:
                    raise HTTPException(409, "An active run holds the cleanup slot")
                value = await self.store.get_run(value["run_id"])
                await self._cleanup(value)
        return await self.store.get_run(value["run_id"])

    async def shutdown(self):
        pending = list(self.tasks.values())
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
