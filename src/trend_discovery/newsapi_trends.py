"""
NewsAPI trend fetcher.
Pulls top headlines + everything endpoint filtered by niche keywords.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from src.utils.logger import log
from src.utils.retry import with_retry

NEWSAPI_BASE = "https://newsapi.org/v2"


class NewsAPITrendsFetcher:
    """
    Fetches trending news topics using the NewsAPI.

    Uses two endpoints:
    - /top-headlines: Breaking news by category.
    - /everything: Keyword-filtered search within lookback window.

    Returns dicts: {"topic": str, "source": "newsapi", "raw_score": int, "category": str}
    """

    # NewsAPI category → our niche mapping
    CATEGORY_MAP: dict[str, str] = {
        "technology": "technology",
        "science": "science",
        "business": "money",
        "health": "science",
        "entertainment": "shocking facts",
        "sports": "shocking facts",
        "general": "shocking facts",
    }

    def __init__(self, niches: list[str], lookback_hours: int = 24):
        """
        Args:
            niches: Configured niche list from config.yaml.
            lookback_hours: How far back to search for articles.
        """
        self.niches = niches
        self.lookback_hours = lookback_hours
        self.api_key = os.environ.get("NEWSAPI_KEY", "")

        if not self.api_key:
            log.warning("newsapi.init.no_api_key", message="NEWSAPI_KEY not set — NewsAPI fetcher disabled")

    def _is_available(self) -> bool:
        return bool(self.api_key)

    def _from_date(self) -> str:
        """Return ISO timestamp string for the lookback window."""
        dt = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _deduplicate(self, articles: list[dict]) -> list[dict]:
        """
        Simple keyword-overlap deduplication.
        Two articles are considered duplicates if they share ≥3 content words in their titles.
        """
        unique: list[dict] = []
        seen_word_sets: list[set[str]] = []
        stopwords = {"the", "a", "an", "in", "of", "to", "is", "was", "are", "for", "and", "or"}

        for article in articles:
            words = set(article.get("title", "").lower().split()) - stopwords
            is_dup = any(len(words & prev) >= 3 for prev in seen_word_sets)
            if not is_dup:
                unique.append(article)
                seen_word_sets.append(words)

        return unique

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(requests.RequestException, Exception))
    def _fetch_top_headlines(self, category: str) -> list[dict[str, Any]]:
        """
        Fetch top headlines for a NewsAPI category.

        Args:
            category: NewsAPI category string.

        Returns:
            List of trend dicts.
        """
        if not self._is_available():
            return []

        params = {
            "category": category,
            "language": "en",
            "pageSize": 20,
            "apiKey": self.api_key,
        }
        resp = requests.get(f"{NEWSAPI_BASE}/top-headlines", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        articles = data.get("articles", [])
        our_niche = self.CATEGORY_MAP.get(category, "general")

        results = []
        for idx, article in enumerate(articles):
            title = (article.get("title") or "").replace(" - " + (article.get("source", {}).get("name") or ""), "").strip()
            if not title or title == "[Removed]":
                continue
            results.append({
                "topic": title,
                "source": "newsapi",
                "raw_score": max(80 - idx * 2, 10),
                "category": our_niche,
                "url": article.get("url", ""),
            })

        log.info("newsapi.top_headlines.fetched", category=category, count=len(results))
        return results

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(requests.RequestException, Exception))
    def _fetch_keyword_search(self, keyword: str) -> list[dict[str, Any]]:
        """
        Search all articles for a niche keyword within the lookback window.

        Args:
            keyword: Niche keyword to search for.

        Returns:
            List of trend dicts.
        """
        if not self._is_available():
            return []

        params = {
            "q": keyword,
            "language": "en",
            "sortBy": "popularity",
            "from": self._from_date(),
            "pageSize": 20,
            "apiKey": self.api_key,
        }
        resp = requests.get(f"{NEWSAPI_BASE}/everything", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        articles = data.get("articles", [])
        results = []
        for idx, article in enumerate(articles):
            title = (article.get("title") or "").strip()
            if not title or title == "[Removed]":
                continue
            results.append({
                "topic": title,
                "source": "newsapi",
                "raw_score": max(70 - idx * 2, 10),
                "category": keyword,
                "url": article.get("url", ""),
            })

        log.info("newsapi.keyword_search.fetched", keyword=keyword, count=len(results))
        return results

    def fetch(self) -> list[dict[str, Any]]:
        """
        Run all NewsAPI fetchers and return deduplicated results.

        Returns:
            Combined list of unique trend dicts.
        """
        if not self._is_available():
            log.warning("newsapi.fetch.skipped", reason="No API key configured")
            return []

        all_articles: list[dict[str, Any]] = []

        # 1. Top headlines by category
        for category in self.CATEGORY_MAP:
            try:
                results = self._fetch_top_headlines(category)
                all_articles.extend(results)
            except Exception as exc:
                log.warning("newsapi.top_headlines.failed", category=category, error=str(exc))

        # 2. Keyword search per niche
        for niche in self.niches:
            try:
                results = self._fetch_keyword_search(niche)
                all_articles.extend(results)
            except Exception as exc:
                log.warning("newsapi.keyword_search.failed", niche=niche, error=str(exc))

        unique = self._deduplicate(all_articles)
        log.info("newsapi.fetch.complete", raw=len(all_articles), unique=len(unique))
        return unique
