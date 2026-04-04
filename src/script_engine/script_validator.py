"""
Script quality validator.
Checks word count, structure, hook quality, and total estimated duration.
Uses Gemini (free) for hook quality rating (rejects hooks scoring < 6/10).
"""

import re
from typing import Any

from src.utils.config_loader import get_config
from src.utils.logger import log

HOOK_RATING_PROMPT = """Rate the following YouTube Shorts hook on a scale of 1-10.

A great hook (8-10): immediately creates curiosity, makes a surprising claim, or poses a compelling question.
A poor hook (1-5): generic, boring, reads like a news headline with no emotional pull.

Respond with JSON only: {{"score": 7, "reason": "brief explanation"}}

Hook: "{hook}"
"""


class ScriptValidationError(Exception):
    """Raised when a script fails any validation check."""
    pass


class ScriptValidator:
    """
    Five-gate script quality validator.

    1. Word count within [min_words, max_words] from config
    2. All scenes have non-empty narration and visual_prompt
    3. Total estimated duration within 15-59 seconds
    4. Hook in first sentence (? or ! or power word)
    5. (Optional) Gemini hook quality score ≥ 6
    """

    DURATION_MIN = 15
    DURATION_MAX = 59
    HOOK_SCORE_MIN = 6

    POWER_WORDS = [
        "secret", "insane", "nobody knows", "actually", "turns out",
        "shocking", "incredible", "mind-blowing", "wild", "crazy",
        "you won't believe", "wait until", "the truth", "nobody talks",
    ]

    def __init__(self, use_llm_hook_check: bool = True):
        """
        Args:
            use_llm_hook_check: Run Gemini hook quality check.
                                Set False for tests / offline runs.
        """
        cfg = get_config()
        self.min_words = cfg.script["min_words"]
        self.max_words = cfg.script["max_words"]
        self.use_llm_hook_check = use_llm_hook_check

    # ---------------------------------------------------------------- #
    #  Individual checks                                                #
    # ---------------------------------------------------------------- #

    def _check_word_count(self, script: dict[str, Any]) -> None:
        text = script.get("script_text", "")
        wc = len(text.split())
        if wc < self.min_words:
            raise ScriptValidationError(
                f"Script too short: {wc} words (min {self.min_words})"
            )
        if wc > self.max_words:
            raise ScriptValidationError(
                f"Script too long: {wc} words (max {self.max_words})"
            )
        log.debug("script_validator.word_count_ok", words=wc)

    def _check_scenes(self, script: dict[str, Any]) -> None:
        scenes = script.get("scenes", [])
        if not scenes:
            raise ScriptValidationError("Script has no scenes")
        for scene in scenes:
            if not scene.get("narration", "").strip():
                raise ScriptValidationError(
                    f"Scene {scene.get('scene_number', '?')} has empty narration"
                )
            if not scene.get("visual_prompt", "").strip():
                raise ScriptValidationError(
                    f"Scene {scene.get('scene_number', '?')} has empty visual_prompt"
                )
        log.debug("script_validator.scenes_ok", count=len(scenes))

    def _check_duration(self, script: dict[str, Any]) -> None:
        total = sum(s.get("duration_estimate", 0) for s in script.get("scenes", []))
        if total < self.DURATION_MIN:
            raise ScriptValidationError(
                f"Estimated duration too short: {total}s (min {self.DURATION_MIN}s)"
            )
        if total > self.DURATION_MAX:
            raise ScriptValidationError(
                f"Estimated duration too long: {total}s (max {self.DURATION_MAX}s)"
            )
        log.debug("script_validator.duration_ok", estimated_seconds=total)

    def _check_hook_structure(self, script: dict[str, Any]) -> str:
        """
        Verify the first sentence has a hook indicator.
        Returns the first sentence for optional LLM rating.
        """
        text = script.get("script_text", "").strip()
        if not text:
            raise ScriptValidationError("script_text is empty")

        sentences = re.split(r"(?<=[.!?])\s+", text)
        first = sentences[0].strip() if sentences else ""

        has_punct_hook = first.endswith(("?", "!"))
        has_power_word = any(w in first.lower() for w in self.POWER_WORDS)

        if not (has_punct_hook or has_power_word):
            raise ScriptValidationError(
                f"First sentence is not a hook (no ?, !, or power word): "
                f"'{first[:80]}'"
            )

        log.debug("script_validator.hook_structure_ok", first_sentence=first[:60])
        return first

    # ---------------------------------------------------------------- #
    #  Gemini hook quality rating                                       #
    # ---------------------------------------------------------------- #

    def _rate_hook(self, hook: str) -> int:
        """
        Ask Gemini to rate hook quality 1-10.

        Returns default passing score (7) if Gemini is unavailable.
        """
        from src.utils.gemini_client import call_gemini_json

        prompt = HOOK_RATING_PROMPT.format(hook=hook)
        try:
            result = call_gemini_json(prompt, temperature=0.1, max_tokens=80)
            score = int(result.get("score", 7))
            reason = result.get("reason", "")
            log.info("script_validator.hook_rated", score=score, reason=reason)
            return score
        except Exception as exc:
            log.warning(
                "script_validator.hook_rating_failed",
                error=str(exc),
                fallback_score=7,
            )
            return 7  # Fail-open: don't block on Gemini errors

    def _check_hook_quality(self, hook: str) -> None:
        score = self._rate_hook(hook)
        if score < self.HOOK_SCORE_MIN:
            raise ScriptValidationError(
                f"Hook quality too low: {score}/10 (min {self.HOOK_SCORE_MIN}). "
                f"Hook: '{hook[:80]}'"
            )
        log.info("script_validator.hook_quality_ok", score=score)

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def validate(self, script: dict[str, Any]) -> dict[str, Any]:
        """
        Run all validation checks.

        Args:
            script: Script dict from ScriptGenerator.generate().

        Returns:
            Same dict, annotated with word_count and estimated_duration.

        Raises:
            ScriptValidationError: On any failed check with descriptive message.
        """
        topic = script.get("topic", "unknown")
        log.info("script_validator.validate.start", topic=topic)

        self._check_word_count(script)
        self._check_scenes(script)
        self._check_duration(script)
        hook = self._check_hook_structure(script)

        if self.use_llm_hook_check:
            self._check_hook_quality(hook)

        script["word_count"] = len(script.get("script_text", "").split())
        script["estimated_duration"] = sum(
            s.get("duration_estimate", 0) for s in script.get("scenes", [])
        )

        log.info(
            "script_validator.validate.passed",
            topic=topic,
            words=script["word_count"],
            duration=script["estimated_duration"],
        )
        return script
