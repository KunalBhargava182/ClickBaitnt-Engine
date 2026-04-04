"""
Topic safety and visual-potential filter.
Uses a lightweight LLM call to classify topics before they enter the pipeline.
"""

from typing import Any, Optional

from src.utils.logger import log
from src.utils.retry import with_retry


class TopicFilter:
    """
    Two-stage topic filter:

    1. Blacklist check (fast, no API call).
    2. LLM safety + visual-richness classification (one API call).

    LLM gates:
    - Safe for general YouTube audience? (Yes/No)
    - Visual richness score 1-10 (rejects < 4)

    Uses OpenAI if available, otherwise Anthropic, otherwise skips LLM check.
    """

    SAFETY_PROMPT = """You are a content moderation assistant for a family-friendly YouTube channel.
Given the topic below, answer two questions with JSON only:

1. "safe": true/false — Is this topic safe for a general YouTube audience (all ages)?
   Mark false if the topic involves: explicit violence, adult content, hate speech,
   political controversy, religious controversy, illegal activities, self-harm.

2. "visual_richness": integer 1-10 — How visually rich is this topic?
   10 = stunning imagery (space, nature, technology, history)
   5  = moderate visuals (psychology concepts, money graphs)
   1  = very hard to illustrate (abstract philosophy, pure statistics)

Respond ONLY with valid JSON:
{{"safe": true, "visual_richness": 8}}

Topic: "{topic}"
"""

    VISUAL_RICHNESS_MIN = 4
    SAFETY_MIN = True

    def __init__(self, blacklist: list[str], use_llm: bool = True):
        """
        Args:
            blacklist: List of forbidden keyword strings.
            use_llm: Whether to run Gemini classification. Set False for tests/offline.
        """
        self.blacklist = [b.lower() for b in blacklist]
        self.use_llm = use_llm

    def _passes_blacklist(self, topic: str) -> bool:
        """Return True if topic does not contain any blacklisted keyword."""
        topic_lower = topic.lower()
        for bad in self.blacklist:
            if bad in topic_lower:
                log.debug("topic_filter.blacklist_hit", topic=topic, keyword=bad)
                return False
        return True

    @with_retry(max_attempts=2, backoff_factor=2, exceptions=(Exception,))
    def _llm_classify(self, topic: str) -> dict[str, Any]:
        """
        Run Gemini classification for topic safety and visual richness.

        Args:
            topic: Topic string to classify.

        Returns:
            Dict with keys: safe (bool), visual_richness (int).
        """
        from src.utils.gemini_client import call_gemini_json

        prompt = self.SAFETY_PROMPT.format(topic=topic)
        try:
            result = call_gemini_json(prompt, temperature=0.1, max_tokens=60)
            return result
        except Exception as exc:
            log.warning("topic_filter.llm_classify.gemini_failed", error=str(exc))
            # Fail-open: allow topic through if Gemini is unavailable
            return {"safe": True, "visual_richness": 7}

    def is_approved(self, topic: str) -> tuple[bool, str]:
        """
        Run all filter stages for a topic.

        Args:
            topic: Topic string to evaluate.

        Returns:
            Tuple (approved: bool, reason: str).
        """
        # Stage 1: Blacklist
        if not self._passes_blacklist(topic):
            return False, "blacklisted"

        # Stage 2: LLM classification
        if self.use_llm:
            try:
                result = self._llm_classify(topic)
                if not result.get("safe", True):
                    return False, "llm_unsafe"
                richness = int(result.get("visual_richness", 7))
                if richness < self.VISUAL_RICHNESS_MIN:
                    return (
                        False,
                        f"low_visual_richness:{richness}",
                    )
            except Exception as exc:
                log.warning(
                    "topic_filter.llm_check.exception",
                    topic=topic,
                    error=str(exc),
                )
                # Don't block on LLM failure — allow through
                return True, "llm_check_failed_allowed"

        return True, "approved"

    def filter_topics(self, topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Filter a list of topic dicts, returning only approved ones.

        Args:
            topics: List of trend dicts (must have "topic" key).

        Returns:
            Filtered list with only approved topics.
        """
        approved = []
        for item in topics:
            topic = item.get("topic", "")
            ok, reason = self.is_approved(topic)
            if ok:
                approved.append(item)
            else:
                log.info(
                    "topic_filter.rejected",
                    topic=topic,
                    reason=reason,
                )

        log.info(
            "topic_filter.filter_topics.done",
            input=len(topics),
            approved=len(approved),
        )
        return approved
