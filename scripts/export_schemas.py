#!/usr/bin/env python3
"""Export platform report contracts without importing a cloud client or executing a workflow."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.contracts import BuildReport, RemediationReport, ReviewReport  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed schemas match models without edits")
    args = parser.parse_args()
    directory = ROOT / "workflows/schemas"
    for name, model in (("review", ReviewReport), ("build", BuildReport), ("remediation", RemediationReport)):
        path = directory / f"{name}.json"
        value = json.dumps(model.model_json_schema(), indent=2) + "\n"
        if args.check:
            if not path.exists() or path.read_text() != value:
                raise SystemExit(f"Schema differs: {path.relative_to(ROOT)}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(value)


if __name__ == "__main__":
    main()
