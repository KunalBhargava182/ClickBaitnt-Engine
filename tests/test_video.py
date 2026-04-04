"""
Tests for Phase 7: Video Assembly.

Covers:
- VideoComposer: scene duration scaling, pipeline orchestration,
                 subtitle integration, audio attachment, output path
- VideoValidator: file gates, duration gates, resolution gates,
                  audio-stream gate, ffprobe fallback

All MoviePy / FFmpeg heavy operations are mocked so tests run without
a GPU, FFmpeg, or any real media files.

Run with: python -m pytest tests/test_video.py -v
"""

import io
import json
import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call, PropertyMock

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _make_png(tmp_path: Path, name: str = "scene.png") -> Path:
    p = tmp_path / name
    Image.new("RGB", (1080, 1920), color=(100, 150, 200)).save(str(p), "PNG")
    return p


def _make_audio(tmp_path: Path, name: str = "audio.wav") -> Path:
    """Write a minimal placeholder WAV."""
    p = tmp_path / name
    p.write_bytes(b"RIFF" + b"\x00" * 40)
    return p


def _make_scenes(n: int = 3) -> list[dict]:
    return [
        {
            "scene_number": i + 1,
            "narration": f"Scene {i + 1} narration text here.",
            "visual_prompt": f"Visual {i + 1}",
            "duration_estimate": 10.0,
        }
        for i in range(n)
    ]


def _make_word_segments(n: int = 6):
    from src.subtitles.whisper_align import WordSegment
    return [
        WordSegment(word=f"word{i}", start=i * 0.5, end=i * 0.5 + 0.45)
        for i in range(n)
    ]


def _solid_clip(duration: float = 3.0):
    """Return a real solid-colour VideoClip (no FFmpeg needed)."""
    from moviepy import VideoClip
    def make_frame(t):
        return np.full((1920, 1080, 3), 100, dtype=np.uint8)
    return VideoClip(make_frame, duration=duration).with_fps(30)


# ------------------------------------------------------------------ #
#  VideoComposer – duration scaling tests (pure logic, no mocks)     #
# ------------------------------------------------------------------ #

class TestVideoComposerScaling:

    def _composer(self):
        from src.video.video_composer import VideoComposer
        return VideoComposer()

    def test_scale_durations_proportional(self):
        """Durations scale proportionally and sum to audio_duration."""
        c = self._composer()
        scenes = [
            {"duration_estimate": 10.0},
            {"duration_estimate": 20.0},
            {"duration_estimate": 30.0},
        ]
        result = c._scale_durations(scenes, audio_duration=45.0)

        assert len(result) == 3
        assert abs(sum(result) - 45.0) < 0.01
        # Ratio preserved: 1 : 2 : 3
        assert abs(result[1] / result[0] - 2.0) < 0.01
        assert abs(result[2] / result[0] - 3.0) < 0.01

    def test_scale_durations_even_when_no_estimates(self):
        """Scenes with no duration_estimate get equal shares."""
        c = self._composer()
        scenes = [{}, {}, {}]
        result = c._scale_durations(scenes, audio_duration=30.0)

        assert len(result) == 3
        assert all(abs(d - 10.0) < 0.01 for d in result)

    def test_scale_durations_single_scene(self):
        """Single scene gets the full audio duration."""
        c = self._composer()
        result = c._scale_durations([{"duration_estimate": 5.0}], 45.0)
        assert abs(result[0] - 45.0) < 0.01

    def test_scale_durations_ignores_zero_total(self):
        """Handles edge case where all duration_estimates are 0."""
        c = self._composer()
        scenes = [{"duration_estimate": 0}, {"duration_estimate": 0}]
        result = c._scale_durations(scenes, audio_duration=20.0)
        assert abs(sum(result) - 20.0) < 0.01


# ------------------------------------------------------------------ #
#  VideoComposer – pipeline orchestration tests                       #
# ------------------------------------------------------------------ #

