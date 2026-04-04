"""
Tests for Phase 6: Subtitle System.

Covers:
- WhisperAligner: segment extraction, even-distribution fallback,
                  JSON save/load roundtrip
- SubtitleRenderer: chunk building, active-word detection, pop-scale
                    animation, frame compositing, full render()

Whisper model is always mocked — tests run offline with no GPU.

Run with: python -m pytest tests/test_subtitles.py -v
"""

import io
import json
import sys
from dataclasses import asdict
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Shared fixtures                                                    #
# ------------------------------------------------------------------ #

def _make_segments(words: list[str], start_offset: float = 0.0) -> list:
    """Build a list of WordSegment with evenly spaced 0.5-second windows."""
    from src.subtitles.whisper_align import WordSegment
    segs = []
    for i, w in enumerate(words):
        t0 = start_offset + i * 0.5
        segs.append(WordSegment(word=w, start=round(t0, 3), end=round(t0 + 0.45, 3)))
    return segs


def _make_audio_file(tmp_path: Path, name: str = "audio.wav") -> Path:
    """Write a tiny placeholder WAV file."""
    p = tmp_path / name
    # Minimal WAV header (44 bytes) + some silence samples
    p.write_bytes(b"RIFF" + b"\x00" * 40)
    return p


def _make_solid_clip(duration: float = 3.0, color=(80, 80, 80)):
    """Return a solid-colour VideoClip for testing."""
    from moviepy import VideoClip
    def make_frame(t):
        return np.full((1920, 1080, 3), color, dtype=np.uint8)
    return VideoClip(make_frame, duration=duration).with_fps(30)


# ------------------------------------------------------------------ #
#  WhisperAligner tests                                               #
# ------------------------------------------------------------------ #

class TestWhisperAligner:

    def _mock_whisper_result(self, words: list[str]) -> dict:
        """Build a fake Whisper transcription result dict with word timestamps."""
        ws = []
        for i, w in enumerate(words):
            ws.append({"word": w, "start": i * 0.5, "end": i * 0.5 + 0.45})
        return {
            "text": " ".join(words),
            "segments": [
                {"start": 0.0, "end": len(words) * 0.5, "text": " ".join(words), "words": ws}
            ],
        }

    def test_align_returns_word_segments(self, tmp_path):
        """align() returns one WordSegment per spoken word."""
        from src.subtitles.whisper_align import WhisperAligner, WordSegment

        audio = _make_audio_file(tmp_path)
        mock_result = self._mock_whisper_result(["Hello", "world", "this", "is", "a", "test"])

        aligner = WhisperAligner()

        mock_model = MagicMock()
        mock_model.transcribe.return_value = mock_result
        aligner._model = mock_model

        segments = aligner.align(audio)

        assert len(segments) == 6
        assert all(isinstance(s, WordSegment) for s in segments)
        assert segments[0].word == "Hello"
        assert segments[-1].word == "test"

    def test_align_segment_timing(self, tmp_path):
        """Each WordSegment has correct start and end times."""
        from src.subtitles.whisper_align import WhisperAligner

        audio = _make_audio_file(tmp_path)
        mock_result = self._mock_whisper_result(["Ocean", "waves"])

        aligner = WhisperAligner()
        aligner._model = MagicMock(transcribe=MagicMock(return_value=mock_result))

        segs = aligner.align(audio)

        assert segs[0].start == 0.0
        assert segs[0].end == 0.45
        assert segs[1].start == 0.5

    def test_align_raises_when_file_missing(self):
        """FileNotFoundError if audio file does not exist."""
        from src.subtitles.whisper_align import WhisperAligner

        aligner = WhisperAligner()
        with pytest.raises(FileNotFoundError):
            aligner.align(Path("/nonexistent/audio.wav"))

    def test_align_falls_back_when_no_word_timestamps(self, tmp_path):
        """When segments have no 'words' key, words are distributed evenly."""
        from src.subtitles.whisper_align import WhisperAligner

        audio = _make_audio_file(tmp_path)
        # Simulate result with no word-level data
        mock_result = {
            "text": "three words here",
            "segments": [{"start": 0.0, "end": 2.0, "text": "three words here"}],
        }

        aligner = WhisperAligner()
        aligner._model = MagicMock(transcribe=MagicMock(return_value=mock_result))

        segs = aligner.align(audio)

        assert len(segs) == 3  # "three words here" → 3 words
        assert segs[0].word == "three"
        assert segs[0].start == 0.0
        assert segs[-1].end > segs[-1].start

    def test_align_filters_empty_words(self, tmp_path):
        """Words that are empty strings after strip() are skipped."""
        from src.subtitles.whisper_align import WhisperAligner

        audio = _make_audio_file(tmp_path)
        mock_result = {
            "text": "hello world",
            "segments": [{
                "start": 0.0, "end": 1.0, "text": "hello world",
                "words": [
                    {"word": "hello", "start": 0.0, "end": 0.4},
                    {"word": "  ",    "start": 0.4, "end": 0.5},  # whitespace-only
                    {"word": "world", "start": 0.5, "end": 0.9},
                ],
            }],
        }

        aligner = WhisperAligner()
        aligner._model = MagicMock(transcribe=MagicMock(return_value=mock_result))

        segs = aligner.align(audio)
        words = [s.word for s in segs]
        assert "" not in words
        assert "hello" in words
        assert "world" in words

    def test_save_and_load_json_roundtrip(self, tmp_path):
        """save_json + load_json preserves all segment data exactly."""
        from src.subtitles.whisper_align import WhisperAligner, WordSegment

        original = _make_segments(["science", "is", "amazing"])
        aligner = WhisperAligner()

        json_path = tmp_path / "segments.json"
        aligner.save_json(original, json_path)

        assert json_path.exists()

        loaded = WhisperAligner.load_json(json_path)
        assert len(loaded) == len(original)
        for orig, loaded_seg in zip(original, loaded):
            assert orig.word  == loaded_seg.word
            assert orig.start == loaded_seg.start
            assert orig.end   == loaded_seg.end

    def test_save_json_creates_parent_dirs(self, tmp_path):
        """save_json() creates intermediate directories if needed."""
        from src.subtitles.whisper_align import WhisperAligner

        aligner = WhisperAligner()
        segs = _make_segments(["hello"])
        nested_path = tmp_path / "deep" / "nested" / "segments.json"

        aligner.save_json(segs, nested_path)
        assert nested_path.exists()

    def test_model_lazy_loaded(self, tmp_path):
        """The Whisper model is not loaded until align() is first called."""
        from src.subtitles.whisper_align import WhisperAligner

        aligner = WhisperAligner()
        assert aligner._model is None  # not yet loaded


