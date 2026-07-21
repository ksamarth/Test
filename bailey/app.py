"""Bailey — upload a healthcare job offer, get the review your mentor would give you."""

import base64
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from analyzer import analyze_offer

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}

# Optional shared-access gate. When BAILEY_PASSWORD is set, every route except the
# health check requires HTTP Basic auth (any username + this password). Use it when
# hosting a public URL so a leaked link can't quietly spend your Anthropic API key.
ACCESS_PASSWORD = os.environ.get("BAILEY_PASSWORD", "")

app = FastAPI(title="Bailey")

STATIC_DIR = Path(__file__).parent / "static"
SAMPLE_OFFER = Path(__file__).parent / "sample_offers" / "sample_dso_offer.txt"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def _require_password(request: Request, call_next):
    if ACCESS_PASSWORD and request.url.path != "/api/health":
        supplied = ""
        header = request.headers.get("authorization", "")
        if header.startswith("Basic "):
            try:
                supplied = base64.b64decode(header[6:]).decode("utf-8").partition(":")[2]
            except Exception:
                supplied = ""
        if not secrets.compare_digest(supplied, ACCESS_PASSWORD):
            return Response(
                "Authentication required.",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Bailey"'},
            )
    return await call_next(request)


def _demo_mode() -> bool:
    return os.environ.get("BAILEY_DEMO", "").lower() in ("1", "true", "yes")


def _require_credentials() -> None:
    if not _demo_mode() and not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            503,
            "ANTHROPIC_API_KEY is not configured. Set it (or set BAILEY_DEMO=1 for a canned demo) and restart.",
        )


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

    _require_credentials()

    try:
        analysis = analyze_offer(file.filename or "offer", data)
    except RuntimeError as exc:
        raise HTTPException(422, str(exc))

    return JSONResponse({"filename": file.filename, "analysis": analysis.model_dump(mode="json")})


@app.post("/api/analyze-sample")
def analyze_sample() -> JSONResponse:
    """Analyze the bundled sample offer — powers the landing page's 'Try the sample offer'."""
    _require_credentials()
    data = SAMPLE_OFFER.read_bytes()
    try:
        analysis = analyze_offer(SAMPLE_OFFER.name, data)
    except RuntimeError as exc:
        raise HTTPException(422, str(exc))
    return JSONResponse({"filename": SAMPLE_OFFER.name, "analysis": analysis.model_dump(mode="json")})
