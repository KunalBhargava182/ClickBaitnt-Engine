"""
AI-powered short-form video script generator.
Uses Google Gemini (free tier: 15 RPM, 1M tokens/day).
"""

import json
from pathlib import Path
from typing import Any

from src.utils.config_loader import get_config, get_project_root
from src.utils.gemini_client import call_gemini_json
from src.utils.logger import log

# ------------------------------------------------------------------ #
#  Prompt templates                                                    #
# ------------------------------------------------------------------ #

HINDI_SCRIPT_PROMPT = """You are a viral Hindi short-form video scriptwriter for the YouTube Shorts channel "ClickBaitn't India".
Write a script in HINDI (Devanagari script) that stops the scroll in the first 3 seconds.

RULES:
- Write script_text and all narration fields ENTIRELY in Hindi (Devanagari script).
- HOOK (first 3 seconds): Start with a surprising question (क्या आप जानते हैं...) or shocking fact.
- BODY: 2-3 punchy facts in natural spoken Hindi. Each fact = 1 scene.
- CTA (last 3 seconds): "Follow करें और ऐसे ही mind-blowing facts जानें।" or similar.
- Word count: {min_words}-{max_words} words total in the script.
- Write conversational Hindi — not formal or bookish. How a friend would tell you.
- VISUAL PROMPTS must be in ENGLISH (used for stock photo search).

TITLE: Hindi title, max 70 characters, ending with #Shorts.
DESCRIPTION: Hindi, 1-2 sentences, no hashtags.
TAGS: English tags for YouTube SEO, exactly 20, no # symbols, lowercase.
TOPIC HASHTAGS: Exactly 10, mix of Hindi and English hashtags starting with #.

Topic: {topic}
Target duration: {duration} seconds

OUTPUT: strict JSON only (no markdown fences), matching this schema exactly:
{{
  "title": "Hindi title ending with #Shorts",
  "description": "Hindi SEO summary — 1-2 sentences",
  "script_text": "Full Hindi narration as one continuous Devanagari string",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "Exact Hindi words spoken in this scene (Devanagari)",
      "visual_prompt": "English image search prompt for this scene (photorealistic, 9:16 portrait)",
      "duration_estimate": 8
    }}
  ],
  "tags": ["tag1", "tag2", "...", "tag20"],
  "topic_hashtags": ["#Tag1", "#Tag2", "...", "#Tag10"],
  "hook_score_self_rating": 8
}}"""


SCRIPT_PROMPT = """You are a viral short-form video scriptwriter specialising in YouTube Shorts for the channel "ClickBaitn't".
Write a script that stops the scroll in the first 3 seconds and holds attention to the end.

RULES:
- HOOK (first 3 seconds): Must stop the scroll. Use {hook_style} style.
- BODY (middle): 2-3 punchy facts or story beats. Each beat = 1 scene.
- CTA (last 3 seconds): "Follow for more [niche] facts" or similar.
- Tone: {tone}
- Word count: {min_words}-{max_words} words total.
- Write for SPOKEN delivery — no stage directions, no emojis, no visual notes.
- Every sentence must be independently interesting.
- Use power words: "secret", "insane", "nobody knows", "actually", "turns out".
- Make it feel like a friend telling you something amazing, not a lecture.

TITLE RULES:
- Max 70 characters total (including the #Shorts suffix).
- Use power words and create curiosity (e.g. "The Secret...", "Nobody Told You...", "This Changes Everything").
- Do NOT include hashtags in the title other than #Shorts at the very end.

DESCRIPTION RULES:
- Write a plain SEO summary (1-2 sentences, no hashtags).
- Do NOT include any hashtags in the description — they will be added separately.

TAGS RULES:
- Provide exactly 20 tags as an array.
- Mix: exact keywords, broader keywords, common misspellings, related topics.
- No # symbols in tags. Lowercase only.

TOPIC HASHTAGS RULES:
- Provide exactly 10 topic-specific hashtags for this video.
- Each must start with #. CamelCase (e.g. #BrainFacts, #SleepScience).
- Do NOT include #Shorts or #ClickBaitnt (those are added automatically).

Topic: {topic}
Niche category: {category}
Target duration: {duration} seconds

OUTPUT: strict JSON only (no markdown fences), matching this schema exactly:
{{
  "title": "Power-word title max 70 chars ending with #Shorts",
  "description": "SEO summary only — 1-2 sentences, no hashtags",
  "script_text": "The full narration script as one continuous string",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "Exact words spoken in this scene",
      "visual_prompt": "Detailed image generation prompt for this scene (photorealistic, 9:16 portrait, vibrant colors)",
      "duration_estimate": 8
    }}
  ],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13", "tag14", "tag15", "tag16", "tag17", "tag18", "tag19", "tag20"],
  "topic_hashtags": ["#TopicTag1", "#TopicTag2", "#TopicTag3", "#TopicTag4", "#TopicTag5", "#TopicTag6", "#TopicTag7", "#TopicTag8", "#TopicTag9", "#TopicTag10"],
  "hook_score_self_rating": 8
}}"""


