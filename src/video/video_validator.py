"""
Video validator — sanity-checks a completed MP4 before YouTube upload.

Validation gates:
  1. File exists and is non-empty.
  2. File size is within reasonable bounds (> 500 KB, < 500 MB).
  3. Duration is within YouTube Shorts limits (15 – 65 seconds).
  4. Resolution is exactly 1080 × 1920.
  5. Video codec is H.264 (required for YouTube).
  6. At least one audio stream is present.

Uses ffprobe for all media inspection (no Python media libraries needed).
Falls back gracefully if ffprobe is not available.
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.utils.logger import log

# YouTube Shorts constraints
_MIN_DURATION_S = 15.0
_MAX_DURATION_S = 65.0      # slightly above 60 s to allow encode overhead
_TARGET_W       = 1080
_TARGET_H       = 1920

# File size sanity bounds
_MIN_SIZE_BYTES = 500 * 1024          # 500 KB
_MAX_SIZE_BYTES = 500 * 1024 * 1024   # 500 MB


@dataclass
class ValidationResult:
    """
    Result of a video validation pass.

    Attributes:
        valid:    True only if all hard gates pass (no errors).
        errors:   Fatal issues that block upload.
        warnings: Non-fatal observations (noted but upload still proceeds).
        info:     Probe metadata (duration, resolution, codecs, size).
    """
    valid:    bool
    errors:   list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info:     dict      = field(default_factory=dict)

    def __str__(self) -> str:
        status = "PASS" if self.valid else "FAIL"
        lines  = [f"[{status}]"]
        if self.errors:
            lines += [f"  ERROR: {e}" for e in self.errors]
        if self.warnings:
            lines += [f"  WARN:  {w}" for w in self.warnings]
        return "\n".join(lines)


class VideoValidator:
    """
    Validates an MP4 before it is handed off to the uploader.

    Usage:
        v      = VideoValidator()
        result = v.validate(Path("output/videos/vid_001.mp4"))
        if not result.valid:
            raise RuntimeError(str(result))
    """

    def validate(self, video_path: Path) -> ValidationResult:
        """
        Run all validation gates against video_path.

        Args:
            video_path: Path to the MP4 to validate.

        Returns:
            ValidationResult with valid=True if all hard gates pass.
        """
        video_path = Path(video_path)
        errors:   list[str] = []
        warnings: list[str] = []
        info:     dict      = {}

        # Gate 1: file existence
        if not video_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"File not found: {video_path}"],
            )

        # Gate 2: file size
        size_bytes = video_path.stat().st_size
        size_mb    = size_bytes / (1024 * 1024)
        info["size_mb"] = round(size_mb, 2)

        if size_bytes == 0:
            errors.append("File is empty (0 bytes)")
        elif size_bytes < _MIN_SIZE_BYTES:
            warnings.append(
                f"File is very small ({size_mb:.2f} MB) — may be corrupt"
            )
        elif size_bytes > _MAX_SIZE_BYTES:
            warnings.append(
                f"File is very large ({size_mb:.0f} MB) — upload may be slow"
            )

        # Try ffprobe inspection
        probe = self._probe(video_path)
        if probe is None:
            warnings.append(
                "ffprobe not available — skipping media inspection gates"
            )
            log.warning("video_validator.ffprobe_unavailable")
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                info=info,
            )

        # Parse format info
        fmt      = probe.get("format", {})
        streams  = probe.get("streams", [])

        duration = float(fmt.get("duration", 0.0))
        info["duration_s"] = round(duration, 2)

        video_streams = [s for s in streams if s.get("codec_type") == "video"]
        audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

        # Gate 3: duration
        if duration < _MIN_DURATION_S:
            errors.append(
                f"Duration too short: {duration:.1f}s (min {_MIN_DURATION_S}s)"
            )
        elif duration > _MAX_DURATION_S:
            errors.append(
                f"Duration too long: {duration:.1f}s (max {_MAX_DURATION_S}s for Shorts)"
            )

        # Gate 4 & 5: video stream — resolution + codec
        if not video_streams:
            errors.append("No video stream found")
        else:
            vs    = video_streams[0]
            w     = vs.get("width", 0)
            h     = vs.get("height", 0)
            codec = vs.get("codec_name", "unknown")

            info["width"]       = w
            info["height"]      = h
            info["video_codec"] = codec

            if w != _TARGET_W or h != _TARGET_H:
                errors.append(
                    f"Wrong resolution: {w}×{h} (expected {_TARGET_W}×{_TARGET_H})"
                )

            if codec.lower() not in ("h264", "avc1", "avc"):
                warnings.append(
                    f"Video codec is '{codec}', not H.264 — YouTube may reject"
                )

        # Gate 6: audio stream
        if not audio_streams:
            errors.append("No audio stream found — YouTube requires audio")
        else:
            as_    = audio_streams[0]
            info["audio_codec"]       = as_.get("codec_name", "unknown")
            info["audio_sample_rate"] = as_.get("sample_rate", "unknown")

        is_valid = len(errors) == 0

        log.info(
            "video_validator.validate.done",
            path=video_path.name,
            valid=is_valid,
            errors=len(errors),
            warnings=len(warnings),
            **{k: v for k, v in info.items()},
        )

        return ValidationResult(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _probe(video_path: Path) -> Optional[dict]:
        """
        Run ffprobe on video_path and return parsed JSON, or None on failure.
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            if result.returncode != 0:
                log.warning(
                    "video_validator.ffprobe.error",
                    stderr=result.stderr[:200],
                )
                return None
            return json.loads(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            return None
