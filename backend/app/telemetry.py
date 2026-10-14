"""Allowlisted structured console telemetry for ACA -> Azure Monitor/Log Analytics.

No headers, request bodies, query strings, model prompts, reports or token values.
"""

import json
import logging
import sys
from uuid import UUID

logger = logging.getLogger("academo.telemetry")
if not logger.handlers:
    logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)
logger.propagate = False


def lifecycle(event):
    # Event/report contents are intentionally excluded even after normal redaction.
    value = {key: event[key] for key in ("event_id", "timestamp", "sandbox_role", "type")}
    value["run_id"] = str(UUID(event["run_id"]))
    if event.get("sandbox_id"):
        value["sandbox_id"] = str(UUID(event["sandbox_id"]))
    status = event.get("payload", {}).get("status")
    if status in {
        "pending",
        "running",
        "passed",
        "failed",
        "skipped",
        "timed_out",
        "completed",
        "cancelled",
        "interrupted",
        "cleanup_failed",
    }:
        value["status"] = status
    logger.info(json.dumps(value, separators=(",", ":")))
