"""
Reddit trending topics fetcher using PRAW.
Scores posts by: upvote_ratio × log(upvotes) × recency_weight.
"""

import math
import os
import time
from datetime import datetime, timezone
from typing import Any

import praw
from praw.exceptions import PRAWException

from src.utils.logger import log
from src.utils.retry import with_retry

# Subreddit mapping per niche keyword
NICHE_SUBREDDITS: dict[str, list[str]] = {
    "technology": ["technology", "Futurology", "artificial", "MachineLearning"],
    "science": ["science", "space", "Physics", "biology"],
    "psychology": ["psychology", "todayilearned", "science", "neuroscience"],
    "money": ["personalfinance", "investing", "financialindependence", "stocks"],
    "history": ["history", "AskHistorians", "todayilearned", "HistoryMemes"],
    "shocking facts": ["todayilearned", "Damnthatsinteresting", "interestingasfuck", "coolguides"],
}

# Fallback subreddits when niche not in map
DEFAULT_SUBREDDITS = ["todayilearned", "Damnthatsinteresting", "interestingasfuck"]


class RedditTrendsFetcher:
    """
    Fetches trending content from Reddit for configured niches.

    Scoring formula:
        score = upvote_ratio × log10(max(upvotes, 1)) × recency_weight
        recency_weight = 1.0 for posts < 6h old, 0.7 for 6-12h, 0.5 for 12-24h
    """

    def __init__(self, niches: list[str], lookback_hours: int = 24):
        """
        Args:
            niches: List of niche strings from config.
            lookback_hours: Max age (hours) of posts to consider.
        """
        self.niches = niches
        self.lookback_hours = lookback_hours
        self._reddit: praw.Reddit | None = None

    def _get_client(self) -> praw.Reddit:
        """Lazy-initialize the PRAW Reddit client from environment variables."""
        if self._reddit is None:
            self._reddit = praw.Reddit(
                client_id=os.environ["REDDIT_CLIENT_ID"],
                client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                user_agent=os.getenv("REDDIT_USER_AGENT", "auto-shorts-engine/1.0"),
                ratelimit_seconds=300,
            )
            # Read-only mode — no login required
            self._reddit.read_only = True
        return self._reddit

    def _recency_weight(self, created_utc: float) -> float:
        """Return a recency multiplier based on post age."""
        age_hours = (time.time() - created_utc) / 3600
        if age_hours <= 6:
            return 1.0
        elif age_hours <= 12:
            return 0.7
        elif age_hours <= 24:
            return 0.5
        else:
            return 0.2

    def _score_post(self, post: praw.models.Submission) -> float:
        """
        Calculate a virality score for a single Reddit post.

        Args:
            post: PRAW Submission object.

        Returns:
            Float score (higher = more viral).
        """
        upvotes = max(post.score, 1)
        ratio = post.upvote_ratio
        recency = self._recency_weight(post.created_utc)
        return ratio * math.log10(upvotes) * recency * 100

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(PRAWException, Exception))
    def _fetch_subreddit(
        self, subreddit_name: str, category: str, limit: int = 25
    ) -> list[dict[str, Any]]:
        """
        Fetch hot and top posts from a single subreddit.

        Args:
            subreddit_name: Name of the subreddit (without r/).
            category: Niche category string for labeling.
            limit: Number of posts to fetch per listing.

        Returns:
            List of trend dicts.
        """
        reddit = self._get_client()
        subreddit = reddit.subreddit(subreddit_name)

        results: list[dict[str, Any]] = []
        cutoff_ts = time.time() - (self.lookback_hours * 3600)

        # Combine hot + top (day) for broader coverage
        post_generators = [
            subreddit.hot(limit=limit),
            subreddit.top(time_filter="day", limit=limit),
        ]

        seen_ids: set[str] = set()

        for generator in post_generators:
            for post in generator:
                if post.id in seen_ids:
                    continue
                if post.created_utc < cutoff_ts:
                    continue
                if post.is_self and not post.selftext:
                    # Skip link posts with no body unless they have high engagement
                    if post.score < 500:
                        continue

                seen_ids.add(post.id)
                raw_score = self._score_post(post)

                results.append({
                    "topic": post.title.strip(),
                    "source": "reddit",
                    "raw_score": round(min(raw_score, 100), 2),
                    "category": category,
                    "reddit_id": post.id,
                    "subreddit": subreddit_name,
                    "upvotes": post.score,
                })

        log.info(
            "reddit_trends.subreddit.fetched",
            subreddit=subreddit_name,
            count=len(results),
        )
        return results

    def fetch(self) -> list[dict[str, Any]]:
        """
        Fetch trending topics across all configured niches.

        Returns:
            Combined, deduplicated list of trend dicts.
        """
        all_results: list[dict[str, Any]] = []
        seen_topics: set[str] = set()

        for niche in self.niches:
            subreddits = NICHE_SUBREDDITS.get(niche.lower(), DEFAULT_SUBREDDITS)
            for sub in subreddits:
                try:
                    posts = self._fetch_subreddit(sub, category=niche)
                    for post in posts:
                        key = post["topic"].lower()[:80]  # normalize by first 80 chars
                        if key not in seen_topics:
                            seen_topics.add(key)
                            all_results.append(post)
                except Exception as exc:
                    log.warning(
                        "reddit_trends.subreddit.failed",
                        subreddit=sub,
                        niche=niche,
                        error=str(exc),
                    )

        log.info("reddit_trends.fetch.complete", total_topics=len(all_results))
        return all_results