class TestVideoComposerPipeline:

    def _make_mock_audio_clip(self, duration: float = 30.0):
        """Build a mock AudioFileClip."""
        mock = MagicMock()
        mock.duration = duration
        mock.subclipped.return_value = mock
        mock.close.return_value = None
        return mock

    def _make_mock_video_clip(self, duration: float = 10.0):
        """Build a mock VideoClip that supports chaining."""
        mock = MagicMock()
        mock.duration = duration
        mock.crossfadein.return_value = mock
        mock.crossfadeout.return_value = mock
        mock.with_audio.return_value = mock
        mock.subclipped.return_value = mock
        mock.write_videofile.return_value = None
        mock.close.return_value = None
        mock.get_frame.return_value = np.full((1920, 1080, 3), 100, dtype=np.uint8)
        return mock

    def test_compose_calls_motion_engine_per_scene(self, tmp_path):
        """MotionEngine.animate is called once per scene."""
        from src.video.video_composer import VideoComposer

        n_scenes  = 3
        scenes    = _make_scenes(n_scenes)
        images    = [_make_png(tmp_path, f"s{i}.png") for i in range(n_scenes)]
        audio     = _make_audio(tmp_path)

        composer  = VideoComposer()
        mock_clip = self._make_mock_video_clip(10.0)

        with patch("src.video.video_composer.AudioFileClip",
                   return_value=self._make_mock_audio_clip(30.0)):
            with patch.object(composer._motion, "animate",
                               return_value=mock_clip) as mock_animate:
                with patch.object(composer._overlay, "apply",
                                   return_value=mock_clip):
                    with patch.object(composer._sub, "render",
                                       return_value=mock_clip):
                        with patch("src.video.video_composer.concatenate_videoclips",
                                   return_value=mock_clip):
                            # Mock write_videofile to create output file
                            mock_clip.write_videofile.side_effect = (
                                lambda p, **kw: Path(p).touch()
                            )
                            composer.compose(
                                scenes=scenes,
                                image_paths=images,
                                audio_path=audio,
                                word_segments=[],
                                video_id="test_vid",
                                output_path=tmp_path / "out.mp4",
                            )

        assert mock_animate.call_count == n_scenes

    def test_compose_calls_overlay_engine_per_clip(self, tmp_path):
        """OverlayEngine.apply is called once per scene clip."""
        from src.video.video_composer import VideoComposer

        n_scenes  = 2
        scenes    = _make_scenes(n_scenes)
        images    = [_make_png(tmp_path, f"s{i}.png") for i in range(n_scenes)]
        audio     = _make_audio(tmp_path)

        composer  = VideoComposer()
        mock_clip = self._make_mock_video_clip(15.0)

        with patch("src.video.video_composer.AudioFileClip",
                   return_value=self._make_mock_audio_clip(30.0)):
            with patch.object(composer._motion, "animate",
                               return_value=mock_clip):
                with patch.object(composer._overlay, "apply",
                                   return_value=mock_clip) as mock_overlay:
                    with patch.object(composer._sub, "render",
                                       return_value=mock_clip):
                        with patch("src.video.video_composer.concatenate_videoclips",
                                   return_value=mock_clip):
                            mock_clip.write_videofile.side_effect = (
                                lambda p, **kw: Path(p).touch()
                            )
                            composer.compose(
                                scenes=scenes,
                                image_paths=images,
                                audio_path=audio,
                                word_segments=[],
                                video_id="test_vid",
                                output_path=tmp_path / "out.mp4",
                            )

        assert mock_overlay.call_count == n_scenes

    def test_compose_calls_subtitle_renderer_when_segments_provided(self, tmp_path):
        """SubtitleRenderer.render is called when word_segments is non-empty."""
        from src.video.video_composer import VideoComposer

        scenes   = _make_scenes(2)
        images   = [_make_png(tmp_path, f"s{i}.png") for i in range(2)]
        audio    = _make_audio(tmp_path)
        segs     = _make_word_segments(4)

        composer  = VideoComposer()
        mock_clip = self._make_mock_video_clip(15.0)

        with patch("src.video.video_composer.AudioFileClip",
                   return_value=self._make_mock_audio_clip(20.0)):
            with patch.object(composer._motion, "animate", return_value=mock_clip):
                with patch.object(composer._overlay, "apply", return_value=mock_clip):
                    with patch.object(composer._sub, "render",
                                       return_value=mock_clip) as mock_sub:
                        with patch("src.video.video_composer.concatenate_videoclips",
                                   return_value=mock_clip):
                            mock_clip.write_videofile.side_effect = (
                                lambda p, **kw: Path(p).touch()
                            )
                            composer.compose(
                                scenes=scenes,
                                image_paths=images,
                                audio_path=audio,
                                word_segments=segs,
                                video_id="test_vid",
                                output_path=tmp_path / "out.mp4",
                            )

        mock_sub.assert_called_once()

    def test_compose_skips_subtitle_renderer_when_no_segments(self, tmp_path):
        """SubtitleRenderer.render is NOT called with an empty segment list."""
        from src.video.video_composer import VideoComposer

        scenes   = _make_scenes(2)
        images   = [_make_png(tmp_path, f"s{i}.png") for i in range(2)]
        audio    = _make_audio(tmp_path)

        composer  = VideoComposer()
        mock_clip = self._make_mock_video_clip(15.0)

        with patch("src.video.video_composer.AudioFileClip",
                   return_value=self._make_mock_audio_clip(20.0)):
            with patch.object(composer._motion, "animate", return_value=mock_clip):
                with patch.object(composer._overlay, "apply", return_value=mock_clip):
                    with patch.object(composer._sub, "render",
                                       return_value=mock_clip) as mock_sub:
                        with patch("src.video.video_composer.concatenate_videoclips",
                                   return_value=mock_clip):
                            mock_clip.write_videofile.side_effect = (
                                lambda p, **kw: Path(p).touch()
                            )
                            composer.compose(
                                scenes=scenes,
                                image_paths=images,
                                audio_path=audio,
                                word_segments=[],     # empty
                                video_id="test_vid",
                                output_path=tmp_path / "out.mp4",
                            )

        mock_sub.assert_not_called()

    def test_compose_raises_when_audio_missing(self, tmp_path):
        """FileNotFoundError raised if audio_path does not exist."""
        from src.video.video_composer import VideoComposer

        composer = VideoComposer()
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            composer.compose(
                scenes=_make_scenes(1),
                image_paths=[_make_png(tmp_path)],
                audio_path=tmp_path / "nonexistent.wav",
                word_segments=[],
                video_id="test",
                output_path=tmp_path / "out.mp4",
            )

    def test_compose_raises_when_image_missing(self, tmp_path):
        """FileNotFoundError raised if any image_path does not exist."""
        from src.video.video_composer import VideoComposer

        audio = _make_audio(tmp_path)
        composer = VideoComposer()

        with pytest.raises(FileNotFoundError, match="Scene image not found"):
            composer.compose(
                scenes=_make_scenes(1),
                image_paths=[tmp_path / "nonexistent.png"],
                audio_path=audio,
                word_segments=[],
                video_id="test",
                output_path=tmp_path / "out.mp4",
            )

    def test_compose_returns_output_path(self, tmp_path):
        """compose() returns the Path to the output MP4."""
        from src.video.video_composer import VideoComposer

        scenes   = _make_scenes(1)
        images   = [_make_png(tmp_path, "s0.png")]
        audio    = _make_audio(tmp_path)
        out_path = tmp_path / "result.mp4"

        composer  = VideoComposer()
        mock_clip = self._make_mock_video_clip(30.0)

        with patch("src.video.video_composer.AudioFileClip",
                   return_value=self._make_mock_audio_clip(30.0)):
            with patch.object(composer._motion, "animate", return_value=mock_clip):
                with patch.object(composer._overlay, "apply", return_value=mock_clip):
                    with patch("src.video.video_composer.concatenate_videoclips",
                               return_value=mock_clip):
                        mock_clip.write_videofile.side_effect = (
                            lambda p, **kw: Path(p).touch()
                        )
                        result = composer.compose(
                            scenes=scenes,
                            image_paths=images,
                            audio_path=audio,
                            word_segments=[],
                            video_id="test",
                            output_path=out_path,
                        )

        assert result == out_path

    def test_concat_single_clip_returns_directly(self):
        """_concat_with_crossfade with one clip returns it without wrapping."""
        from src.video.video_composer import VideoComposer

        composer = VideoComposer()
        clip     = _solid_clip(5.0)
        result   = composer._concat_with_crossfade([clip])

        assert result is clip


