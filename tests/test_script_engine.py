"""
Tests for Phase 3: Script Engine.

Covers:
- hook_templates: template selection and formatting
- script_validator: all validation checks (no API calls)
- script_generator: LLM call mocking + JSON parsing + retry logic
- config_loader: config reading

Run with: python -m pytest tests/test_script_engine.py -v
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  hook_templates                                                      #
# ------------------------------------------------------------------ #

class TestHookTemplates:
    def test_question_hook_fills_topic(self):
        from src.script_engine.hook_templates import get_hook
        hook = get_hook("question", "the speed of light", seed=0)
        assert "the speed of light" in hook
        assert hook.endswith("?")

    def test_shocking_stat_hook(self):
        from src.script_engine.hook_templates import get_hook
        hook = get_hook("shocking_stat", "black holes", seed=0)
        assert "black holes" in hook

    def test_bold_claim_hook(self):
        from src.script_engine.hook_templates import get_hook
        hook = get_hook("bold_claim", "gravity", seed=0)
        assert "gravity" in hook

    def test_seed_varies_template(self):
        from src.script_engine.hook_templates import get_hook
        h0 = get_hook("question", "AI", seed=0)
        h1 = get_hook("question", "AI", seed=1)
        # Different seeds should produce different templates
        assert h0 != h1

    def test_invalid_style_falls_back_to_question(self):
        from src.script_engine.hook_templates import get_hook
        hook = get_hook("nonexistent_style", "topic")  # type: ignore
        assert "topic" in hook

    def test_get_cta_varies(self):
        from src.script_engine.hook_templates import get_cta
        c0 = get_cta(seed=0)
        c1 = get_cta(seed=1)
        assert isinstance(c0, str)
        assert isinstance(c1, str)
        assert c0 != c1


# ------------------------------------------------------------------ #
#  config_loader                                                       #
# ------------------------------------------------------------------ #

class TestConfigLoader:
    def test_get_config_returns_appconfig(self):
        from src.utils.config_loader import get_config, AppConfig
        cfg = get_config(reload=True)
        assert isinstance(cfg, AppConfig)

    def test_scheduler_keys_present(self):
        from src.utils.config_loader import get_config
        cfg = get_config(reload=True)
        assert cfg.scheduler["videos_per_day"] == 3
        assert cfg.scheduler["timezone"] == "Asia/Kolkata"

    def test_script_keys_present(self):
        from src.utils.config_loader import get_config
        cfg = get_config(reload=True)
        assert cfg.script["min_words"] > 0
        assert cfg.script["max_words"] > cfg.script["min_words"]

    def test_dot_access(self):
        from src.utils.config_loader import get_config
        cfg = get_config(reload=True)
        # Nested dot-access
        assert cfg.trends["min_trend_score"] == 60


# ------------------------------------------------------------------ #
#  ScriptValidator — no API calls                                      #
# ------------------------------------------------------------------ #

def _make_valid_script() -> dict:
    """Build a minimal valid script dict (≥80 words, 25-59s duration)."""
    return {
        "topic": "Black Holes",
        "category": "science",
        "video_id": "test_001",
        "title": "The insane truth about Black Holes #Shorts",
        "description": "Mind-blowing black hole facts.\n#Shorts #Space #Facts",
        "script_text": (
            "Did you know that black holes are so dense that nothing — "
            "not even light — can escape their gravity? "
            "Scientists have discovered that every galaxy, including our own Milky Way, "
            "has a supermassive black hole sitting right at its center. "
            "The closest one to Earth is 26,000 light years away. "
            "That sounds incredibly far, but in cosmic terms it is basically our next door neighbor. "
            "Turns out the universe is far stranger and more violent than we ever imagined. "
            "These cosmic monsters warp space and time itself around them. "
            "Follow for more mind-blowing space facts every single day."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Did you know that black holes are so dense that nothing — not even light — can escape their gravity?",
                "visual_prompt": "Dramatic visualization of a black hole with glowing accretion disk in deep space, photorealistic, 9:16 portrait",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Scientists have discovered that every galaxy has a supermassive black hole at its center.",
                "visual_prompt": "Milky Way galaxy center glowing with cosmic energy, stars swirling around a dark center, photorealistic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "The closest one to Earth is 26,000 light years away — basically next door in cosmic terms. Follow for more.",
                "visual_prompt": "Distance visualization from Earth to galactic center, space travel perspective, photorealistic",
                "duration_estimate": 9,
            },
        ],
        "tags": ["blackhole", "space", "facts", "shorts", "science"],
        "hook_score_self_rating": 8,
    }


class TestScriptValidator:
    def _make_validator(self) -> "ScriptValidator":
        from src.script_engine.script_validator import ScriptValidator
        return ScriptValidator(use_llm_hook_check=False)

    def test_valid_script_passes(self):
        v = self._make_validator()
        script = _make_valid_script()
        result = v.validate(script)
        assert result["word_count"] > 0
        assert result["estimated_duration"] > 0

    def test_too_short_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        script["script_text"] = "Short script."  # way under min_words
        with pytest.raises(ScriptValidationError, match="too short"):
            v.validate(script)

    def test_too_long_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        script["script_text"] = " ".join(["word"] * 200)  # over max_words
        with pytest.raises(ScriptValidationError, match="too long"):
            v.validate(script)

    def test_empty_scenes_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        script["scenes"] = []
        with pytest.raises(ScriptValidationError, match="no scenes"):
            v.validate(script)

    def test_scene_missing_narration_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        script["scenes"][0]["narration"] = ""
        with pytest.raises(ScriptValidationError, match="empty narration"):
            v.validate(script)

    def test_scene_missing_visual_prompt_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        script["scenes"][0]["visual_prompt"] = ""
        with pytest.raises(ScriptValidationError, match="empty visual_prompt"):
            v.validate(script)

    def test_duration_too_short_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        for s in script["scenes"]:
            s["duration_estimate"] = 1  # total = 3s
        with pytest.raises(ScriptValidationError, match="too short"):
            v.validate(script)

    def test_duration_too_long_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        # Add extra scenes so total duration exceeds 59s while keeping word count valid
        for s in script["scenes"]:
            s["duration_estimate"] = 22  # 3 × 22 = 66s > 59s max
        with pytest.raises(ScriptValidationError, match="too long"):
            v.validate(script)

    def test_no_hook_in_first_sentence_fails(self):
        from src.script_engine.script_validator import ScriptValidationError
        v = self._make_validator()
        script = _make_valid_script()
        # First sentence is bland — no ?, !, or power words
        script["script_text"] = (
            "Black holes exist in outer space throughout the observable universe. "
            "Scientists have confirmed through observation that nothing escapes their immense gravitational pull. "
            "Every single major galaxy we have observed has one positioned at the very center. "
            "The nearest one is twenty six thousand light years away from planet Earth. "
            "This is considered a remarkable finding in the field of modern observational astronomy. "
            "Researchers from around the world continue to study these extraordinary cosmic phenomena carefully. "
            "Follow for more interesting science content delivered to your feed every single day."
        )
        with pytest.raises(ScriptValidationError, match="hook"):
            v.validate(script)

    def test_power_word_hook_passes(self):
        """A hook with a power word but no ? or ! should still pass."""
        v = self._make_validator()
        script = _make_valid_script()
        script["script_text"] = (
            "Turns out black holes are far stranger than anyone in history ever imagined. "
            "Scientists have now discovered that every single galaxy has one sitting right at its very center. "
            "The nearest supermassive black hole to Earth is a staggering 26,000 light years away. "
            "That means it is basically our closest and most terrifying cosmic neighbor in the whole galaxy. "
            "The universe is absolutely insane and we are only just beginning to scratch the surface. "
            "Follow for more mind-blowing space facts delivered to you every single day of the week."
        )
        result = v.validate(script)
        assert result is not None

    @patch("src.script_engine.script_validator.ScriptValidator._rate_hook")
    def test_low_hook_score_fails(self, mock_rate):
        from src.script_engine.script_validator import ScriptValidationError, ScriptValidator
        mock_rate.return_value = 4  # below threshold of 6
        v = ScriptValidator(use_llm_hook_check=True)
        script = _make_valid_script()
        with pytest.raises(ScriptValidationError, match="quality too low"):
            v.validate(script)

    @patch("src.script_engine.script_validator.ScriptValidator._rate_hook")
    def test_good_hook_score_passes(self, mock_rate):
        from src.script_engine.script_validator import ScriptValidator
        mock_rate.return_value = 8
        v = ScriptValidator(use_llm_hook_check=True)
        result = v.validate(_make_valid_script())
        assert result["word_count"] > 0

    def test_word_count_annotated(self):
        v = self._make_validator()
        script = _make_valid_script()
        result = v.validate(script)
        expected_wc = len(script["script_text"].split())
        assert result["word_count"] == expected_wc

    def test_estimated_duration_annotated(self):
        v = self._make_validator()
        script = _make_valid_script()
        result = v.validate(script)
        expected_dur = sum(s["duration_estimate"] for s in script["scenes"])
        assert result["estimated_duration"] == expected_dur


# ------------------------------------------------------------------ #
#  ScriptGenerator — Gemini-mocked calls                              #
# ------------------------------------------------------------------ #

class TestScriptGenerator:
    def _valid_script_dict(self) -> dict:
        """Return a valid script dict (as Gemini would parse and return)."""
        return {
            "title": "The insane truth about AI #Shorts",
            "description": "AI facts that will blow your mind.\n#Shorts #AI #Tech",
            "script_text": (
                "Did you know that AI can now write code better than most programmers? "
                "In 2024, AI systems started outperforming human engineers on benchmarks. "
                "The pace of improvement is accelerating faster than anyone predicted. "
                "We are living through the most important technological shift in history. "
                "Nobody knows where this is heading, but it is changing everything. "
                "Follow for more mind-blowing tech facts every single day."
            ),
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Did you know that AI can now write code better than most programmers?",
                    "visual_prompt": "Futuristic AI robot coding at a holographic terminal, blue neon light, 9:16 portrait",
                    "duration_estimate": 8,
                },
                {
                    "scene_number": 2,
                    "narration": "AI systems started outperforming human engineers on every benchmark.",
                    "visual_prompt": "Bar chart showing AI vs human performance, digital visualization",
                    "duration_estimate": 9,
                },
                {
                    "scene_number": 3,
                    "narration": "Nobody knows where this is heading — but it changes everything. Follow for more.",
                    "visual_prompt": "Earth from space with digital data streams, global AI impact",
                    "duration_estimate": 8,
                },
            ],
            "tags": ["ai", "technology", "facts", "shorts", "future",
                     "artificial intelligence", "machine learning", "coding",
                     "future tech", "innovation", "tech facts", "ai facts",
                     "robots", "automation", "neural network", "deep learning",
                     "openai", "programming", "software", "digital"],
            "topic_hashtags": [
                "#AIFacts", "#TechFacts", "#ArtificialIntelligence", "#MachineLearning",
                "#FutureTech", "#Innovation", "#TechTrends", "#AIRevolution",
                "#CodingFacts", "#TechNews",
            ],
            "hook_score_self_rating": 8,
        }

    @patch("src.script_engine.script_generator.call_gemini_json")
    def test_generate_success(self, mock_gemini, tmp_path):
        from src.script_engine.script_generator import ScriptGenerator

        mock_gemini.return_value = self._valid_script_dict()

        with patch("src.script_engine.script_generator.get_project_root", return_value=tmp_path):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                gen = ScriptGenerator()
                script = gen.generate("AI technology breakthroughs", "video_001", "technology")

        assert script["title"] != ""
        assert len(script["scenes"]) == 3
        assert script["video_id"] == "video_001"
        assert script["topic"] == "AI technology breakthroughs"
        mock_gemini.assert_called_once()

    @patch("src.script_engine.script_generator.call_gemini_json")
    def test_script_saved_to_disk(self, mock_gemini, tmp_path):
        from src.script_engine.script_generator import ScriptGenerator

        mock_gemini.return_value = self._valid_script_dict()

        with patch("src.script_engine.script_generator.get_project_root", return_value=tmp_path):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                gen = ScriptGenerator()
                gen.generate("AI topic", "video_save_test", "technology")

        saved = tmp_path / "output" / "scripts" / "video_save_test.json"
        assert saved.exists()
        with open(saved) as f:
            data = json.load(f)
        assert data["video_id"] == "video_save_test"

    @patch("src.script_engine.script_generator.call_gemini_json")
    def test_invalid_response_retries_then_fails(self, mock_gemini, tmp_path):
        from src.script_engine.script_generator import ScriptGenerator

        # Gemini returns dict missing required 'scenes' key
        mock_gemini.return_value = {"title": "test", "description": "d", "script_text": "t", "tags": []}

        with patch("src.script_engine.script_generator.get_project_root", return_value=tmp_path):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                gen = ScriptGenerator()
                with pytest.raises(RuntimeError, match="failed after"):
                    gen.generate("Some topic", "video_fail", "general")

        assert mock_gemini.call_count == gen.max_retries

    @patch("src.script_engine.script_generator.call_gemini_json")
    def test_gemini_exception_retries_then_fails(self, mock_gemini, tmp_path):
        from src.script_engine.script_generator import ScriptGenerator

        mock_gemini.side_effect = RuntimeError("Gemini unavailable")

        with patch("src.script_engine.script_generator.get_project_root", return_value=tmp_path):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                gen = ScriptGenerator()
                with pytest.raises(RuntimeError, match="failed after"):
                    gen.generate("Topic", "video_err", "general")

        assert mock_gemini.call_count == gen.max_retries

    @patch("src.script_engine.script_generator.call_gemini_json")
    def test_metadata_attached_to_script(self, mock_gemini, tmp_path):
        from src.script_engine.script_generator import ScriptGenerator

        mock_gemini.return_value = self._valid_script_dict()

        with patch("src.script_engine.script_generator.get_project_root", return_value=tmp_path):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                gen = ScriptGenerator()
                script = gen.generate("Ocean waves energy", "video_meta", "science")

        assert script["topic"] == "Ocean waves energy"
        assert script["category"] == "science"
        assert script["video_id"] == "video_meta"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
