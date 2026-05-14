from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

from models import AnalyzeRequest, AnalyzeResponse
from agents import run_pipeline
from websocket_manager import manager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VentureLens")

app = FastAPI(
    title="VentureLens AI",
    description="AI-powered startup due diligence — 7-agent Google ADK pipeline",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # broad for local dev — tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "venturelens-ai", "version": "0.3.0"}


# ── WebSocket endpoint ─────────────────────────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WS connecting: {session_id}")
    await manager.connect(session_id, websocket)
    try:
        while True:
            # Keep the connection alive; client sends nothing
            data = await websocket.receive_text()
            logger.debug(f"WS received (ignored): {data}")
    except WebSocketDisconnect:
        logger.info(f"WS disconnected: {session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        logger.warning(f"WS error for {session_id}: {e}")
        manager.disconnect(session_id)


# ── Analyze endpoint ───────────────────────────────────────────────────────────
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