"""
VentureLens AI — 7-Agent Due Diligence Pipeline
Uses Google ADK SequentialAgent pattern.
Now emits real-time WebSocket progress events after each agent completes.
Auto-retries on 502/503 Google server errors (up to 3 attempts).
"""

import asyncio
import os
import json
import logging
from typing import Optional

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

from .prompts import (
    COMPANY_RESEARCH_PROMPT,
    MARKET_ANALYSIS_PROMPT,
    FINANCIAL_MODELING_PROMPT,
    RISK_ASSESSMENT_PROMPT,
    INVESTOR_MEMO_PROMPT,
    REPORT_GENERATOR_PROMPT,
    SCORING_AGENT_PROMPT,
)
from .tools import save_markdown_report, parse_score_json

logger = logging.getLogger("VentureLens.Pipeline")

FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL   = "gemini-2.5-flash"

APP_NAME = "venturelens_ai"
USER_ID  = "venturelens_user"

# Stage metadata — order must match SequentialAgent sub_agents order
STAGES = [
    ("company_info",    "CompanyResearchAgent",   "Researching company profile & funding history"),
    ("market_analysis", "MarketAnalysisAgent",    "Analyzing market size & competitive landscape"),
    ("financial_model", "FinancialModelingAgent", "Building Bear/Base/Bull financial models"),
    ("risk_assessment", "RiskAssessmentAgent",    "Assessing risks across 5 categories"),
    ("investor_memo",   "InvestorMemoAgent",      "Writing investment committee memo"),
    ("report_result",   "ReportGeneratorAgent",   "Generating professional report"),
    ("score_card_raw",  "ScoringAgent",           "Computing final investment score"),
]

# ── Agent definitions ──────────────────────────────────────────────────────────
company_research_agent = LlmAgent(
    name="CompanyResearchAgent",
    model=FLASH_MODEL,
    description="Researches company information using live web search",
    instruction=COMPANY_RESEARCH_PROMPT,
    tools=[google_search],
    output_key="company_info",
)

market_analysis_agent = LlmAgent(
    name="MarketAnalysisAgent",
    model=FLASH_MODEL,
    description="Analyzes market size, competitors, and positioning",
    instruction=MARKET_ANALYSIS_PROMPT,
    tools=[google_search],
    output_key="market_analysis",
)

financial_modeling_agent = LlmAgent(
    name="FinancialModelingAgent",
    model=PRO_MODEL,
    description="Builds Bear/Base/Bull revenue models",
    instruction=FINANCIAL_MODELING_PROMPT,
    output_key="financial_model",
)

risk_assessment_agent = LlmAgent(
    name="RiskAssessmentAgent",
    model=PRO_MODEL,
    description="Deep risk analysis across 5 categories",
    instruction=RISK_ASSESSMENT_PROMPT,
    output_key="risk_assessment",
)

investor_memo_agent = LlmAgent(
    name="InvestorMemoAgent",
    model=PRO_MODEL,
    description="Synthesizes all findings into a structured investment memo",
    instruction=INVESTOR_MEMO_PROMPT,
    output_key="investor_memo",
)

report_generator_agent = LlmAgent(
    name="ReportGeneratorAgent",
    model=FLASH_MODEL,
    description="Converts memo to professional Markdown report",
    instruction=REPORT_GENERATOR_PROMPT,
    tools=[save_markdown_report],
    output_key="report_result",
)

scoring_agent = LlmAgent(
    name="ScoringAgent",
    model=FLASH_MODEL,
    description="Produces the final structured JSON score card",
    instruction=SCORING_AGENT_PROMPT,
    output_key="score_card_raw",
)

due_diligence_pipeline = SequentialAgent(
    name="DueDiligencePipeline",
    description="Full 7-stage VC due diligence pipeline",
    sub_agents=[
        company_research_agent,
        market_analysis_agent,
        financial_modeling_agent,
        risk_assessment_agent,
        investor_memo_agent,
        report_generator_agent,
        scoring_agent,
    ],
)

root_agent = LlmAgent(
    name="DueDiligenceAnalyst",
    model=FLASH_MODEL,
    description="VentureLens AI — senior investment analyst coordinator",
    instruction="""You are a senior investment analyst.
When the user provides a startup to analyze, immediately transfer to DueDiligencePipeline.
After the pipeline completes, summarize the key findings in 3 bullet points.
""",
    sub_agents=[due_diligence_pipeline],
)


