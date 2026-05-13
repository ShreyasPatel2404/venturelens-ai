"""
VentureLens AI — 7-Agent Due Diligence Pipeline
Uses Google ADK SequentialAgent pattern.
Each agent writes to an output_key; downstream agents read via {template_vars}.
"""

import os
import json
import logging
from typing import AsyncGenerator

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

# ── Model config ──────────────────────────────────────────────────────────────
# FLASH_MODEL = "gemini-2.0-flash"          # fast agents: research + report
# PRO_MODEL   = "gemini-2.0-flash"          # heavy reasoning (swap to gemini-1.5-pro if quota allows)
# NEW (works on free tier today)
FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL   = "gemini-2.5-flash"

APP_NAME    = "venturelens_ai"
USER_ID     = "venturelens_user"


# ── 1. Company Research Agent ─────────────────────────────────────────────────
company_research_agent = LlmAgent(
    name="CompanyResearchAgent",
    model=FLASH_MODEL,
    description="Researches company information using live web search",
    instruction=COMPANY_RESEARCH_PROMPT,
    tools=[google_search],
    output_key="company_info",
)

# ── 2. Market Analysis Agent ──────────────────────────────────────────────────
market_analysis_agent = LlmAgent(
    name="MarketAnalysisAgent",
    model=FLASH_MODEL,
    description="Analyzes market size, competitors, and positioning",
    instruction=MARKET_ANALYSIS_PROMPT,
    tools=[google_search],
    output_key="market_analysis",
)

# ── 3. Financial Modeling Agent ───────────────────────────────────────────────
financial_modeling_agent = LlmAgent(
    name="FinancialModelingAgent",
    model=PRO_MODEL,
    description="Builds Bear/Base/Bull revenue models and calculates returns",
    instruction=FINANCIAL_MODELING_PROMPT,
    output_key="financial_model",
)

# ── 4. Risk Assessment Agent ──────────────────────────────────────────────────
risk_assessment_agent = LlmAgent(
    name="RiskAssessmentAgent",
    model=PRO_MODEL,
    description="Deep risk analysis across 5 categories with severity scores",
    instruction=RISK_ASSESSMENT_PROMPT,
    output_key="risk_assessment",
)

# ── 5. Investor Memo Agent ────────────────────────────────────────────────────
investor_memo_agent = LlmAgent(
    name="InvestorMemoAgent",
    model=PRO_MODEL,
    description="Synthesizes all findings into a structured investment memo",
    instruction=INVESTOR_MEMO_PROMPT,
    output_key="investor_memo",
)

# ── 6. Report Generator Agent ─────────────────────────────────────────────────
report_generator_agent = LlmAgent(
    name="ReportGeneratorAgent",
    model=FLASH_MODEL,
    description="Converts memo to professional Markdown report and saves it",
    instruction=REPORT_GENERATOR_PROMPT,
    tools=[save_markdown_report],
    output_key="report_result",
)

# ── 7. Scoring Agent ──────────────────────────────────────────────────────────
scoring_agent = LlmAgent(
    name="ScoringAgent",
    model=FLASH_MODEL,
    description="Produces the final structured JSON score card",
    instruction=SCORING_AGENT_PROMPT,
    output_key="score_card_raw",
)

# ── SequentialAgent Pipeline ──────────────────────────────────────────────────
due_diligence_pipeline = SequentialAgent(
    name="DueDiligencePipeline",
    description=(
        "Full 7-stage VC due diligence: "
        "Research → Market → Financials → Risks → Memo → Report → Score"
    ),
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

# ── Root coordinator (ADK entry-point + FastAPI entry-point) ──────────────────
root_agent = LlmAgent(
    name="DueDiligenceAnalyst",
    model=FLASH_MODEL,
    description="VentureLens AI — senior investment analyst coordinator",
    instruction="""You are a senior investment analyst.
When the user provides a startup to analyze, immediately transfer to DueDiligencePipeline.
After the pipeline completes, summarize the key findings in 3 bullet points and
note that the full report has been saved to the outputs/ folder.
""",
    sub_agents=[due_diligence_pipeline],
)


# ── FastAPI-callable runner ───────────────────────────────────────────────────
async def run_pipeline(
    startup_name: str,
    industry: str,
    description: str,
    stage: str,
) -> dict:
    """
    Runs the full 7-agent pipeline and returns a structured result dict
    that maps directly to the AnalyzeResponse Pydantic model.

    Called by: backend/main.py  POST /analyze
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session = await session_service.create_session(
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

    final_state: dict = {}

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        ),
    ):
        # Capture session state after each agent writes its output_key
        if event.is_final_response():
            session_obj = await session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session.id,
            )
            final_state = session_obj.state or {}
            logger.info("Pipeline completed. Final state keys: %s", list(final_state.keys()))

    # ── Parse the score card JSON produced by ScoringAgent ────────────────────
    raw_score = final_state.get("score_card_raw", "")
    parsed = parse_score_json(raw_score)

    if parsed.get("status") == "ok":
        card = parsed["data"]
    else:
        logger.warning("Score card parse failed: %s", parsed.get("message"))
        # Fallback: build a minimal card from memo text
        card = _fallback_score_card(startup_name, final_state)

    return {
        "startup_name": startup_name,
        "overall_score": card.get("overall_score", 50),
        "summary": card.get("summary", "Analysis complete. See full report."),
        "scores": card.get("scores", {}),
        "verdict": card.get("verdict", "NEUTRAL"),
        "red_flags": card.get("red_flags", []),
        "green_flags": card.get("green_flags", []),
        "sources": card.get("sources", []),
    }


def _fallback_score_card(startup_name: str, state: dict) -> dict:
    """Minimal fallback when ScoringAgent JSON is unparseable."""
    return {
        "overall_score": 50,
        "scores": {
            "market_opportunity": 50,
            "team_strength": 50,
            "product_differentiation": 50,
            "traction": 50,
            "financial_health": 50,
        },
        "verdict": "NEUTRAL",
        "summary": (
            f"Analysis of {startup_name} completed. "
            "Score parsing encountered an issue — review the saved report for full details."
        ),
        "green_flags": [],
        "red_flags": ["Score card could not be parsed — check outputs/ for the full report."],
        "sources": [],
    }


# ── ADK discovery export ──────────────────────────────────────────────────────
# Required if you ever want to run `adk web` on this folder directly.
__all__ = ["root_agent", "run_pipeline"]