# syntax=docker/dockerfile:1
FROM node:24-alpine AS frontend
ARG NPM_REGISTRY=https://registry.npmjs.org/
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts --registry="$NPM_REGISTRY"
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim AS dependencies
ARG PIP_INDEX_URL=https://pypi.org/simple/
WORKDIR /app
COPY requirements.txt ./
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --index-url "$PIP_INDEX_URL" --no-cache-dir --require-hashes -r requirements.txt

FROM python:3.13-slim AS runtime
WORKDIR /app
LABEL com.azure.containerizationassist.createdby="containerization-assist"
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 LIVE_EXECUTION_ENABLED=false
COPY --from=dependencies /opt/venv /opt/venv
COPY backend/app/ /app/backend/app/
COPY workflows/ /app/workflows/
COPY scripts/smoke_workflow_runner.py /app/scripts/smoke_workflow_runner.py
COPY --from=frontend /app/backend/static/ /app/backend/static/
ENV PYTHONPATH=/app/backend
RUN useradd --create-home --uid 10001 appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/healthz', timeout=3)"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log", "--timeout-graceful-shutdown", "90"]
USER appuser