# ── FastAPI-callable runner ────────────────────────────────────────────────────
async def run_pipeline(
    startup_name: str,
    industry: str,
    description: str,
    stage: str,
    session_id: Optional[str] = None,
) -> dict:
    """
    Runs the full 7-agent pipeline.
    If session_id provided, emits WebSocket progress events in real-time.
    Auto-retries up to 3 times on 502/503 Google server errors.
    """
    from websocket_manager import manager

    async def emit(stage_key: str, status: str, message: str = ""):
        if session_id:
            await manager.broadcast_progress(session_id, stage_key, status, message)

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    adk_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    user_message = (
        f"Analyze this startup for investment due diligence:\n\n"
        f"Name: {startup_name}\n"
        f"Industry: {industry}\n"
        f"Stage: {stage}\n"
        f"Description: {description}"
    )

    # Emit initial "waiting" for all stages so frontend renders the full stepper
    for key, _, msg in STAGES:
        await emit(key, "waiting", msg)

    # Mark first stage running
    await emit(STAGES[0][0], "running", STAGES[0][2])

    seen_keys: set = set()

    # ── Runner loop with 502/503 retry ────────────────────────────────────────
    for attempt in range(3):
        try:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=adk_session.id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)],
                ),
            ):
                # Poll session state after every event to detect newly completed stages
                try:
                    snap = await session_service.get_session(
                        app_name=APP_NAME,
                        user_id=USER_ID,
                        session_id=adk_session.id,
                    )
                    current_state = snap.state or {}
                except Exception:
                    current_state = {}

                for idx, (key, agent_name, msg) in enumerate(STAGES):
                    if key in current_state and key not in seen_keys:
                        seen_keys.add(key)
                        await emit(key, "done", f"{agent_name} complete")
                        logger.info(f"Stage done: {key}")
                        if idx + 1 < len(STAGES):
                            nk, _, nm = STAGES[idx + 1]
                            await emit(nk, "running", nm)

            # Success — exit retry loop
            break

        except Exception as e:
            err_str = str(e)
            is_retryable = "502" in err_str or "503" in err_str or "500" in err_str

            if is_retryable and attempt < 2:
                wait = 30 * (attempt + 1)   # 30s on first retry, 60s on second
                logger.warning(
                    f"Google server error (attempt {attempt + 1}/3). "
                    f"Retrying in {wait}s... Error: {err_str[:120]}"
                )
                await emit(
                    STAGES[0][0], "running",
                    f"Server busy — retrying in {wait}s (attempt {attempt + 2}/3)..."
                )
                await asyncio.sleep(wait)
                # Reset seen_keys so stage tracking works on retry
                seen_keys = set()
                await emit(STAGES[0][0], "running", STAGES[0][2])
                continue

            # Non-retryable error or out of attempts — re-raise
            raise

    # ── Read final state ───────────────────────────────────────────────────────
    try:
        final_snap = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=adk_session.id,
        )
        final_state = final_snap.state or {}
    except Exception:
        final_state = {}

    logger.info("Pipeline done. Keys: %s", list(final_state.keys()))

    raw_score = final_state.get("score_card_raw", "")
    parsed = parse_score_json(raw_score)
    card = parsed["data"] if parsed.get("status") == "ok" else _fallback_score_card(startup_name)

    return {
        "startup_name": startup_name,
        "overall_score": card.get("overall_score", 50),
        "summary": card.get("summary", "Analysis complete."),
        "scores": card.get("scores", {}),
        "verdict": _safe_verdict(card.get("verdict", "NEUTRAL")),
        "red_flags": card.get("red_flags", []),
        "green_flags": card.get("green_flags", []),
        "sources": card.get("sources", []),
    }


def _safe_verdict(v: str) -> str:
    allowed = {"STRONG BUY", "BUY", "PROMISING", "HOLD", "NEUTRAL", "RISKY", "PASS"}
    v = str(v).strip().upper()
    if v in allowed:
        return v
    if "STRONG" in v:  return "STRONG BUY"
    if "BUY" in v:     return "BUY"
    if "PASS" in v or "AVOID" in v: return "PASS"
    if "RISK" in v:    return "RISKY"
    return "NEUTRAL"


def _fallback_score_card(startup_name: str) -> dict:
    return {
        "overall_score": 50,
        "scores": {k: 50 for k in ["market_opportunity", "team_strength",
                                    "product_differentiation", "traction", "financial_health"]},
        "verdict": "NEUTRAL",
        "summary": f"Analysis of {startup_name} completed. Review the saved report for full details.",
        "green_flags": [],
        "red_flags": ["Score card parsing encountered an issue — check outputs/ for the full report."],
        "sources": [],
    }


__all__ = ["root_agent", "run_pipeline"]