# ------------------------------------------------------------------ #
#  VideoValidator tests                                               #
# ------------------------------------------------------------------ #

def _make_probe_output(
    duration: float = 45.0,
    width:    int   = 1080,
    height:   int   = 1920,
    vcodec:   str   = "h264",
    has_audio: bool = True,
) -> str:
    """Build fake ffprobe JSON output."""
    streams = [
        {
            "codec_type": "video",
            "codec_name": vcodec,
            "width": width,
            "height": height,
        }
    ]
    if has_audio:
        streams.append({
            "codec_type": "audio",
            "codec_name": "aac",
            "sample_rate": "44100",
        })
    return json.dumps({
        "format": {"duration": str(duration)},
        "streams": streams,
    })


class TestVideoValidator:

    def _validator(self):
        from src.video.video_validator import VideoValidator
        return VideoValidator()

    def test_validate_passes_for_valid_video(self, tmp_path):
        """Valid video (correct duration, resolution, codecs) passes all gates."""
        p = tmp_path / "good.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))  # 1 MB

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=_make_probe_output(), stderr=""
            )
            result = v.validate(p)

        assert result.valid is True
        assert result.errors == []

    def test_validate_fails_file_not_found(self, tmp_path):
        """Missing file → valid=False immediately."""
        v = self._validator()
        result = v.validate(tmp_path / "missing.mp4")

        assert result.valid is False
        assert any("not found" in e.lower() for e in result.errors)

    def test_validate_fails_empty_file(self, tmp_path):
        """Zero-byte file → error."""
        p = tmp_path / "empty.mp4"
        p.write_bytes(b"")

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=_make_probe_output(), stderr=""
            )
            result = v.validate(p)

        assert not result.valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_fails_duration_too_short(self, tmp_path):
        """Duration < 15 s → error."""
        p = tmp_path / "short.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(duration=8.0),
                stderr="",
            )
            result = v.validate(p)

        assert not result.valid
        assert any("too short" in e.lower() for e in result.errors)

    def test_validate_fails_duration_too_long(self, tmp_path):
        """Duration > 65 s → error."""
        p = tmp_path / "long.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(duration=90.0),
                stderr="",
            )
            result = v.validate(p)

        assert not result.valid
        assert any("too long" in e.lower() for e in result.errors)

    def test_validate_fails_wrong_resolution(self, tmp_path):
        """Non-1080×1920 resolution → error."""
        p = tmp_path / "wrong_res.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(width=1920, height=1080),  # landscape
                stderr="",
            )
            result = v.validate(p)

        assert not result.valid
        assert any("resolution" in e.lower() for e in result.errors)

    def test_validate_fails_no_audio_stream(self, tmp_path):
        """Missing audio track → error."""
        p = tmp_path / "silent.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(has_audio=False),
                stderr="",
            )
            result = v.validate(p)

        assert not result.valid
        assert any("audio" in e.lower() for e in result.errors)

    def test_validate_warns_non_h264_codec(self, tmp_path):
        """Non-H.264 video codec triggers a warning (not an error)."""
        p = tmp_path / "hevc.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(vcodec="hevc"),
                stderr="",
            )
            result = v.validate(p)

        # Should still be valid (warning, not error) assuming other gates pass
        assert result.valid is True
        assert any("h.264" in w.lower() or "h264" in w.lower() for w in result.warnings)

    def test_validate_passes_without_ffprobe(self, tmp_path):
        """If ffprobe is unavailable, file-size checks still run and warn."""
        p = tmp_path / "noprobe.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))  # 1 MB, so no size error

        v = self._validator()

        with patch("subprocess.run", side_effect=FileNotFoundError("ffprobe")):
            result = v.validate(p)

        # Should not fail hard; just warns about ffprobe
        assert any("ffprobe" in w.lower() for w in result.warnings)

    def test_validate_info_dict_populated(self, tmp_path):
        """ValidationResult.info contains duration, resolution, codecs."""
        p = tmp_path / "info.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=_make_probe_output(duration=42.5, width=1080, height=1920),
                stderr="",
            )
            result = v.validate(p)

        assert result.info["duration_s"]  == 42.5
        assert result.info["width"]       == 1080
        assert result.info["height"]      == 1920
        assert result.info["video_codec"] == "h264"

    def test_validation_result_str_shows_pass(self, tmp_path):
        """str(ValidationResult) shows [PASS] for a valid result."""
        p = tmp_path / "pass.mp4"
        p.write_bytes(b"\x00" * (1024 * 1024))

        v = self._validator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=_make_probe_output(), stderr=""
            )
            result = v.validate(p)

        assert "[PASS]" in str(result)

    def test_validation_result_str_shows_fail(self, tmp_path):
        """str(ValidationResult) shows [FAIL] for an invalid result."""
        result = self._validator().validate(tmp_path / "ghost.mp4")
        assert "[FAIL]" in str(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
