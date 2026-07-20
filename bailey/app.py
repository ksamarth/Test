"""Bailey — upload a healthcare job offer, get the review your mentor would give you."""

import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from analyzer import analyze_offer

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}

app = FastAPI(title="Bailey")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _demo_mode() -> bool:
    return os.environ.get("BAILEY_DEMO", "").lower() in ("1", "true", "yes")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "demo_mode": _demo_mode(),
        "api_key_configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> JSONResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Upload a PDF, DOCX, or TXT file.")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File is too large (25 MB limit).")
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")

    if not _demo_mode() and not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            503,
            "ANTHROPIC_API_KEY is not configured. Set it (or set BAILEY_DEMO=1 for a canned demo) and restart.",
        )

    try:
        analysis = analyze_offer(file.filename or "offer", data)
    except RuntimeError as exc:
        raise HTTPException(422, str(exc))

    return JSONResponse({"filename": file.filename, "analysis": analysis.model_dump(mode="json")})
