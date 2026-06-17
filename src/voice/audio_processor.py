"""
Audio post-processor.

Pipeline:
  1. Trim silence from start/end
  2. Normalise to -14 LUFS  (YouTube standard)
  3. Mix in background music at 15% volume  (random pick from assets/music/)
  4. Apply gentle dynamic range compression
  5. Export as 44100 Hz stereo WAV (MoviePy-compatible)

Requires FFmpeg to be installed and on PATH.
"""

import os
import random
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from src.utils.config_loader import get_project_root
from src.utils.logger import log


def _ffmpeg(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run an ffmpeg command, raising on non-zero exit."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + list(args)
    log.debug("audio_processor.ffmpeg", cmd=" ".join(cmd))
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def _ffmpeg_available() -> bool:
    """Return True if ffmpeg is on PATH."""
    result = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


class AudioProcessor:
    """
    Post-processes generated TTS audio into a broadcast-ready WAV.

    Output spec:
        - Format    : WAV  (PCM 16-bit)
        - Sample rate: 44 100 Hz
        - Channels  : 2 (stereo)
        - Loudness  : -14 LUFS (YouTube standard)
        - Music     : 15% of voice level, auto-faded
    """

    MUSIC_VOLUME    = 0.15      # 15% relative to normalised voice
    TARGET_LUFS     = -14.0
    TRUE_PEAK       = -1.0      # dBTP ceiling
    LRA             = 11.0      # Loudness range target
    MAX_DURATION_S  = 63.0      # Hard ceiling; atempo speeds up audio that exceeds this

    def __init__(self):
        if not _ffmpeg_available():
            log.warning(
                "audio_processor.ffmpeg_missing",
                message="FFmpeg not found on PATH — audio processing will be limited",
            )

    # ---------------------------------------------------------------- #
    #  Step helpers                                                     #
    # ---------------------------------------------------------------- #

    def _trim_silence(self, src: Path, dst: Path) -> Path:
        """
        Remove silence from start and end of audio.
        Uses silenceremove filter: stops when > 50 dB below peak.
        """
        _ffmpeg(
            "-i", str(src),
            "-af",
            "silenceremove=start_periods=1:start_silence=0.3:start_threshold=-50dB"
            ":stop_periods=-1:stop_silence=0.3:stop_threshold=-50dB",
            str(dst),
        )
        log.debug("audio_processor.trim_silence.done", dst=str(dst))
        return dst

    def _normalise_lufs(self, src: Path, dst: Path) -> Path:
        """
        Two-pass loudnorm to hit exactly TARGET_LUFS.
        Pass 1 analyses; pass 2 applies with measured parameters.
        """
        # Pass 1: analyse
        probe = subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner",
                "-i", str(src),
                "-af", f"loudnorm=I={self.TARGET_LUFS}:TP={self.TRUE_PEAK}:LRA={self.LRA}:print_format=json",
                "-f", "null", "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Loudnorm prints JSON to stderr
        import json
        import re
        json_match = re.search(r"\{[^}]+\}", probe.stderr, re.DOTALL)
        if json_match:
            try:
                stats = json.loads(json_match.group())
                measured_i    = stats.get("input_i", str(self.TARGET_LUFS))
                measured_tp   = stats.get("input_tp", "0")
                measured_lra  = stats.get("input_lra", str(self.LRA))
                measured_thresh = stats.get("input_thresh", "-70")

                # Pass 2: apply with measured values
                loudnorm_filter = (
                    f"loudnorm=I={self.TARGET_LUFS}:TP={self.TRUE_PEAK}:LRA={self.LRA}"
                    f":measured_I={measured_i}:measured_TP={measured_tp}"
                    f":measured_LRA={measured_lra}:measured_thresh={measured_thresh}"
                    f":linear=true:print_format=none"
                )
                _ffmpeg("-i", str(src), "-af", loudnorm_filter, str(dst))
                log.debug(
                    "audio_processor.normalise_lufs.done",
                    measured_i=measured_i,
                    target=self.TARGET_LUFS,
                )
                return dst
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: single-pass normalise if analysis failed
        log.warning("audio_processor.normalise_lufs.fallback_single_pass")
        _ffmpeg(
            "-i", str(src),
            "-af", f"loudnorm=I={self.TARGET_LUFS}:TP={self.TRUE_PEAK}:LRA={self.LRA}",
            str(dst),
        )
        return dst

    def _mix_background_music(self, voice: Path, dst: Path) -> Path:
        """
        Mix the voice track with a random background music file.
        Music is volume-reduced to MUSIC_VOLUME and faded out over the last 2 s.
        If no music files found, copies voice track unchanged.
        """
        music_dir = get_project_root() / "assets" / "music"
        music_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))

        if not music_files:
            log.info("audio_processor.mix_music.no_files_skipping")
            import shutil
            shutil.copy2(str(voice), str(dst))
            return dst

        music_path = random.choice(music_files)
        log.info(
            "audio_processor.mix_music",
            music=music_path.name,
            volume=self.MUSIC_VOLUME,
        )

        # Get voice duration for fade-out timing
        voice_dur = self._get_duration(voice)
        fade_start = max(0, voice_dur - 2.0)

        filter_complex = (
            f"[1:a]volume={self.MUSIC_VOLUME},"
            f"afade=t=out:st={fade_start:.2f}:d=2,"
            f"aloop=loop=-1:size=2e+09[bg];"   # loop music to match voice length
            f"[0:a][bg]amix=inputs=2:duration=first:normalize=0[out]"
        )

        _ffmpeg(
            "-i", str(voice),
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[out]",
            str(dst),
        )
        return dst

    def _get_duration(self, audio_path: Path) -> float:
        """Return audio duration in seconds via ffprobe."""
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            return float(result.stdout.strip())
        except ValueError:
            return 0.0

    def _fit_to_duration(self, src: Path, dst: Path) -> Path:
        """
        Speed up audio with atempo if it exceeds MAX_DURATION_S.
        Pitch is preserved; tempo is increased proportionally.
        atempo accepts values in [0.5, 100]; a single filter suffices up to ~2x.
        """
        duration = self._get_duration(src)
        if duration <= self.MAX_DURATION_S:
            import shutil
            shutil.copy2(str(src), str(dst))
            return dst

        rate = duration / self.MAX_DURATION_S
        log.info(
            "audio_processor.fit_duration.speeding_up",
            original_s=round(duration, 2),
            target_s=self.MAX_DURATION_S,
            atempo=round(rate, 4),
        )
        _ffmpeg(
            "-i", str(src),
            "-af", f"atempo={rate:.4f}",
            str(dst),
        )
        fitted = self._get_duration(dst)
        log.info("audio_processor.fit_duration.done", fitted_s=round(fitted, 2))
        return dst

    def _export_wav(self, src: Path, dst: Path) -> Path:
        """Convert to 44100 Hz stereo 16-bit WAV."""
        _ffmpeg(
            "-i", str(src),
            "-ar", "44100",
            "-ac", "2",
            "-sample_fmt", "s16",
            str(dst),
        )
        log.debug("audio_processor.export_wav.done", dst=str(dst))
        return dst

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def process(
        self,
        voice_path: Path,
        video_id: str,
        output_path: Optional[Path] = None,
        add_music: bool = True,
    ) -> Path:
        """
        Run the full audio post-processing pipeline.

        Args:
            voice_path: Path to the raw TTS .mp3 file.
            video_id: Used for temp file naming.
            output_path: Final WAV output path. Defaults to output/audio/{video_id}_final.wav.
            add_music: Whether to mix in background music.

        Returns:
            Path to the processed WAV file.
        """
        if output_path is None:
            audio_dir = get_project_root() / "output" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            output_path = audio_dir / f"{video_id}_final.wav"

        if not _ffmpeg_available():
            log.warning(
                "audio_processor.process.ffmpeg_missing",
                message="FFmpeg not available — copying raw audio without processing",
            )
            import shutil
            shutil.copy2(str(voice_path), str(output_path.with_suffix(".mp3")))
            return output_path.with_suffix(".mp3")

        with tempfile.TemporaryDirectory(prefix=f"ase_{video_id}_") as tmp:
            tmp_dir = Path(tmp)

            # Step 1: Trim silence
            trimmed = tmp_dir / "01_trimmed.wav"
            try:
                self._trim_silence(voice_path, trimmed)
            except Exception as exc:
                log.warning("audio_processor.trim_silence.failed", error=str(exc))
                import shutil
                shutil.copy2(str(voice_path), str(trimmed))

            # Step 2: LUFS normalisation
            normalised = tmp_dir / "02_normalised.wav"
            try:
                self._normalise_lufs(trimmed, normalised)
            except Exception as exc:
                log.warning("audio_processor.normalise.failed", error=str(exc))
                normalised = trimmed

            # Step 3: Mix background music
            mixed = tmp_dir / "03_mixed.wav"
            if add_music:
                try:
                    self._mix_background_music(normalised, mixed)
                except Exception as exc:
                    log.warning("audio_processor.mix_music.failed", error=str(exc))
                    mixed = normalised
            else:
                import shutil
                shutil.copy2(str(normalised), str(mixed))

            # Step 4: Speed-up if audio would exceed Shorts limit
            fitted = tmp_dir / "04_fitted.wav"
            try:
                self._fit_to_duration(mixed, fitted)
            except Exception as exc:
                log.warning("audio_processor.fit_duration.failed", error=str(exc))
                fitted = mixed

            # Step 5: Export final WAV
            self._export_wav(fitted, output_path)

        duration = self._get_duration(output_path)
        size_kb = output_path.stat().st_size / 1024
        log.info(
            "audio_processor.process.done",
            video_id=video_id,
            output=str(output_path),
            duration_s=round(duration, 2),
            size_kb=round(size_kb, 1),
        )
        return output_path
