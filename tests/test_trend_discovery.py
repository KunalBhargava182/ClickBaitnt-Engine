"""
Tests for Phase 2: Trend Discovery module.

Run with: python -m pytest tests/test_trend_discovery.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  TrendScorer tests (no network, no API keys required)               #
# ------------------------------------------------------------------ #

class TestTrendScorer:
    def _make_scorer(self, tmp_path: Path):
        from src.trend_discovery.trend_scorer import TrendScorer

        return TrendScorer(
            niches=["technology", "science"],
            blacklist=["politics", "religion", "war"],
            min_trend_score=30,  # low threshold for testing
            history_path=tmp_path / "history.json",
        )

    def _sample_topics(self) -> list[dict]:
        return [
            {"topic": "AI Breakthrough", "source": "google_trends", "raw_score": 90, "category": "technology"},
            {"topic": "AI Breakthrough", "source": "reddit", "raw_score": 85, "category": "technology"},
            {"topic": "AI Breakthrough", "source": "newsapi", "raw_score": 80, "category": "technology"},
            {"topic": "Space Discovery", "source": "google_trends", "raw_score": 70, "category": "science"},
            {"topic": "politics drama", "source": "newsapi", "raw_score": 95, "category": "general"},
            {"topic": "Cheap topic", "source": "reddit", "raw_score": 10, "category": "general"},
        ]

    def test_multi_source_bonus(self, tmp_path):
        """Topic appearing in 3 sources gets 2x bonus."""
        scorer = self._make_scorer(tmp_path)
        topics = self._sample_topics()
        top = scorer.get_top_topics(topics, top_n=5)
        # AI Breakthrough appears in 3 sources — should be #1
        assert top[0]["topic"] == "AI Breakthrough"
        assert top[0]["source_count"] == 3

    def test_blacklist_filtering(self, tmp_path):
        """Politics should be filtered out regardless of score."""
        scorer = self._make_scorer(tmp_path)
        topics = self._sample_topics()
        top = scorer.get_top_topics(topics, top_n=10)
        topics_returned = [t["topic"].lower() for t in top]
        assert not any("politics" in t for t in topics_returned)

    def test_history_dedup(self, tmp_path):
        """Once a topic is added to history, it shouldn't appear again."""
        scorer = self._make_scorer(tmp_path)
        topics = self._sample_topics()

        first = scorer.get_top_topic(topics)
        assert first is not None
        chosen = first["topic"]

        # Run again — chosen topic should not reappear
        second_batch = scorer.get_top_topics(topics, top_n=10)
        returned = [t["topic"] for t in second_batch]
        assert chosen not in returned

    def test_history_persistence(self, tmp_path):
        """History is saved to disk and reloaded correctly."""
        history_path = tmp_path / "history.json"
        scorer = self._make_scorer(tmp_path)
        scorer.add_to_history("Test Topic", 75.0, "google_trends")

        # Create new instance pointing to same file
        from src.trend_discovery.trend_scorer import TrendScorer
        scorer2 = TrendScorer(
            niches=["technology"],
            blacklist=[],
            min_trend_score=0,
            history_path=history_path,
        )
        assert scorer2._is_in_history("Test Topic")

    def test_composite_score_capped_at_100(self, tmp_path):
        """Composite scores should never exceed 100."""
        scorer = self._make_scorer(tmp_path)
        topics = [
            {"topic": "Mega Viral Topic", "source": "google_trends", "raw_score": 100, "category": "technology"},
            {"topic": "Mega Viral Topic", "source": "reddit", "raw_score": 100, "category": "technology"},
            {"topic": "Mega Viral Topic", "source": "newsapi", "raw_score": 100, "category": "technology"},
        ]
        top = scorer.get_top_topics(topics, top_n=1)
        assert top[0]["trend_score"] <= 100.0

    def test_empty_input(self, tmp_path):
        """Empty input returns empty list gracefully."""
        scorer = self._make_scorer(tmp_path)
        result = scorer.get_top_topics([], top_n=5)
        assert result == []


# ------------------------------------------------------------------ #
#  TopicFilter tests                                                   #
# ------------------------------------------------------------------ #

