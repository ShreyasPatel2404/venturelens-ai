"""
VentureLens AI — News Service
Fetches the 5 latest news articles about a company using SerpAPI.
Set SERP_API_KEY in .env to enable. Falls back to empty list if not set.
Install: pip install google-search-results
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger("VentureLens.News")


async def fetch_company_news(company_name: str, num: int = 5) -> list[dict]:
    """
    Fetch latest news articles for a company.
    Returns list of {title, url, source, date, snippet}.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        logger.warning("SERP_API_KEY not set — returning empty news feed.")
        return []

    try:
        from serpapi import GoogleSearch   # pip install google-search-results

        search = GoogleSearch({
            "q":       f"{company_name} startup news",
            "tbm":     "nws",
            "num":     num,
            "api_key": api_key,
        })
        results = search.get_dict()
        articles = []

        for item in results.get("news_results", [])[:num]:
            articles.append({
                "title":   item.get("title", ""),
                "url":     item.get("link", ""),
                "source":  item.get("source", ""),
                "date":    item.get("date", ""),
                "snippet": item.get("snippet", ""),
            })

        return articles

    except ImportError:
        logger.error("serpapi not installed. Run: pip install google-search-results")
        return []
    except Exception as e:
        logger.error(f"News fetch failed for {company_name}: {e}")
        return []