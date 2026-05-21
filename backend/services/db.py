"""
VentureLens AI — SQLite Database
Tables: users, analyses (user-scoped)
"""

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, select
)
from sqlalchemy.orm import DeclarativeBase, Session

DB_PATH = Path(__file__).parent.parent / "venturelens.db"
engine  = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


# ── Users table ────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    name          = Column(String(120), nullable=False, default="")
    password_hash = Column(String(255), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)


# ── Analyses table ─────────────────────────────────────────────────────────────
class Analysis(Base):
    __tablename__ = "analyses"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, nullable=True, index=True)   # nullable for backward compat
    startup_name  = Column(String(120), nullable=False, index=True)
    industry      = Column(String(80),  nullable=False)
    stage         = Column(String(30),  nullable=False)
    overall_score = Column(Integer,     nullable=False)
    verdict       = Column(String(20),  nullable=False)
    summary       = Column(Text,        nullable=True)
    result_json   = Column(Text,        nullable=False)
    report_file   = Column(String(256), nullable=True)
    share_token   = Column(String(36),  nullable=True, index=True)
    created_at    = Column(DateTime,    default=datetime.utcnow, nullable=False)


def init_db():
    Base.metadata.create_all(engine)
    # Add user_id column to existing analyses table if upgrading
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text(
                "ALTER TABLE analyses ADD COLUMN user_id INTEGER"))
            conn.commit()
    except Exception:
        pass  # Column already exists


# ── User CRUD ──────────────────────────────────────────────────────────────────
def create_user(email: str, name: str, password_hash: str) -> dict:
    with Session(engine) as session:
        user = User(email=email, name=name, password_hash=password_hash,
                    created_at=datetime.utcnow())
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "email": user.email, "name": user.name}

def get_user_by_email(email: str) -> dict | None:
    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.email == email.lower().strip())
        ).scalar_one_or_none()
        if not user:
            return None
        return {"id": user.id, "email": user.email,
                "name": user.name, "password_hash": user.password_hash}

def get_user_by_id(user_id: int) -> dict | None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        return {"id": user.id, "email": user.email, "name": user.name}


# ── Analysis CRUD ──────────────────────────────────────────────────────────────
def save_analysis(result: dict, report_file: str | None = None,
                  user_id: int | None = None) -> int:
    with Session(engine) as session:
        row = Analysis(
            user_id       = user_id,
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


def get_history(limit: int = 50, user_id: int | None = None) -> list[dict]:
    """Returns analyses for a specific user (or all if user_id is None)."""
    with Session(engine) as session:
        q = select(Analysis).order_by(Analysis.created_at.desc()).limit(limit)
        if user_id is not None:
            q = select(Analysis).where(
                Analysis.user_id == user_id
            ).order_by(Analysis.created_at.desc()).limit(limit)
        rows = session.execute(q).scalars().all()
        return [_row_to_dict(r) for r in rows]


def get_analysis_by_id(analysis_id: int, user_id: int | None = None) -> dict | None:
    """Returns analysis only if it belongs to the user (or no user check if None)."""
    with Session(engine) as session:
        row = session.get(Analysis, analysis_id)
        if not row:
            return None
        # If user_id provided, enforce ownership
        if user_id is not None and row.user_id is not None and row.user_id != user_id:
            return None
        return _row_to_dict(row)


def _row_to_dict(row: Analysis) -> dict:
    result = json.loads(row.result_json)
    return {
        "id":            row.id,
        "user_id":       row.user_id,
        "startup_name":  row.startup_name,
        "industry":      row.industry,
        "stage":         row.stage,
        "overall_score": row.overall_score,
        "verdict":       row.verdict,
        "summary":       row.summary,
        "report_file":   row.report_file,
        "share_token":   row.share_token,
        "created_at":    row.created_at.isoformat(),
        "result":        result,
    }