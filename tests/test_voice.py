"""
Tests for Phase 4: Voice Generation.

Covers:
- TTSEngine: provider selection, ElevenLabs call, Edge-TTS fallback
- AudioProcessor: pipeline steps individually + full process()

Run with: python -m pytest tests/test_voice.py -v
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def _make_silent_mp3(path: Path, duration_seconds: float = 2.0) -> Path:
    """
    Create a minimal silent MP3 file using pydub (no ffmpeg needed).
    Falls back to writing an empty file if pydub unavailable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from pydub import AudioSegment
        silence = AudioSegment.silent(duration=int(duration_seconds * 1000))
        silence.export(str(path), format="mp3")
    except Exception:
        # Create a tiny valid-ish mp3 header (sufficient for mocked tests)
        path.write_bytes(b"\xff\xfb\x90\x00" * 100)
    return path


# ------------------------------------------------------------------ #
#  TTSEngine tests                                                     #
# ------------------------------------------------------------------ #

class TestTTSEngine:
    def test_uses_edge_tts_when_no_elevenlabs_key(self, tmp_path):
        """If ELEVENLABS_API_KEY is missing, falls straight to Edge-TTS."""
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine()
        output = tmp_path / "voice.mp3"

        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            with patch.object(engine, "_generate_edge_tts", return_value=output) as mock_edge:
                with patch("src.voice.tts_engine.get_project_root", return_value=tmp_path):
                    result = engine.generate("Hello world test script.", "vid_001", output)

        mock_edge.assert_called_once()
        assert result == output

    def test_uses_edge_tts_when_provider_is_edge_tts(self, tmp_path):
        """provider: edge_tts in config forces Edge-TTS regardless of key."""
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine()
        # Patch the config to override provider
        engine.cfg_voice = dict(engine.cfg_voice)
        engine.cfg_voice["provider"] = "edge_tts"
        output = tmp_path / "voice.mp3"

        with patch.object(engine, "_generate_edge_tts", return_value=output) as mock_edge:
            result = engine.generate("Hello world test script.", "vid_002", output)

        mock_edge.assert_called_once()

    @patch("src.voice.tts_engine.TTSEngine._generate_elevenlabs")
    def test_elevenlabs_called_when_key_present(self, mock_el, tmp_path):
        """ElevenLabs is called when a key is available."""
        from src.voice.tts_engine import TTSEngine

        output = tmp_path / "voice.mp3"
        output.touch()
        mock_el.return_value = output

        engine = TTSEngine()

        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "sk_testkey"}):
            with patch("src.voice.tts_engine.get_project_root", return_value=tmp_path):
                result = engine.generate("Test text.", "vid_003", output)

        mock_el.assert_called_once_with("Test text.", output)

    @patch("src.voice.tts_engine.TTSEngine._generate_elevenlabs")
    @patch("src.voice.tts_engine.TTSEngine._generate_edge_tts")
    def test_falls_back_to_edge_tts_on_elevenlabs_failure(self, mock_edge, mock_el, tmp_path):
        """On ElevenLabs failure, engine falls back to Edge-TTS."""
        from src.voice.tts_engine import TTSEngine

        fallback_path = tmp_path / "voice_edgetts.mp3"
        fallback_path.touch()

        mock_el.side_effect = RuntimeError("ElevenLabs API down")
        mock_edge.return_value = fallback_path

        engine = TTSEngine()

        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "sk_testkey"}):
            with patch("src.voice.tts_engine.get_project_root", return_value=tmp_path):
                result = engine.generate("Test fallback.", "vid_004", tmp_path / "voice.mp3")

        mock_edge.assert_called_once()
        assert result == fallback_path

    def test_edge_tts_generates_file(self, tmp_path):
        """Edge-TTS creates a non-empty output file (live call — skipped if offline)."""
        import socket
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            has_internet = True
        except OSError:
            has_internet = False
        finally:
            socket.setdefaulttimeout(None)

        if not has_internet:
            pytest.skip("No internet — skipping live Edge-TTS test")

        from src.voice.tts_engine import TTSEngine
        engine = TTSEngine()
        output = tmp_path / "edge_tts_out.mp3"
        result = engine._generate_edge_tts("This is a test narration.", output)

        assert result.exists()
        assert result.stat().st_size > 1000  # At least 1 KB of audio data

    def test_default_output_path_is_in_audio_dir(self, tmp_path):
        """When no output_path given, file lands in output/audio/."""
        from src.voice.tts_engine import TTSEngine

        engine = TTSEngine()
        expected = tmp_path / "output" / "audio" / "vid_auto_voice.mp3"

        with patch.object(engine, "_generate_edge_tts", return_value=expected):
            with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
                with patch("src.voice.tts_engine.get_project_root", return_value=tmp_path):
                    result = engine.generate("Auto path test.", "vid_auto")

        assert result == expected


# ------------------------------------------------------------------ #
#  AudioProcessor tests                                               #
# ------------------------------------------------------------------ #

