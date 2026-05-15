from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from pathlib import Path
import re
import os
import logging

from models import AnalyzeRequest, AnalyzeResponse
from agents import run_pipeline
from websocket_manager import manager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VentureLens")

OUTPUTS_DIR = Path(__file__).parent / "outputs"

app = FastAPI(
    title="VentureLens AI",
    description="AI-powered startup due diligence — 7-agent Google ADK pipeline",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "venturelens-ai", "version": "0.4.0"}


# ── WebSocket ──────────────────────────────────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WS connecting: {session_id}")
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WS disconnected: {session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        logger.warning(f"WS error for {session_id}: {e}")
        manager.disconnect(session_id)


# ── Analyze ────────────────────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    logger.info(f"Starting analysis for: {request.startup_name} (session: {request.session_id})")
    try:
        result = await run_pipeline(
            startup_name=request.startup_name,
            industry=request.industry,
            description=request.description,
            stage=request.stage,
            session_id=request.session_id,
        )
        if request.session_id:
            await manager.broadcast_result(request.session_id, result)
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Pipeline error for {request.startup_name}: {e}", exc_info=True)
        if request.session_id:
            await manager.broadcast_error(request.session_id, str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── Report viewer ──────────────────────────────────────────────────────────────
@app.get("/report/{startup_name}", response_class=PlainTextResponse)
async def get_report(startup_name: str):
    """
    Returns the latest saved Markdown report for a given startup name.
    Matches files like: stripe_report_20260509_173738.md
    """
    slug = re.sub(r"[^a-z0-9]+", "_", startup_name.lower()).strip("_")

    if not OUTPUTS_DIR.exists():
        raise HTTPException(status_code=404, detail="No reports found yet.")

    # Find all matching report files, pick the most recent
    matches = sorted(
        OUTPUTS_DIR.glob(f"{slug}_report_*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for '{startup_name}'. Run an analysis first."
        )

    content = matches[0].read_text(encoding="utf-8")
    logger.info(f"Serving report: {matches[0].name}")
    return content