from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

from models import AnalyzeRequest, AnalyzeResponse
from agents import run_pipeline

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VentureLens")

app = FastAPI(
    title="VentureLens AI",
    description="AI-powered startup due diligence — 7-agent Google ADK pipeline",
    version="0.2.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "venturelens-ai", "version": "0.2.0"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Runs the full 7-agent Google ADK due diligence pipeline.
    Typical latency: 60–120 seconds depending on web search depth.
    """
    logger.info(f"Starting analysis for: {request.startup_name}")
    try:
        result = await run_pipeline(
            startup_name=request.startup_name,
            industry=request.industry,
            description=request.description,
            stage=request.stage,
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Pipeline error for {request.startup_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")