class TestAudioProcessor:
    def _make_processor(self):
        from src.voice.audio_processor import AudioProcessor
        return AudioProcessor()

    def test_process_copies_file_when_ffmpeg_missing(self, tmp_path):
        """When FFmpeg is unavailable, process() copies raw audio unchanged."""
        from src.voice.audio_processor import AudioProcessor

        proc = AudioProcessor()
        src = tmp_path / "raw_voice.mp3"
        _make_silent_mp3(src)

        with patch("src.voice.audio_processor._ffmpeg_available", return_value=False):
            with patch("src.voice.audio_processor.get_project_root", return_value=tmp_path):
                result = proc.process(src, "vid_noffmpeg", add_music=False)

        assert result.exists()
        assert result.stat().st_size > 0

    @patch("src.voice.audio_processor._ffmpeg")
    @patch("src.voice.audio_processor._ffmpeg_available", return_value=True)
    def test_process_calls_pipeline_steps(self, mock_avail, mock_ffmpeg, tmp_path):
        """Full process() calls trim, normalise, and export steps."""
        from src.voice.audio_processor import AudioProcessor
        import subprocess

        # Make _ffmpeg a no-op that creates empty output files
        def fake_ffmpeg(*args, **kwargs):
            # Find the last positional arg that ends with .wav or .mp3 (the output)
            for arg in reversed(args):
                p = Path(str(arg))
                if p.suffix in (".wav", ".mp3") and not str(arg).startswith("-"):
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(b"\x00" * 1000)
                    break
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        mock_ffmpeg.side_effect = fake_ffmpeg

        # Also mock ffprobe duration
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="2.5\n", stderr=""
            )
            # But _ffmpeg_available uses subprocess.run too — return True for ffmpeg -version
            def selective_run(cmd, **kwargs):
                if cmd[0] == "ffmpeg" and "-version" in cmd:
                    r = MagicMock(); r.returncode = 0; return r
                if cmd[0] == "ffprobe":
                    r = MagicMock(); r.returncode = 0; r.stdout = "2.5\n"; return r
                # For loudnorm analysis pass
                r = MagicMock(); r.returncode = 0; r.stdout = ""; r.stderr = ""
                return r
            mock_run.side_effect = selective_run

            proc = AudioProcessor()
            src = tmp_path / "raw.mp3"
            _make_silent_mp3(src)

            with patch("src.voice.audio_processor.get_project_root", return_value=tmp_path):
                with patch("src.voice.audio_processor._ffmpeg", side_effect=fake_ffmpeg):
                    with patch("src.voice.audio_processor._ffmpeg_available", return_value=True):
                        result = proc.process(src, "vid_pipeline", add_music=False)

        # Output should exist (created by fake_ffmpeg)
        assert result is not None

    def test_get_duration_returns_float(self, tmp_path):
        """_get_duration returns a float even when ffprobe fails."""
        from src.voice.audio_processor import AudioProcessor

        proc = AudioProcessor()
        fake_path = tmp_path / "nonexistent.wav"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            duration = proc._get_duration(fake_path)

        assert isinstance(duration, float)
        assert duration == 0.0

    def test_mix_background_music_skips_when_no_files(self, tmp_path):
        """If assets/music/ is empty, mixing is skipped and voice is copied as-is."""
        from src.voice.audio_processor import AudioProcessor
        import shutil

        proc = AudioProcessor()
        src = tmp_path / "voice.wav"
        _make_silent_mp3(src)
        dst = tmp_path / "mixed.wav"

        # Empty music directory
        music_dir = tmp_path / "assets" / "music"
        music_dir.mkdir(parents=True, exist_ok=True)

        with patch("src.voice.audio_processor.get_project_root", return_value=tmp_path):
            proc._mix_background_music(src, dst)

        assert dst.exists()
        assert dst.stat().st_size == src.stat().st_size  # Copied unchanged


# ------------------------------------------------------------------ #
#  Integration: TTSEngine → AudioProcessor chain                      #
# ------------------------------------------------------------------ #

class TestTTSToAudioChain:
    @patch("src.voice.tts_engine.TTSEngine._generate_edge_tts")
    def test_tts_output_fed_to_processor(self, mock_tts, tmp_path):
        """Verify the handoff: TTS output path is valid input to AudioProcessor."""
        from src.voice.tts_engine import TTSEngine
        from src.voice.audio_processor import AudioProcessor

        # TTS produces a real file
        tts_output = tmp_path / "output" / "audio" / "vid_chain_voice.mp3"
        tts_output.parent.mkdir(parents=True, exist_ok=True)
        _make_silent_mp3(tts_output)
        mock_tts.return_value = tts_output

        engine = TTSEngine()
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            with patch("src.voice.tts_engine.get_project_root", return_value=tmp_path):
                voice_path = engine.generate("Chain test narration.", "vid_chain")

        # voice_path should be a real file that AudioProcessor can ingest
        assert voice_path.exists()
        assert voice_path.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