# ------------------------------------------------------------------ #
#  SubtitleRenderer tests                                             #
# ------------------------------------------------------------------ #

class TestSubtitleRenderer:

    def test_render_returns_clip_same_duration(self):
        """Rendered clip has the same duration as the base clip."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        base = _make_solid_clip(duration=4.0)
        segs = _make_segments(["hello", "world", "this", "is", "cool"], 0.2)

        result = renderer.render(base, segs)
        assert abs(result.duration - 4.0) < 0.01

    def test_render_returns_30fps_clip(self):
        """Output clip is always 30 fps."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        base = _make_solid_clip(duration=2.0)
        segs = _make_segments(["test"], 0.2)

        result = renderer.render(base, segs)
        assert result.fps == 30

    def test_render_frame_shape_correct(self):
        """Frames from the rendered clip are (1920, 1080, 3)."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        base = _make_solid_clip(duration=3.0)
        segs = _make_segments(["ocean", "waves", "power"], 0.1)

        result = renderer.render(base, segs)
        frame = result.get_frame(1.0)
        assert frame.shape == (1920, 1080, 3)

    def test_render_no_segments_returns_base_clip(self):
        """With an empty segment list, the base clip is returned unchanged."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        base = _make_solid_clip(duration=3.0)

        result = renderer.render(base, [])
        np.testing.assert_array_equal(base.get_frame(1.0), result.get_frame(1.0))

    def test_chunk_building_groups_correctly(self):
        """Chunks contain exactly max_words_per_line words (except possibly last)."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        renderer._max_words = 4

        words = ["a", "b", "c", "d", "e", "f", "g"]
        segs  = _make_segments(words)
        chunks = renderer._build_chunks(segs)

        assert len(chunks) == 2          # 4 + 3
        assert len(chunks[0].words) == 4
        assert len(chunks[1].words) == 3

    def test_chunk_timing_spans_all_words(self):
        """Each chunk's start/end spans the full word group."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        segs = _make_segments(["one", "two", "three", "four"])
        chunks = renderer._build_chunks(segs)

        assert len(chunks) == 1
        assert chunks[0].start == segs[0].start
        assert chunks[0].end   == segs[-1].end

    def test_find_active_returns_correct_word_index(self):
        """_find_active() returns the right word index at a given time."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        segs   = _make_segments(["hello", "world", "test", "now"])
        chunks = renderer._build_chunks(segs)

        # At t=0.05 → first word "hello" (start=0.0, end=0.45)
        chunk, idx = renderer._find_active(0.05, chunks)
        assert chunk is not None
        assert idx == 0

        # At t=0.55 → second word "world" (start=0.5, end=0.95)
        chunk, idx = renderer._find_active(0.55, chunks)
        assert idx == 1

    def test_find_active_returns_none_outside_all_chunks(self):
        """Time before all words → no active chunk."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        segs   = _make_segments(["hello"], start_offset=2.0)
        chunks = renderer._build_chunks(segs)

        chunk, idx = renderer._find_active(0.0, chunks)
        assert chunk is None

    def test_pop_scale_at_word_start_is_peak(self):
        """Pop scale is at maximum right at the word's start time."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer, _POP_SCALE
        from src.subtitles.whisper_align import WordSegment

        renderer = SubtitleRenderer()
        renderer._animation = "scale_pop"

        ws = WordSegment(word="pop", start=1.0, end=1.5)
        scale = renderer._pop_scale_at(1.0, ws)

        assert abs(scale - _POP_SCALE) < 0.01

    def test_pop_scale_returns_1_outside_window(self):
        """Pop scale is 1.0 before the word starts or after the pop window."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer, _POP_DURATION
        from src.subtitles.whisper_align import WordSegment

        renderer = SubtitleRenderer()
        ws = WordSegment(word="pop", start=1.0, end=1.5)

        assert renderer._pop_scale_at(0.5, ws) == 1.0                      # before
        assert renderer._pop_scale_at(1.0 + _POP_DURATION + 0.01, ws) == 1.0  # after

    def test_pop_scale_disabled_when_animation_not_scale_pop(self):
        """pop_scale_at returns 1.0 when animation style is not scale_pop."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer
        from src.subtitles.whisper_align import WordSegment

        renderer = SubtitleRenderer()
        renderer._animation = "fade"
        ws = WordSegment(word="test", start=0.0, end=0.5)

        assert renderer._pop_scale_at(0.0, ws) == 1.0

    def test_caption_modifies_frame_pixels(self):
        """A frame during an active word should differ from the base frame."""
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        renderer = SubtitleRenderer()
        base = _make_solid_clip(duration=3.0, color=(80, 80, 80))
        segs = _make_segments(["Hello", "World"], start_offset=0.5)

        result = renderer.render(base, segs)

        t = segs[0].start + 0.1   # during first word
        base_frame   = base.get_frame(t)
        result_frame = result.get_frame(t)

        # Frames should differ (subtitle pixels added)
        assert not np.array_equal(base_frame, result_frame), (
            "Expected subtitle to modify at least some pixels"
        )

    def test_composite_helper_blends_correctly(self):
        """_composite() correctly blends caption over base using alpha."""
        from src.subtitles.subtitle_renderer import _composite

        # White base frame
        base = np.full((1920, 1080, 3), 255, dtype=np.uint8)

        # Fully opaque black caption in top-left 10×10 patch
        caption = np.zeros((1920, 1080, 4), dtype=np.uint8)
        caption[:10, :10, 3] = 255   # alpha = fully opaque
        caption[:10, :10, :3] = 0    # colour = black

        result = _composite(base, caption)

        # Top-left patch should now be black
        assert result[5, 5, 0] == 0
        # Rest of frame should remain white
        assert result[500, 500, 0] == 255

    def test_hex_to_rgb_conversion(self):
        """_hex_to_rgb converts hex colour strings correctly."""
        from src.subtitles.subtitle_renderer import _hex_to_rgb

        assert _hex_to_rgb("#FFFF00") == (255, 255, 0)
        assert _hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert _hex_to_rgb("#000000") == (0, 0, 0)
        assert _hex_to_rgb("FF0000")  == (255, 0, 0)   # no leading #


# ------------------------------------------------------------------ #
#  Integration: WhisperAligner → SubtitleRenderer chain              #
# ------------------------------------------------------------------ #

class TestWhisperToRendererChain:

    def test_aligner_output_feeds_renderer(self, tmp_path):
        """Segments from WhisperAligner can be passed directly to SubtitleRenderer."""
        from src.subtitles.whisper_align import WhisperAligner
        from src.subtitles.subtitle_renderer import SubtitleRenderer

        # Mock Whisper
        words = ["Ocean", "waves", "could", "power", "the", "world"]
        mock_result = {
            "text": " ".join(words),
            "segments": [{
                "start": 0.0,
                "end": len(words) * 0.5,
                "text": " ".join(words),
                "words": [
                    {"word": w, "start": i * 0.5, "end": i * 0.5 + 0.45}
                    for i, w in enumerate(words)
                ],
            }],
        }

        audio = _make_audio_file(tmp_path)
        aligner = WhisperAligner()
        aligner._model = MagicMock(transcribe=MagicMock(return_value=mock_result))

        segments = aligner.align(audio)

        # Feed into renderer
        renderer = SubtitleRenderer()
        base     = _make_solid_clip(duration=5.0)
        result   = renderer.render(base, segments)

        assert result.duration == base.duration
        assert result.get_frame(1.0).shape == (1920, 1080, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