class ScriptGenerator:
    """
    Generates complete short-form video scripts using Google Gemini.

    Retries up to max_retries times if JSON parsing or schema validation fails.
    Saves each script to output/scripts/{video_id}.json.
    """

    def __init__(self):
        cfg = get_config()
        self.cfg_script = cfg.script
        self.max_retries = cfg.scheduler.max_retries

    # ---------------------------------------------------------------- #
    #  Prompt building                                                  #
    # ---------------------------------------------------------------- #

    def _build_prompt(self, topic: str, category: str, language: str = "en") -> str:
        """Return the filled-in prompt string for the given language."""
        if language == "hi":
            return HINDI_SCRIPT_PROMPT.format(
                min_words=self.cfg_script["min_words"],
                max_words=self.cfg_script["max_words"],
                topic=topic,
                duration=self.cfg_script["target_duration_seconds"],
            )
        return SCRIPT_PROMPT.format(
            hook_style=self.cfg_script["hook_style"],
            tone=self.cfg_script["tone"],
            min_words=self.cfg_script["min_words"],
            max_words=self.cfg_script["max_words"],
            topic=topic,
            category=category,
            duration=self.cfg_script["target_duration_seconds"],
        )

    # ---------------------------------------------------------------- #
    #  Schema validation                                                #
    # ---------------------------------------------------------------- #

    def _validate_schema(self, data: dict[str, Any]) -> None:
        """
        Verify all required top-level keys and scene keys are present.

        Raises:
            ValueError: On missing keys or empty scenes list.
        """
        required = {"title", "description", "script_text", "scenes", "tags", "topic_hashtags"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Script JSON missing required keys: {missing}")

        if not isinstance(data["scenes"], list) or len(data["scenes"]) == 0:
            raise ValueError("Script must have at least one scene")

        for i, scene in enumerate(data["scenes"]):
            scene_required = {"scene_number", "narration", "visual_prompt", "duration_estimate"}
            missing_scene = scene_required - scene.keys()
            if missing_scene:
                raise ValueError(f"Scene {i+1} missing keys: {missing_scene}")

    # ---------------------------------------------------------------- #
    #  Persistence                                                      #
    # ---------------------------------------------------------------- #

    def _save_script(self, video_id: str, script: dict[str, Any]) -> Path:
        """Save validated script JSON to output/scripts/."""
        scripts_dir = get_project_root() / "output" / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        path = scripts_dir / f"{video_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        log.info("script_generator.script_saved", path=str(path))
        return path

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def generate(
        self,
        topic: str,
        video_id: str,
        category: str = "general",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Generate and validate a complete script for the given topic.

        Args:
            topic: Trending topic string.
            video_id: Unique identifier used for file naming.
            category: Niche category label (for prompt context).

        Returns:
            Validated script dict with keys:
            title, description, script_text, scenes, tags,
            hook_score_self_rating, topic, category, video_id.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        prompt = self._build_prompt(topic, category, language=language)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                log.info(
                    "script_generator.generate.attempt",
                    topic=topic,
                    attempt=attempt,
                )
                data = call_gemini_json(prompt, temperature=0.9, max_tokens=1500)
                self._validate_schema(data)

                # Attach pipeline metadata
                data["topic"] = topic
                data["category"] = category
                data["video_id"] = video_id

                self._save_script(video_id, data)
                log.info(
                    "script_generator.generate.success",
                    topic=topic,
                    video_id=video_id,
                    scenes=len(data["scenes"]),
                    hook_score=data.get("hook_score_self_rating", "n/a"),
                )
                return data

            except Exception as exc:
                last_error = exc
                log.warning(
                    "script_generator.generate.failed_attempt",
                    attempt=attempt,
                    error=str(exc),
                )

        raise RuntimeError(
            f"Script generation failed after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )
