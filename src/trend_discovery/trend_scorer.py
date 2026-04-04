"""
Aggregates, scores, deduplicates, and ranks topics from all trend sources.
"""

import json
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

from src.utils.logger import log

# Multi-source bonus multipliers
MULTI_SOURCE_BONUS = {1: 1.0, 2: 1.5, 3: 2.0}

# Similarity threshold for fuzzy dedup (0-1, higher = stricter)
SIMILARITY_THRESHOLD = 0.70


def _similarity(a: str, b: str) -> float:
    """Return fuzzy similarity ratio between two strings (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _is_duplicate(topic: str, existing: list[str], threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """Check if topic is too similar to any existing topic."""
    return any(_similarity(topic, e) >= threshold for e in existing)


class TrendScorer:
    """
    Aggregates trend data from multiple sources and produces a ranked list.

    Composite score formula:
        base_score = average raw_score across sources where topic appeared
        multi_bonus = 1.0 / 1.5 / 2.0 depending on source count
        final_score = min(base_score × multi_bonus, 100)

    History deduplication prevents the same topic from appearing within
    lookback_hours of a previous use.
    """

    def __init__(
        self,
        niches: list[str],
        blacklist: list[str],
        min_trend_score: float,
        history_path: Optional[Path] = None,
    ):
        """
        Args:
            niches: Configured niche list (for niche relevance bonus).
            blacklist: Keywords to filter out unconditionally.
            min_trend_score: Minimum composite score threshold (0-100).
            history_path: Path to topics_history.json for dedup tracking.
        """
        self.niches = [n.lower() for n in niches]
        self.blacklist = [b.lower() for b in blacklist]
        self.min_trend_score = min_trend_score

        if history_path is None:
            history_path = Path(__file__).resolve().parents[2] / "data" / "topics_history.json"
        self.history_path = history_path
        self._history: list[dict[str, Any]] = self._load_history()

    # ------------------------------------------------------------------ #
    #  History management                                                  #
    # ------------------------------------------------------------------ #

    def _load_history(self) -> list[dict[str, Any]]:
        """Load topics history JSON. Returns empty list if file absent."""
        if self.history_path.exists():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                log.warning("trend_scorer.history.load_error", error=str(exc))
        return []

    def _save_history(self) -> None:
        """Persist history to disk."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            log.error("trend_scorer.history.save_error", error=str(exc))

    def _is_in_history(self, topic: str) -> bool:
        """Return True if topic (fuzzy matched) is already in history."""
        known = [h["topic"] for h in self._history]
        return _is_duplicate(topic, known, threshold=SIMILARITY_THRESHOLD)

    def add_to_history(self, topic: str, score: float, source: str) -> None:
        """
        Record a topic as used.

        Args:
            topic: The selected topic string.
            score: Composite score at time of selection.
            source: Primary source label.
        """
        self._history.append({
            "topic": topic,
            "score": score,
            "source": source,
            "used_at": datetime.now(timezone.utc).isoformat(),
        })
        # Keep last 500 entries to prevent unbounded growth
        self._history = self._history[-500:]
        self._save_history()
        log.info("trend_scorer.history.added", topic=topic)

    # ------------------------------------------------------------------ #
    #  Filtering                                                           #
    # ------------------------------------------------------------------ #

    def _passes_blacklist(self, topic: str) -> bool:
        topic_lower = topic.lower()
        return not any(bad in topic_lower for bad in self.blacklist)

    def _niche_relevance(self, category: str) -> float:
        """Return 1.2 if the category matches a configured niche, else 1.0."""
        return 1.2 if any(n in category.lower() for n in self.niches) else 1.0

    # ------------------------------------------------------------------ #
    #  Aggregation & scoring                                               #
    # ------------------------------------------------------------------ #

    def _aggregate(self, all_topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Group duplicates (fuzzy match), compute composite scores.

        Args:
            all_topics: Raw combined list from all fetchers.

        Returns:
            List of aggregated topic dicts with composite_score.
        """
        groups: list[dict[str, Any]] = []

        for item in all_topics:
            topic = item["topic"].strip()
            if not topic:
                continue

            # Find matching group
            matched = None
            for group in groups:
                if _similarity(topic, group["canonical_topic"]) >= SIMILARITY_THRESHOLD:
                    matched = group
                    break

            if matched:
                matched["sources"].add(item["source"])
                matched["raw_scores"].append(item["raw_score"])
                # Keep highest-scoring category
                if item["raw_score"] > matched.get("best_raw", 0):
                    matched["best_raw"] = item["raw_score"]
                    matched["category"] = item.get("category", "general")
            else:
                groups.append({
                    "canonical_topic": topic,
                    "sources": {item["source"]},
                    "raw_scores": [item["raw_score"]],
                    "best_raw": item["raw_score"],
                    "category": item.get("category", "general"),
                })

        # Compute composite scores
        scored: list[dict[str, Any]] = []
        for group in groups:
            n_sources = len(group["sources"])
            bonus = MULTI_SOURCE_BONUS.get(min(n_sources, 3), 2.0)
            avg_raw = sum(group["raw_scores"]) / len(group["raw_scores"])
            niche_rel = self._niche_relevance(group["category"])
            composite = min(avg_raw * bonus * niche_rel, 100.0)

            scored.append({
                "topic": group["canonical_topic"],
                "source": " + ".join(sorted(group["sources"])),
                "primary_source": sorted(group["sources"])[0],
                "category": group["category"],
                "trend_score": round(composite, 2),
                "source_count": n_sources,
            })

        return sorted(scored, key=lambda x: x["trend_score"], reverse=True)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_top_topics(
        self,
        all_topics: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Process raw topics from all fetchers and return the top N candidates.

        Args:
            all_topics: Combined raw list from GoogleTrends + Reddit + NewsAPI.
            top_n: Number of topics to return.

        Returns:
            Ranked list of topic dicts (filtered, deduplicated, scored).
        """
        aggregated = self._aggregate(all_topics)

        filtered: list[dict[str, Any]] = []
        for item in aggregated:
            topic = item["topic"]

            if not self._passes_blacklist(topic):
                log.debug("trend_scorer.blacklisted", topic=topic)
                continue

            if item["trend_score"] < self.min_trend_score:
                log.debug(
                    "trend_scorer.below_threshold",
                    topic=topic,
                    score=item["trend_score"],
                )
                continue

            if self._is_in_history(topic):
                log.debug("trend_scorer.in_history", topic=topic)
                continue

            filtered.append(item)
            if len(filtered) >= top_n:
                break

        log.info(
            "trend_scorer.get_top_topics.done",
            candidates=len(aggregated),
            filtered=len(filtered),
        )
        return filtered

    def get_top_topic(self, all_topics: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """
        Return the single best topic. Records it in history immediately.

        Args:
            all_topics: Combined raw list from all fetchers.

        Returns:
            Best topic dict, or None if nothing passes filters.
        """
        top = self.get_top_topics(all_topics, top_n=1)
        if not top:
            log.warning("trend_scorer.get_top_topic.no_results")
            return None

        best = top[0]
        self.add_to_history(best["topic"], best["trend_score"], best["primary_source"])
        return best
