"""Trusted, intentionally vulnerable teaching fixture. Execute only in an ACA Sandbox."""

from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI()
DOCUMENT_ROOT = Path(__file__).parent / "documents"


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/document")
def document(name: str):
    # Intentional demo issue: user input is joined without a containment check.
    # The regression test uses a harmless temporary canary, never a credential.
    target = DOCUMENT_ROOT / name
    try:
        return {"content": target.read_text()}
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
        raise HTTPException(404, "Document not found") from None