class TestTopicFilter:
    def _make_filter(self, use_llm: bool = False):
        from src.trend_discovery.topic_filter import TopicFilter
        return TopicFilter(
            blacklist=["politics", "religion", "war", "nsfw"],
            use_llm=use_llm,
        )

    def test_blacklist_blocks(self):
        f = self._make_filter()
        approved, reason = f.is_approved("war in ukraine latest news")
        assert not approved
        assert reason == "blacklisted"

    def test_clean_topic_passes(self):
        f = self._make_filter()
        approved, reason = f.is_approved("Amazing space discoveries in 2024")
        assert approved

    def test_filter_list(self):
        f = self._make_filter()
        topics = [
            {"topic": "Amazing AI Technology"},
            {"topic": "Debate about religion in schools"},   # contains "religion"
            {"topic": "Space Telescope Discoveries"},
            {"topic": "war crimes exposed"},                 # contains "war"
        ]
        result = f.filter_topics(topics)
        assert len(result) == 2
        returned = [t["topic"] for t in result]
        assert "Amazing AI Technology" in returned
        assert "Space Telescope Discoveries" in returned

    @patch("src.trend_discovery.topic_filter.TopicFilter._llm_classify")
    def test_llm_unsafe_blocks(self, mock_classify):
        mock_classify.return_value = {"safe": False, "visual_richness": 8}
        f = self._make_filter(use_llm=True)
        approved, reason = f.is_approved("some sensitive topic")
        assert not approved
        assert reason == "llm_unsafe"

    @patch("src.trend_discovery.topic_filter.TopicFilter._llm_classify")
    def test_llm_low_visual_richness_blocks(self, mock_classify):
        mock_classify.return_value = {"safe": True, "visual_richness": 2}
        f = self._make_filter(use_llm=True)
        approved, reason = f.is_approved("Pure abstract mathematics theory")
        assert not approved
        assert "low_visual_richness" in reason

    @patch("src.trend_discovery.topic_filter.TopicFilter._llm_classify")
    def test_llm_failure_allows_through(self, mock_classify):
        mock_classify.side_effect = Exception("API timeout")
        f = self._make_filter(use_llm=True)
        approved, reason = f.is_approved("Some topic")
        assert approved  # Fail-open: don't block on LLM errors


# ------------------------------------------------------------------ #
#  Google Trends fetcher (mocked network)                             #
# ------------------------------------------------------------------ #

