"""
VentureLens AI — Custom ADK Tools
Tools that agents can call during the pipeline.
google_search is imported from google.adk.tools — defined here are custom ones.
"""

import logging
import json
import re
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("VentureLens.Tools")

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


# ── Tool: save_markdown_report ────────────────────────────────────────────────
async def save_markdown_report(
    startup_name: str,
    report_markdown: str,
) -> dict:
    """
    Saves the generated Markdown investment report to the outputs/ folder.

    Args:
        startup_name: Name of the startup being analyzed.
        report_markdown: Full Markdown content of the report.

    Returns:
        dict with file_path and status.
    """
    try:
        slug = re.sub(r"[^a-z0-9]+", "_", startup_name.lower()).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_report_{timestamp}.md"
        filepath = OUTPUTS_DIR / filename

        filepath.write_text(report_markdown, encoding="utf-8")
        logger.info(f"Report saved: {filepath}")

        return {
            "status": "success",
            "file_path": str(filepath),
            "filename": filename,
            "message": f"Report saved as {filename}",
        }
    except Exception as e:
        logger.error(f"save_markdown_report failed: {e}")
        return {"status": "error", "message": str(e)}


# ── Tool: parse_score_json ────────────────────────────────────────────────────
def parse_score_json(raw_json: str) -> dict:
    """
    Cleans and parses the JSON score card produced by the ScoringAgent.
    Strips markdown fences if present and validates required keys.

    Args:
        raw_json: Raw string output from the ScoringAgent.

    Returns:
        Parsed dict or error dict.
    """
    try:
        # Strip ```json ... ``` fences if present
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_json.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)

        required_keys = {"overall_score", "scores", "verdict", "summary", "green_flags", "red_flags"}
        missing = required_keys - data.keys()
        if missing:
            return {"status": "error", "message": f"Missing keys: {missing}"}

        return {"status": "ok", "data": data}
    except json.JSONDecodeError as e:
        logger.error(f"parse_score_json failed: {e}\nRaw: {raw_json[:300]}")
        return {"status": "error", "message": f"JSON parse error: {e}"}