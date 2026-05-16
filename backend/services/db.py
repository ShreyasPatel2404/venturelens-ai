"""
VentureLens AI — SQLite Database
Stores every completed analysis for history + comparison.
"""

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Text, DateTime, select
)
from sqlalchemy.orm import DeclarativeBase, Session

DB_PATH = Path(__file__).parent.parent / "venturelens.db"
engine  = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    startup_name   = Column(String(120), nullable=False, index=True)
    industry       = Column(String(80),  nullable=False)
    stage          = Column(String(30),  nullable=False)
    overall_score  = Column(Integer,     nullable=False)
    verdict        = Column(String(20),  nullable=False)
    summary        = Column(Text,        nullable=True)
    result_json    = Column(Text,        nullable=False)   # full AnalyzeResponse as JSON
    report_file    = Column(String(256), nullable=True)    # path to .md report in outputs/
    created_at     = Column(DateTime,   default=datetime.utcnow, nullable=False)


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)


def save_analysis(result: dict, report_file: str | None = None) -> int:
    """Persist a completed analysis. Returns the new row id."""
    with Session(engine) as session:
        row = Analysis(
            startup_name  = result["startup_name"],
            industry      = result.get("industry", ""),
            stage         = result.get("stage", ""),
            overall_score = result["overall_score"],
            verdict       = result["verdict"],
            summary       = result.get("summary", ""),
            result_json   = json.dumps(result),
            report_file   = report_file,
            created_at    = datetime.utcnow(),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row.id


def get_history(limit: int = 50) -> list[dict]:
    """Return recent analyses sorted newest-first."""
    with Session(engine) as session:
        rows = session.execute(
            select(Analysis).order_by(Analysis.created_at.desc()).limit(limit)
        ).scalars().all()
        return [_row_to_dict(r) for r in rows]


def get_analysis_by_id(analysis_id: int) -> dict | None:
    """Return one analysis by primary key, or None."""
    with Session(engine) as session:
        row = session.get(Analysis, analysis_id)
        return _row_to_dict(row) if row else None


def _row_to_dict(row: Analysis) -> dict:
    result = json.loads(row.result_json)
    return {
        "id":            row.id,
        "startup_name":  row.startup_name,
        "industry":      row.industry,
        "stage":         row.stage,
        "overall_score": row.overall_score,
        "verdict":       row.verdict,
        "summary":       row.summary,
        "report_file":   row.report_file,
        "created_at":    row.created_at.isoformat(),
        "result":        result,
    }