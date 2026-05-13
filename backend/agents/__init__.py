"""
VentureLens AI — Agents Package
Exports root_agent so `adk web` can discover this as a standalone agent app.
Also exports run_pipeline for FastAPI integration.
"""

from .pipeline import root_agent, run_pipeline

__all__ = ["root_agent", "run_pipeline"]