from pydantic import BaseModel, Field
from typing import Literal, Optional


class AnalyzeRequest(BaseModel):
    startup_name: str = Field(..., min_length=1, max_length=120, example="NovaPay")
    industry: str = Field(..., example="Fintech")
    description: str = Field(..., min_length=20, max_length=2000,
        example="A B2B payment infrastructure startup targeting SMEs in Southeast Asia.")
    stage: Literal["idea", "pre-seed", "seed", "series-a", "series-b+"] = Field(default="seed")
    pitch_deck_url: Optional[str] = Field(default=None)
    # WebSocket session ID — frontend generates a UUID before calling /analyze
    session_id: Optional[str] = Field(default=None, example="abc-123")


class AnalyzeResponse(BaseModel):
    startup_name: str
    overall_score: int = Field(..., ge=0, le=100)
    summary: str
    scores: dict[str, int]
    # Expanded to cover all variants the LLM might return
    verdict: Literal["STRONG BUY", "BUY", "PROMISING", "HOLD", "NEUTRAL", "RISKY", "PASS"]
    red_flags: list[str] = Field(default_factory=list)
    green_flags: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)