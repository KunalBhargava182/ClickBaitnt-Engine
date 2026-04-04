"""
Whisper-based audio alignment.

Transcribes an audio file using the local openai-whisper model
(runs fully on-device, no API key required) and extracts word-level
timestamps.

Model size tradeoffs (config: subtitles.whisper_model):
  tiny   — fastest (~1 s/min audio),  lowest accuracy
  base   — fast    (~2 s/min audio),  good accuracy      ← default
  small  — medium  (~5 s/min audio),  better accuracy
  medium — slow    (~15 s/min audio), high accuracy
  large  — slowest (~30 s/min audio), best accuracy

Usage:
    aligner = WhisperAligner()
    segments = aligner.align(Path("output/audio/vid_001_final.wav"))
    # segments: list[WordSegment]
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src.utils.config_loader import get_config
from src.utils.logger import log


@dataclass
class WordSegment:
    """A single transcribed word with its timing boundaries."""
    word:  str
    start: float   # seconds from audio start
    end:   float   # seconds from audio start


class WhisperAligner:
    """
    Transcribes audio and returns word-level timestamps.

    The whisper model is lazy-loaded on the first call to align()
    so that import time stays fast.
    """

    def __init__(self) -> None:
        cfg = get_config()
        self._model_size: str = cfg.subtitles.get("whisper_model", "base")
        self._model = None  # loaded on first use

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def align(self, audio_path: Path, language: str = "en") -> list[WordSegment]:
        """
        Transcribe audio and return word-level segments.

        For Hindi audio (language="hi"), Whisper translates to English so the
        subtitle renderer gets English words with correct timestamps.
        For Hinglish (language="hinglish"), auto-detection handles the mix.
        For English (language="en"), standard transcription is used.

        Args:
            audio_path: Path to WAV or MP3 file.
            language:   "en" | "hi" | "hinglish"

        Returns:
            List of WordSegment in chronological order (always English text).

        Raises:
            FileNotFoundError: audio_path does not exist.
            RuntimeError: Whisper transcription failed.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        log.info("whisper_aligner.align.start", path=str(audio_path), language=language)

        model = self._get_model()

        # Build transcription kwargs based on language
        if language == "hi":
            # Translate Hindi audio → English subtitles
            transcribe_kwargs = dict(
                word_timestamps=True,
                language="hi",
                task="translate",   # translate to English
                fp16=False,
            )
        elif language == "hinglish":
            # Auto-detect — Whisper handles Roman Hindi+English mix well
            transcribe_kwargs = dict(
                word_timestamps=True,
                fp16=False,
            )
        else:
            transcribe_kwargs = dict(
                word_timestamps=True,
                language="en",
                fp16=False,
            )

        try:
            result = model.transcribe(str(audio_path), **transcribe_kwargs)
        except Exception as exc:
            raise RuntimeError(f"Whisper transcription failed: {exc}") from exc

        segments = self._extract_word_segments(result)

        # Fallback: if whisper returned no word-level data, distribute evenly
        if not segments:
            log.warning(
                "whisper_aligner.no_word_timestamps",
                hint="Falling back to even distribution",
            )
            segments = self._distribute_evenly(result)

        log.info(
            "whisper_aligner.align.done",
            audio=audio_path.name,
            words=len(segments),
        )
        return segments

    def save_json(self, segments: list[WordSegment], output_path: Path) -> Path:
        """
        Persist word segments to JSON (debugging / caching).

        Args:
            segments: List of WordSegment.
            output_path: Destination .json file.

        Returns:
            Path to the saved file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(s) for s in segments]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info("whisper_aligner.saved_json", path=str(output_path))
        return output_path

    @staticmethod
    def load_json(json_path: Path) -> list[WordSegment]:
        """
        Reload word segments from a previously saved JSON file.

        Args:
            json_path: Path to .json file created by save_json().

        Returns:
            List of WordSegment.
        """
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        return [WordSegment(**d) for d in data]

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get_model(self):
        """Return the cached Whisper model, loading it if necessary."""
        if self._model is None:
            try:
                import whisper
            except ImportError as exc:
                raise ImportError(
                    "openai-whisper is not installed. "
                    "Run: pip install openai-whisper"
                ) from exc

            log.info("whisper_aligner.loading_model", size=self._model_size)
            self._model = whisper.load_model(self._model_size)
            log.info("whisper_aligner.model_ready", size=self._model_size)

        return self._model

    def _extract_word_segments(self, result: dict) -> list[WordSegment]:
        """
        Pull word-level segments out of a Whisper transcription result.

        Whisper stores word timestamps inside each segment's "words" list
        when word_timestamps=True.
        """
        segments: list[WordSegment] = []

        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                word = w.get("word", "").strip()
                if not word:
                    continue
                segments.append(
                    WordSegment(
                        word=word,
                        start=float(w.get("start", 0.0)),
                        end=float(w.get("end", 0.0)),
                    )
                )

        return segments

    def _distribute_evenly(self, result: dict) -> list[WordSegment]:
        """
        Fallback: split the full transcript text into words and distribute
        them evenly across the audio duration inferred from segment timings.
        """
        text = result.get("text", "").strip()
        words = text.split()
        if not words:
            return []

        # Determine total duration from the last segment end time
        segs = result.get("segments", [])
        total_dur = segs[-1]["end"] if segs else len(words) * 0.4

        step = total_dur / len(words)
        return [
            WordSegment(
                word=w,
                start=round(i * step, 3),
                end=round((i + 1) * step, 3),
            )
            for i, w in enumerate(words)
        ]
