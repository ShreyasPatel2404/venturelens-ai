from pydantic import BaseModel, Field
from typing import Literal


# ── Request ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    startup_name: str = Field(..., min_length=1, max_length=120, example="NovaPay")
    industry: str = Field(..., example="Fintech")
    description: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        example="A B2B payment infrastructure startup targeting SMEs in Southeast Asia.",
    )
    stage: Literal["idea", "pre-seed", "seed", "series-a", "series-b+"] = Field(
        default="seed"
    )
    pitch_deck_url: str | None = Field(
        default=None,
        description="Optional public URL to a pitch deck (PDF / Google Slides).",
        example="https://drive.google.com/file/d/xxx/view",
    )


# ── Sub-models ────────────────────────────────────────────────────────────────
class AnalyzeResponse(BaseModel):
    startup_name: str
    overall_score: int = Field(..., ge=0, le=100, description="Composite 0-100 score")
    summary: str
    scores: dict[str, int] = Field(
        ...,
        description="Dimension scores: market_opportunity, team_strength, product_differentiation, traction, financial_health",
    )
    verdict: Literal["STRONG BUY", "BUY", "PROMISING", "HOLD", "NEUTRAL", "RISKY", "PASS"]
    red_flags: list[str] = Field(default_factory=list)
    green_flags: list[str] = Field(default_factory=list)
    sources: list[str] = Field(
        default_factory=list,
        description="URLs or citations used by the agent (populated on DAY 2+)",
    )