from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel
import re, os, json, uuid, logging
from collections import Counter

from models import AnalyzeRequest, AnalyzeResponse
from agents import run_pipeline
from websocket_manager import manager
from auth import require_auth
from services.db import (
    init_db, save_analysis, get_history, get_analysis_by_id,
    engine, Analysis, Session, select
)
from services.pdf_generator import generate_pdf
from services.news_service import fetch_company_news

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VentureLens")

OUTPUTS_DIR = Path(__file__).parent / "outputs"

app = FastAPI(title="VentureLens AI", version="0.7.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text(
                "ALTER TABLE analyses ADD COLUMN share_token TEXT"))
            conn.commit()
    except Exception:
        pass
    logger.info("Database initialized.")


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.7.0"}


# ── Metrics ────────────────────────────────────────────────────────────────────
@app.get("/metrics")
async def metrics():
    """Returns total analyses, average score, and verdict distribution."""
    rows = get_history(limit=1000)
    if not rows:
        return {"total": 0, "avg_score": 0, "verdict_distribution": {}, "top_industries": {}}

    total        = len(rows)
    avg_score    = round(sum(r["overall_score"] for r in rows) / total, 1)
    verdicts     = Counter(r["verdict"]   for r in rows)
    industries   = Counter(r["industry"]  for r in rows)

    return {
        "total":                total,
        "avg_score":            avg_score,
        "verdict_distribution": dict(verdicts.most_common()),
        "top_industries":       dict(industries.most_common(5)),
    }


# ── WebSocket ──────────────────────────────────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception:
        manager.disconnect(session_id)


# ── Analyze ────────────────────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_auth)])
async def analyze(request: AnalyzeRequest):
    logger.info(f"Analyzing: {request.startup_name}")
    try:
        result = await run_pipeline(
            startup_name=request.startup_name, industry=request.industry,
            description=request.description, stage=request.stage,
            session_id=request.session_id,
        )
        result_for_db = {**result, "industry": request.industry, "stage": request.stage}
        slug = re.sub(r"[^a-z0-9]+", "_", request.startup_name.lower()).strip("_")
        report_file = None
        if OUTPUTS_DIR.exists():
            matches = sorted(OUTPUTS_DIR.glob(f"{slug}_report_*.md"),
                             key=lambda f: f.stat().st_mtime, reverse=True)
            if matches:
                report_file = str(matches[0])
        analysis_id = save_analysis(result_for_db, report_file=report_file)
        if request.session_id:
            await manager.broadcast_result(request.session_id, {**result, "analysis_id": analysis_id})
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        if request.session_id:
            await manager.broadcast_error(request.session_id, str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── Markdown report ────────────────────────────────────────────────────────────
@app.get("/report/{startup_name}", response_class=PlainTextResponse)
async def get_report_md(startup_name: str):
    slug = re.sub(r"[^a-z0-9]+", "_", startup_name.lower()).strip("_")
    if not OUTPUTS_DIR.exists():
        raise HTTPException(status_code=404, detail="No reports found.")
    matches = sorted(OUTPUTS_DIR.glob(f"{slug}_report_*.md"),
                     key=lambda f: f.stat().st_mtime, reverse=True)
    if not matches:
        raise HTTPException(status_code=404, detail=f"No report found for '{startup_name}'.")
    return matches[0].read_text(encoding="utf-8")


# ── PDF ────────────────────────────────────────────────────────────────────────
@app.get("/report/{analysis_id}/pdf")
async def get_report_pdf(analysis_id: int):
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    result   = row["result"]
    markdown = ""
    if row.get("report_file") and Path(row["report_file"]).exists():
        markdown = Path(row["report_file"]).read_text(encoding="utf-8")
    pdf_bytes = generate_pdf(result, markdown_text=markdown)
    slug = re.sub(r"[^a-z0-9]+", "_", row["startup_name"].lower()).strip("_")
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{slug}_venturelens.pdf"'})


# ── History ────────────────────────────────────────────────────────────────────
@app.get("/history")
async def history(limit: int = 50):
    rows = get_history(limit=limit)
    return [{"id":r["id"],"startup_name":r["startup_name"],"industry":r["industry"],
             "stage":r["stage"],"overall_score":r["overall_score"],
             "verdict":r["verdict"],"created_at":r["created_at"]} for r in rows]

@app.get("/history/{analysis_id}")
async def history_detail(analysis_id: int):
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return row


# ── Competitors ────────────────────────────────────────────────────────────────
@app.get("/competitors/{analysis_id}")
async def get_competitors(analysis_id: int):
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    try:
        import google.generativeai as genai
        from agents.prompts import COMPETITOR_ANALYSIS_PROMPT
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model  = genai.GenerativeModel("gemini-2.5-flash")
        prompt = COMPETITOR_ANALYSIS_PROMPT.format(
            company_info    = row["result"].get("summary",""),
            market_analysis = f"Industry: {row['industry']}, Stage: {row['stage']}",
        )
        response    = model.generate_content(prompt)
        raw         = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE)
        competitors = json.loads(raw)
        return {"competitors": competitors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")


# ── News ───────────────────────────────────────────────────────────────────────
@app.get("/news/{startup_name}")
async def get_news(startup_name: str):
    articles = await fetch_company_news(startup_name)
    return {"articles": articles}


# ── Thesis ─────────────────────────────────────────────────────────────────────
class ThesisRequest(BaseModel):
    analysis_id: int

@app.post("/thesis")
async def generate_thesis(req: ThesisRequest):
    row = get_analysis_by_id(req.analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    try:
        import google.generativeai as genai
        from agents.prompts import THESIS_GENERATOR_PROMPT
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model  = genai.GenerativeModel("gemini-2.5-flash")
        result = row["result"]
        prompt = THESIS_GENERATOR_PROMPT.format(
            startup_name  = result["startup_name"],
            overall_score = result["overall_score"],
            verdict       = result["verdict"],
            summary       = result.get("summary",""),
            green_flags   = ", ".join(result.get("green_flags",[])),
            red_flags     = ", ".join(result.get("red_flags",[])),
            scores        = json.dumps(result.get("scores",{})),
        )
        response = model.generate_content(prompt)
        return {"thesis": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thesis failed: {str(e)}")


# ── Share ──────────────────────────────────────────────────────────────────────
@app.post("/share/{analysis_id}")
async def create_share_link(analysis_id: int):
    row = get_analysis_by_id(analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    token = str(uuid.uuid4())
    with Session(engine) as session:
        analysis = session.get(Analysis, analysis_id)
        analysis.share_token = token
        session.commit()
    base_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return {"share_url": f"{base_url}/share/{token}", "token": token}

@app.get("/share/{token}")
async def get_shared_report(token: str):
    with Session(engine) as session:
        row = session.execute(
            select(Analysis).where(Analysis.share_token == token)
        ).scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Share link not found.")
        from services.db import _row_to_dict
        return _row_to_dict(row)