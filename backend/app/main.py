"""Single-process Azure app, bearer-authenticated API and resumable SSE."""
import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .auth import EntraVerifier, Principal
from .config import Settings
from .contracts import Remediate, StartRun, run_id
from .store import BlobStore, Events, UnavailableStore


def create_app(settings=None, *, store=None, executor=None, verifier=None):
    settings = settings or Settings.from_env()
    store = store or (BlobStore(settings.storage_account, settings.managed_identity_client_id)
                      if settings.storage_account and settings.managed_identity_client_id else UnavailableStore())
    events = Events(store, settings.event_retention_limit)
    authenticate = verifier or EntraVerifier(settings)
    runtime = None
    if executor is not None:
        from .orchestrator import Orchestrator
        runtime = Orchestrator(settings, store, events, executor)

    @asynccontextmanager
    async def lifespan(app):
        app.state.ready = False
        try:
            await store.ready()
            if runtime:
                await runtime.reconcile()
            app.state.ready = True
        except Exception:
            # Health exposes fixed statuses, never SDK errors or credentials.
            app.state.ready = False
        yield
        if runtime:
            await runtime.shutdown()
        await store.close()

    app = FastAPI(title="From Untrusted Code to Trusted Decisions", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.state.ready = False

    @app.middleware("http")
    async def boundaries(request, call_next):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin")
            if origin and origin != settings.public_origin:
                return JSONResponse({"detail": "Origin not permitted"}, status_code=403)
            # Bound streaming/chunked bodies too, not just Content-Length.
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 16384:
                    return JSONResponse({"detail": "Request too large"}, status_code=413)
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self' https://login.microsoftonline.com; "
            "frame-src https://login.microsoftonline.com; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        return response

    @app.exception_handler(Exception)
    async def failure(request, exc):
        return JSONResponse({"detail": "Operation unavailable; no success is assumed"}, status_code=503)

    async def owned(identifier: str, principal: Principal):
        try:
            value = await store.get_run(run_id(identifier))
        except (KeyError, ValueError):
            raise HTTPException(404, "Run not found") from None
        if value["owner_id"] != principal.object_id:
            raise HTTPException(404, "Run not found")
        return value

    def enabled():
        if not settings.live_execution_enabled or runtime is None:
            raise HTTPException(503, "Live execution awaits verified Milestone 0 and deployment configuration")
        if not app.state.ready:
            raise HTTPException(503, "Durable storage and startup reconciliation must succeed first")

    @app.get("/api/healthz")
    async def health():
        return {"status": "healthy"}

    @app.get("/api/readyz")
    async def ready():
        return JSONResponse({"ready": app.state.ready, "live_execution_enabled": settings.live_execution_enabled and runtime is not None},
                            status_code=200 if app.state.ready else 503)

    @app.get("/api/config")
    async def config():
        return {"tenant_id": settings.tenant_id, "spa_client_id": settings.spa_client_id,
                "api_scope": f"api://{settings.api_client_id}/access_as_user",
                "live_execution_enabled": settings.live_execution_enabled and runtime is not None,
                "allowed_repositories": settings.allowed_repositories,
                "publication_owner": settings.publication_owner}

    @app.get("/api/me")
    async def me(principal: Principal = Depends(authenticate)):
        return {"object_id": principal.object_id}

    @app.get("/api/runs")
    async def runs(principal: Principal = Depends(authenticate)):
        return [r for r in await store.runs() if r["owner_id"] == principal.object_id]

    @app.post("/api/runs", status_code=202)
    async def start(body: StartRun, principal: Principal = Depends(authenticate)):
        enabled()
        return await runtime.start(body.repository_url, principal.object_id)

    @app.get("/api/runs/{identifier}")
    async def get_run(identifier: str, principal: Principal = Depends(authenticate)):
        return await owned(identifier, principal)

    @app.post("/api/runs/{identifier}/remediate", status_code=202)
    async def remediate(identifier: str, body: Remediate, principal: Principal = Depends(authenticate)):
        enabled()
        value = await owned(identifier, principal)
        return await runtime.remediate(value, body)

    @app.post("/api/runs/{identifier}/cleanup", status_code=202)
    async def cleanup(identifier: str, principal: Principal = Depends(authenticate)):
        value = await owned(identifier, principal)
        if runtime is None:
            raise HTTPException(503, "Sandbox cleanup adapter not configured")
        return await runtime.cancel(value)

    @app.get("/api/runs/{identifier}/events")
    async def stream(identifier: str, request: Request, principal: Principal = Depends(authenticate)):
        await owned(identifier, principal)
        try:
            after = int(request.headers.get("last-event-id", "0"))
            if after < 0:
                raise ValueError
        except ValueError:
            raise HTTPException(400, "Invalid Last-Event-ID") from None
        current = await events.read(identifier)
        if after > len(current):
            raise HTTPException(409, "Event cursor is beyond this run's history")

        async def output():
            cursor = after
            # Re-authenticate on reconnection at least once per minute so expiry and revocation checks recur.
            deadline = asyncio.get_running_loop().time() + 60
            while not await request.is_disconnected() and asyncio.get_running_loop().time() < deadline:
                signal = events.signals.setdefault(identifier, asyncio.Event())
                signal.clear()
                for event in (await events.read(identifier))[cursor:]:
                    yield f"id: {event['event_id']}\ndata: {json.dumps(event)}\n\n"
                    cursor = event["event_id"]
                try:
                    await asyncio.wait_for(signal.wait(), timeout=10)
                except TimeoutError:
                    yield ": heartbeat\n\n"
        return StreamingResponse(output(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"})

    static = Path(__file__).resolve().parents[2] / "static"
    if (static / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @app.get("/")
    async def index():
        if not (static / "index.html").is_file():
            raise HTTPException(503, "Frontend assets have not been built")
        return FileResponse(static / "index.html")

    return app


app = create_app()
