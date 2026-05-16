from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from dotenv import load_dotenv
from pathlib import Path
import re
import os
import logging

from models import AnalyzeRequest, AnalyzeResponse
from agents import run_pipeline
from websocket_manager import manager
from services.db import init_db, save_analysis, get_history, get_analysis_by_id
from services.pdf_generator import generate_pdf

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VentureLens")

OUTPUTS_DIR = Path(__file__).parent / "outputs"

app = FastAPI(
    title="VentureLens AI",
    description="AI-powered startup due diligence — 7-agent Google ADK pipeline",
    version="0.5.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB on startup
@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized.")


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "venturelens-ai", "version": "0.5.0"}


# ── WebSocket ──────────────────────────────────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WS connecting: {session_id}")
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.warning(f"WS error for {session_id}: {e}")
        manager.disconnect(session_id)


# ── Analyze ────────────────────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    logger.info(f"Starting analysis: {request.startup_name} (session: {request.session_id})")
    try:
        result = await run_pipeline(
            startup_name=request.startup_name,
            industry=request.industry,
            description=request.description,
            stage=request.stage,
            session_id=request.session_id,
        )

        # Inject form fields for DB storage (not in AnalyzeResponse model)
        result_for_db = {
            **result,
            "industry": request.industry,
            "stage":    request.stage,
        }

        # Find the latest report .md file for this startup
        slug = re.sub(r"[^a-z0-9]+", "_", request.startup_name.lower()).strip("_")
        report_file = None
        if OUTPUTS_DIR.exists():
            matches = sorted(OUTPUTS_DIR.glob(f"{slug}_report_*.md"),
                             key=lambda f: f.stat().st_mtime, reverse=True)
            if matches:
                report_file = str(matches[0])

        analysis_id = save_analysis(result_for_db, report_file=report_file)
        logger.info(f"Analysis saved to DB: id={analysis_id}")

        if request.session_id:
            await manager.broadcast_result(request.session_id, {**result, "analysis_id": analysis_id})

        return AnalyzeResponse(**result)

    except Exception as e:
        logger.error(f"Pipeline error for {request.startup_name}: {e}", exc_info=True)
        if request.session_id:
            await manager.broadcast_error(request.session_id, str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── Markdown Report ────────────────────────────────────────────────────────────
@app.get("/report/{startup_name}", response_class=PlainTextResponse)
async def get_report_md(startup_name: str):
    slug = re.sub(r"[^a-z0-9]+", "_", startup_name.lower()).strip("_")
    if not OUTPUTS_DIR.exists():
        raise HTTPException(status_code=404, detail="No reports found.")
    matches = sorted(OUTPUTS_DIR.glob(f"{slug}_report_*.md"),
                     key=lambda f: f.stat().st_mtime, reverse=True)
    if not matches:
        raise HTTPException(status_code=404,
            detail=f"No report found for '{startup_name}'. Run an analysis first.")
    return matches[0].read_text(encoding="utf-8")


# ── PDF Download ───────────────────────────────────────────────────────────────
@app.get("/report/{analysis_id}/pdf")
async def get_report_pdf(analysis_id: int):
    """Generate and return a branded PDF for a given analysis_id."""
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found.")

    result   = row["result"]
    markdown = ""
    if row.get("report_file") and Path(row["report_file"]).exists():
        markdown = Path(row["report_file"]).read_text(encoding="utf-8")

    pdf_bytes = generate_pdf(result, markdown_text=markdown)
    slug      = re.sub(r"[^a-z0-9]+", "_", row["startup_name"].lower()).strip("_")

    return Response(
        content     = pdf_bytes,
        media_type  = "application/pdf",
        headers     = {"Content-Disposition": f'attachment; filename="{slug}_venturelens.pdf"'},
    )


# ── History ────────────────────────────────────────────────────────────────────
@app.get("/history")
async def history(limit: int = 50):
    """Return list of past analyses, newest first."""
    rows = get_history(limit=limit)
    # Return lightweight cards (no full result_json)
    return [
        {
            "id":            r["id"],
            "startup_name":  r["startup_name"],
            "industry":      r["industry"],
            "stage":         r["stage"],
            "overall_score": r["overall_score"],
            "verdict":       r["verdict"],
            "created_at":    r["created_at"],
        }
        for r in rows
    ]


@app.get("/history/{analysis_id}")
async def history_detail(analysis_id: int):
    """Return full analysis result by id."""
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found.")
    return row