class TestGoogleTrendsFetcher:
    @patch("src.trend_discovery.google_trends.TrendReq")
    def test_fetch_returns_list(self, mock_trend_req_class):
        """Fetcher returns a list of dicts with required keys."""
        from src.trend_discovery.google_trends import GoogleTrendsFetcher
        import pandas as pd

        # Mock trending_searches response
        mock_pytrends = MagicMock()
        mock_pytrends.trending_searches.return_value = pd.DataFrame(["AI Tools", "Space News", "Python Tips"])
        mock_pytrends.related_queries.return_value = {}
        mock_trend_req_class.return_value = mock_pytrends

        fetcher = GoogleTrendsFetcher(niches=["technology"])
        results = fetcher._fetch_trending_searches("US")

        assert isinstance(results, list)
        if results:
            required_keys = {"topic", "source", "raw_score", "category"}
            assert required_keys.issubset(results[0].keys())
            assert results[0]["source"] == "google_trends"

    def test_rss_fallback_parses_xml(self):
        """RSS fallback returns valid results from well-formed XML."""
        from src.trend_discovery.google_trends import GoogleTrendsFetcher

        sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <item><title>AI Robots Now Everywhere</title></item>
            <item><title>New Planet Discovered</title></item>
          </channel>
        </rss>"""

        fetcher = GoogleTrendsFetcher(niches=["technology"])

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = sample_rss.encode("utf-8")
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            results = fetcher._fetch_rss_fallback("US")

        assert len(results) == 2
        assert results[0]["topic"] == "AI Robots Now Everywhere"
        assert results[0]["source"] == "google_trends"


# ------------------------------------------------------------------ #
#  Reddit fetcher (mocked PRAW)                                       #
# ------------------------------------------------------------------ #

class TestRedditTrendsFetcher:
    def _make_mock_post(self, title: str, score: int = 1000, ratio: float = 0.95, age_hours: float = 2.0):
        import time
        post = MagicMock()
        post.id = title[:10].replace(" ", "_")
        post.title = title
        post.score = score
        post.upvote_ratio = ratio
        post.created_utc = time.time() - (age_hours * 3600)
        post.is_self = True
        post.selftext = "body text"
        return post

    @patch("praw.Reddit")
    def test_fetch_returns_correct_format(self, mock_reddit_class):
        from src.trend_discovery.reddit_trends import RedditTrendsFetcher

        mock_reddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        posts = [
            self._make_mock_post("Amazing New AI Model Released", score=5000),
            self._make_mock_post("Scientists Discover New Element", score=3000),
        ]
        mock_subreddit.hot.return_value = iter(posts)
        mock_subreddit.top.return_value = iter([])

        fetcher = RedditTrendsFetcher(niches=["technology"])
        fetcher._reddit = mock_reddit

        results = fetcher._fetch_subreddit("technology", category="technology")

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["source"] == "reddit"
        assert "topic" in results[0]
        assert "raw_score" in results[0]

    def test_score_formula(self):
        """Score formula produces positive values; capping to 100 happens in _fetch_subreddit."""
        import time
        from src.trend_discovery.reddit_trends import RedditTrendsFetcher

        fetcher = RedditTrendsFetcher(niches=["technology"])

        post = MagicMock()
        post.score = 10000
        post.upvote_ratio = 0.98
        post.created_utc = time.time() - 3600  # 1h old

        score = fetcher._score_post(post)
        # Raw score is uncapped — cap applied downstream in _fetch_subreddit
        assert score > 0

        # Low-engagement post scores lower than high-engagement post
        low_post = MagicMock()
        low_post.score = 10
        low_post.upvote_ratio = 0.5
        low_post.created_utc = time.time() - 3600

        assert fetcher._score_post(low_post) < score


# ------------------------------------------------------------------ #
#  NewsAPI fetcher (mocked HTTP)                                       #
# ------------------------------------------------------------------ #

class TestNewsAPITrendsFetcher:
    def _sample_response(self) -> dict:
        return {
            "status": "ok",
            "articles": [
                {"title": "Tech Giant Announces AI Breakthrough", "url": "https://example.com/1",
                 "source": {"name": "TechCrunch"}},
                {"title": "Space Agency Plans Mars Mission", "url": "https://example.com/2",
                 "source": {"name": "NASA News"}},
                {"title": "[Removed]", "url": "", "source": {"name": ""}},  # Should be filtered
            ]
        }

    @patch.dict(os.environ, {"NEWSAPI_KEY": "test_key_12345"})
    @patch("requests.get")
    def test_fetch_top_headlines(self, mock_get):
        from src.trend_discovery.newsapi_trends import NewsAPITrendsFetcher

        mock_resp = MagicMock()
        mock_resp.json.return_value = self._sample_response()
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        fetcher = NewsAPITrendsFetcher(niches=["technology"])
        results = fetcher._fetch_top_headlines("technology")

        # [Removed] should be filtered
        assert len(results) == 2
        assert results[0]["source"] == "newsapi"
        assert results[0]["topic"] == "Tech Giant Announces AI Breakthrough"

    def test_deduplication(self):
        from src.trend_discovery.newsapi_trends import NewsAPITrendsFetcher

        fetcher = NewsAPITrendsFetcher(niches=["technology"])
        articles = [
            {"title": "AI Model Breaks Records in New Benchmark Test"},
            {"title": "AI Model Breaks Records in New Benchmark Study"},  # near-duplicate
            {"title": "Space Probe Reaches Jupiter"},
        ]
        unique = fetcher._deduplicate(articles)
        assert len(unique) == 2

    @patch.dict(os.environ, {"NEWSAPI_KEY": ""})
    def test_skips_when_no_key(self):
        from src.trend_discovery.newsapi_trends import NewsAPITrendsFetcher

        fetcher = NewsAPITrendsFetcher(niches=["technology"])
        results = fetcher.fetch()
        assert results == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
