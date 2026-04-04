"""
Google Trends fetcher using pytrends with RSS fallback.
"""

import time
import xml.etree.ElementTree as ET
from typing import Any

import requests
from pytrends.request import TrendReq

from src.utils.logger import log
from src.utils.retry import with_retry

# Rate-limit: 5 requests/minute → 12s gap between requests
_REQUEST_INTERVAL = 12.0


class GoogleTrendsFetcher:
    """
    Fetches trending topics from Google Trends.

    Combines:
    - Real-time trending searches (geo-targeted: US + IN)
    - Related queries for each configured niche keyword

    Returns a list of dicts:
        {"topic": str, "source": "google_trends", "raw_score": int, "category": str}
    """

    RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    GEOS = ["US", "IN"]

    def __init__(self, niches: list[str], lookback_hours: int = 24):
        """
        Args:
            niches: List of niche keyword strings from config.
            lookback_hours: How far back to check for trends.
        """
        self.niches = niches
        self.lookback_hours = lookback_hours
        self._last_request_time: float = 0.0

    def _rate_limit(self) -> None:
        """Ensure at least _REQUEST_INTERVAL seconds between API calls."""
        elapsed = time.time() - self._last_request_time
        if elapsed < _REQUEST_INTERVAL:
            time.sleep(_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _build_pytrends(self) -> TrendReq:
        return TrendReq(hl="en-US", tz=330, timeout=(10, 25), retries=2, backoff_factor=0.5)

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,))
    def _fetch_trending_searches(self, geo: str) -> list[dict[str, Any]]:
        """
        Fetch daily trending searches for a given country code.

        Args:
            geo: ISO country code, e.g. "US" or "IN".

        Returns:
            List of trend dicts.
        """
        self._rate_limit()
        pytrends = self._build_pytrends()
        df = pytrends.trending_searches(pn=geo.lower() if geo == "IN" else "united_states")

        results: list[dict[str, Any]] = []
        if df is not None and not df.empty:
            for idx, row in df.iterrows():
                topic = str(row.iloc[0]).strip()
                if topic:
                    results.append({
                        "topic": topic,
                        "source": "google_trends",
                        "raw_score": max(90 - int(idx) * 2, 10),  # rank-based score
                        "category": "trending",
                        "geo": geo,
                    })

        log.info(
            "google_trends.trending_searches.fetched",
            geo=geo,
            count=len(results),
        )
        return results

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,))
    def _fetch_related_queries(self, keyword: str) -> list[dict[str, Any]]:
        """
        Fetch rising related queries for a niche keyword.

        Args:
            keyword: Niche keyword to query.

        Returns:
            List of trend dicts.
        """
        self._rate_limit()
        pytrends = self._build_pytrends()
        pytrends.build_payload([keyword], cat=0, timeframe="now 1-d", geo="", gprop="")
        related = pytrends.related_queries()

        results: list[dict[str, Any]] = []
        if related and keyword in related:
            rising_df = related[keyword].get("rising")
            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.iterrows():
                    topic = str(row.get("query", "")).strip()
                    raw_value = row.get("value", 50)
                    # "Breakout" topics come back as strings like "Breakout"
                    try:
                        score = min(int(raw_value), 100)
                    except (ValueError, TypeError):
                        score = 80  # Breakout = high virality
                    if topic:
                        results.append({
                            "topic": topic,
                            "source": "google_trends",
                            "raw_score": score,
                            "category": keyword,
                        })

        log.info(
            "google_trends.related_queries.fetched",
            keyword=keyword,
            count=len(results),
        )
        return results

    def _fetch_rss_fallback(self, geo: str) -> list[dict[str, Any]]:
        """
        Fallback: scrape Google Trends RSS feed directly.

        Args:
            geo: ISO country code.

        Returns:
            List of trend dicts.
        """
        url = self.RSS_URL.format(geo=geo)
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "auto-shorts-engine/1.0"})
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            results: list[dict[str, Any]] = []
            ns = {"ht": "https://trends.google.com/trends/trendingsearches/daily"}
            for idx, item in enumerate(root.findall(".//item")):
                title_el = item.find("title")
                if title_el is not None and title_el.text:
                    results.append({
                        "topic": title_el.text.strip(),
                        "source": "google_trends",
                        "raw_score": max(85 - idx * 3, 10),
                        "category": "trending",
                        "geo": geo,
                    })
                if len(results) >= 20:
                    break

            log.info("google_trends.rss_fallback.fetched", geo=geo, count=len(results))
            return results

        except Exception as exc:
            log.error("google_trends.rss_fallback.failed", geo=geo, error=str(exc))
            return []

    def fetch(self) -> list[dict[str, Any]]:
        """
        Run all fetchers and return a deduplicated list of trending topics.

        Returns:
            Combined list of trend dicts from trending searches + related queries.
        """
        all_results: list[dict[str, Any]] = []
        seen_topics: set[str] = set()

        # 1. Trending searches per geo
        for geo in self.GEOS:
            try:
                results = self._fetch_trending_searches(geo)
            except Exception as exc:
                log.warning(
                    "google_trends.trending_searches.failed",
                    geo=geo,
                    error=str(exc),
                )
                log.info("google_trends.falling_back_to_rss", geo=geo)
                results = self._fetch_rss_fallback(geo)

            for item in results:
                key = item["topic"].lower()
                if key not in seen_topics:
                    seen_topics.add(key)
                    all_results.append(item)

        # 2. Related queries per niche
        for niche in self.niches:
            try:
                results = self._fetch_related_queries(niche)
                for item in results:
                    key = item["topic"].lower()
                    if key not in seen_topics:
                        seen_topics.add(key)
                        all_results.append(item)
            except Exception as exc:
                log.warning(
                    "google_trends.related_queries.failed",
                    niche=niche,
                    error=str(exc),
                )

        log.info("google_trends.fetch.complete", total_topics=len(all_results))
        return all_results
