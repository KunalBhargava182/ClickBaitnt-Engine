"""
TTS Engine — ElevenLabs (primary) + Edge-TTS (free fallback).

Unified interface: generate(text, output_path) → Path to .mp3
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log
from src.utils.retry import with_retry


class TTSEngine:
    """
    Text-to-speech engine with automatic fallback.

    Primary  : ElevenLabs API  (sk_... key in .env)
    Fallback : Edge-TTS        (free, runs locally via Microsoft Edge neural voices)

    Both produce .mp3 output.  AudioProcessor downstream normalises format.
    """

    def __init__(self):
        cfg = get_config()
        self.cfg_voice = cfg.voice
        self._el_client = None

    # ---------------------------------------------------------------- #
    #  ElevenLabs                                                       #
    # ---------------------------------------------------------------- #

    def _get_elevenlabs_client(self):
        """Lazy-init ElevenLabs client."""
        if self._el_client is None:
            from elevenlabs.client import ElevenLabs
            key = os.environ.get("ELEVENLABS_API_KEY", "")
            if not key:
                raise ValueError("ELEVENLABS_API_KEY not set")
            self._el_client = ElevenLabs(api_key=key)
        return self._el_client

    @with_retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,))
    def _generate_elevenlabs(self, text: str, output_path: Path) -> Path:
        """
        Generate speech via ElevenLabs and save to output_path.

        Args:
            text: Narration script text.
            output_path: Destination .mp3 file path.

        Returns:
            output_path on success.
        """
        # VoiceSettings import works in both v1.x and v2.x
        try:
            from elevenlabs import VoiceSettings
        except ImportError:
            from elevenlabs.types import VoiceSettings  # type: ignore[no-redef]

        client = self._get_elevenlabs_client()
        el_cfg = self.cfg_voice["elevenlabs"]

        log.info(
            "tts_engine.elevenlabs.generating",
            voice_id=el_cfg["voice_id"],
            chars=len(text),
        )

        audio_stream = client.text_to_speech.convert(
            voice_id=el_cfg["voice_id"],
            text=text,
            model_id=el_cfg["model_id"],
            voice_settings=VoiceSettings(
                stability=float(el_cfg["stability"]),
                similarity_boost=float(el_cfg["similarity_boost"]),
            ),
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        size_kb = output_path.stat().st_size / 1024
        log.info(
            "tts_engine.elevenlabs.done",
            path=str(output_path),
            size_kb=round(size_kb, 1),
        )
        return output_path

    # ---------------------------------------------------------------- #
    #  Edge-TTS (free fallback)                                         #
    # ---------------------------------------------------------------- #

    def _generate_edge_tts(self, text: str, output_path: Path, language: str = "en") -> Path:
        """
        Generate speech via Edge-TTS (free, no API key needed).

        Args:
            text:       Narration script text.
            output_path: Destination .mp3 file path.
            language:   "en" | "hi" | "hinglish" — selects the neural voice.

        Returns:
            output_path on success.
        """
        import edge_tts

        edge_cfg = self.cfg_voice["edge_tts"]
        rate  = edge_cfg.get("rate",  "+5%")
        pitch = edge_cfg.get("pitch", "+0Hz")

        # Pick voice by language — Hindi/Hinglish use native Indian neural voice
        if language in ("hi", "hinglish"):
            voice = "hi-IN-MadhurNeural"   # male, natural Hindi/Hinglish delivery
        else:
            voice = edge_cfg.get("voice", "en-US-GuyNeural")

        log.info("tts_engine.edge_tts.generating", voice=voice, chars=len(text))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        async def _run():
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
            await communicate.save(str(output_path))

        asyncio.run(_run())

        size_kb = output_path.stat().st_size / 1024
        log.info(
            "tts_engine.edge_tts.done",
            path=str(output_path),
            size_kb=round(size_kb, 1),
        )
        return output_path

    # ---------------------------------------------------------------- #
    #  Audio duration helper                                            #
    # ---------------------------------------------------------------- #

    def _get_duration(self, audio_path: Path) -> float:
        """Return audio duration in seconds using mutagen or pydub fallback."""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            return audio.info.length
        except Exception:
            pass

        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(str(audio_path))
            return len(seg) / 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def generate(self, text: str, video_id: str, output_path: Optional[Path] = None,
                 language: str = "en") -> Path:
        """
        Generate narration audio for the given script text.

        For Hindi / Hinglish, always uses Edge-TTS with the native Indian voice
        (hi-IN-MadhurNeural) — ElevenLabs English voices sound accented in Hindi.
        For English, tries ElevenLabs first, falls back to Edge-TTS.

        Args:
            text:        Full narration script.
            video_id:    Used to name the output file if output_path not given.
            output_path: Optional explicit output path.
            language:    "en" | "hi" | "hinglish"

        Returns:
            Path to the generated .mp3 file.

        Raises:
            RuntimeError: If both providers fail.
        """
        if output_path is None:
            audio_dir = get_project_root() / "output" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            output_path = audio_dir / f"{video_id}_voice.mp3"

        # Hindi / Hinglish — always use native Edge-TTS voice
        if language in ("hi", "hinglish"):
            log.info("tts_engine.using_edge_tts_hindi", language=language)
            return self._generate_edge_tts(text, output_path, language=language)

        provider = self.cfg_voice.get("provider", "elevenlabs")
        el_key = os.environ.get("ELEVENLABS_API_KEY", "")
        has_elevenlabs = bool(el_key) and not el_key.startswith("sk_xxx")

        # If provider is edge_tts or no ElevenLabs key, go straight to Edge-TTS
        if provider == "edge_tts" or not has_elevenlabs:
            log.info("tts_engine.using_edge_tts")
            return self._generate_edge_tts(text, output_path, language=language)

        # Try ElevenLabs, fall back to Edge-TTS
        try:
            result = self._generate_elevenlabs(text, output_path)
            duration = self._get_duration(result)
            log.info("tts_engine.generate.done", provider="elevenlabs", duration_s=round(duration, 1))
            return result
        except Exception as exc:
            log.warning(
                "tts_engine.elevenlabs_failed_falling_back",
                error=str(exc),
            )
            fallback_path = output_path.with_stem(output_path.stem + "_edgetts")
            result = self._generate_edge_tts(text, fallback_path, language=language)
            duration = self._get_duration(result)
            log.info("tts_engine.generate.done", provider="edge_tts", duration_s=round(duration, 1))
            return result
