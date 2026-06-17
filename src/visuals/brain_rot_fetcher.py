"""
BrainRotFetcher — supplies the bottom-panel clip for split-screen mode.

Workflow:
  1. Scan assets/brain_rot_clips/ for ALL .mp4 files (manual + auto-downloaded).
  2. Manual clips (any file NOT matching *_[timestamp].mp4) are preferred first.
     Auto-downloaded clips are used as fallback when manual pool is exhausted.
  3. Only fetch a new clip from Pexels if the total pool has fewer than 3 clips.
  4. Anti-repeat: skip clips used in the last 5 selections (usage_log.json).
  5. Validate every candidate: skip clips under 8 s, delete corrupted ones.
  6. Trim or loop the raw clip to exactly ``duration`` seconds.
  7. Resize to 1080 × 768 (portrait crop if needed).
  8. Strip audio from the returned clip.
  9. On ANY failure: log the error and return None.
     The caller (VideoComposer) treats None as a signal to fall back to
     the standard fullscreen pipeline.

Environment:
  PEXELS_API_KEY  — loaded from .env via config_loader
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from pathlib import Path
from typing import Optional

import requests

from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log

# Pexels Video Search endpoint
_PEXELS_API_URL = "https://api.pexels.com/videos/search"

# Target output dimensions for the brain-rot panel
_OUT_W = 1080
_OUT_H = 768

# Minimum acceptable video height from Pexels (skip tiny files)
_MIN_VIDEO_HEIGHT = 720

# Minimum clip pool size before we call the Pexels API
_CACHE_HIT_THRESHOLD = 3

# Minimum clip duration in seconds — clips shorter than this are skipped
_MIN_CLIP_DURATION = 8.0

# How many recent selections to remember for anti-repeat
_ANTI_REPEAT_WINDOW = 5

# Pattern that matches auto-downloaded filenames: <slug>_<unix-timestamp>.mp4
_AUTO_PATTERN = re.compile(r'^.+_\d{9,10}\.mp4$')


def _slug(text: str) -> str:
    """Convert query string to a safe filename fragment."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


class BrainRotFetcher:
    """
    Fetches, caches, trims, and sizes a brain-rot background clip.

    Usage:
        clip = BrainRotFetcher().get_clip(duration_seconds)
        # clip is a muted MoviePy VideoFileClip (1080×768) or None on failure.
    """

    def __init__(self) -> None:
        cfg = get_config()
        ss  = cfg.get("splitscreen", {})

        self._categories: list[dict] = ss.get("brain_rot_categories", [])
        self._cache_dir  = get_project_root() / ss.get("clip_cache_dir", "assets/brain_rot_clips")
        self._max_cached: int = int(ss.get("max_cached_clips", 30))
        self._api_key: str   = os.environ.get("PEXELS_API_KEY", "")

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_clip(self, duration: float):
        """
        Return a muted MoviePy VideoFileClip (1080×768) lasting ``duration``
        seconds, or None if anything goes wrong.

        Args:
            duration: Exact length in seconds the clip must match.

        Returns:
            MoviePy VideoFileClip or None.
        """
        try:
            return self._get_clip(duration)
        except Exception as exc:
            log.error(
                "brain_rot_fetcher.unexpected_error",
                error=str(exc)[:200],
            )
            return None

    # ------------------------------------------------------------------ #
    #  Internal implementation                                            #
    # ------------------------------------------------------------------ #

    def _get_clip(self, duration: float):
        """Core logic — all errors propagate to get_clip() which catches them."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # 1. Scan entire folder for all .mp4 files
        manual, downloaded = self._scan_pool()
        total = len(manual) + len(downloaded)

        # 2. Download from Pexels only if pool is too small
        if total < _CACHE_HIT_THRESHOLD:
            if self._categories:
                category = self._pick_category()
                log.info(
                    "brain_rot_fetcher.fetching_new_clip",
                    query=category["query"],
                    pool_size=total,
                )
                new_path = self._fetch_from_pexels(category)
                if new_path:
                    downloaded.append(new_path)
                    self._prune_cache()
            if not manual and not downloaded:
                log.error("brain_rot_fetcher.empty_pool")
                return None

        # Print pool summary
        print(
            f"[BrainRot] Pool: {len(manual) + len(downloaded)} clips "
            f"({len(manual)} manual + {len(downloaded)} downloaded)"
        )

        # 3. Select clip with anti-repeat and validation
        chosen, clip_duration = self._select_from_pool(manual, downloaded)
        if chosen is None:
            log.error("brain_rot_fetcher.no_valid_clip_found")
            return None

        print(f"[BrainRot] Selected: {chosen.name} (duration: {clip_duration:.1f}s) ✓")

        # 4. Process (trim/loop + resize + mute)
        return self._process_clip(chosen, duration)

    def _pick_category(self) -> dict:
        """Weighted-random selection from brain_rot_categories."""
        weights = [float(c.get("weight", 1)) for c in self._categories]
        return random.choices(self._categories, weights=weights, k=1)[0]

    # ------------------------------------------------------------------ #
    #  Pool scanning                                                      #
    # ------------------------------------------------------------------ #

    def _is_auto_downloaded(self, path: Path) -> bool:
        """True if the filename matches the auto-download pattern <slug>_<timestamp>.mp4."""
        return bool(_AUTO_PATTERN.match(path.name))

    def _scan_pool(self) -> tuple[list[Path], list[Path]]:
        """
        Scan self._cache_dir for all .mp4 files.
        Returns (manual_clips, auto_downloaded_clips).
        """
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        manual: list[Path] = []
        downloaded: list[Path] = []
        for p in sorted(self._cache_dir.glob("*.mp4")):
            if self._is_auto_downloaded(p):
                downloaded.append(p)
            else:
                manual.append(p)
        return manual, downloaded

    # ------------------------------------------------------------------ #
    #  Selection                                                          #
    # ------------------------------------------------------------------ #

    def _select_from_pool(
        self, manual: list[Path], downloaded: list[Path]
    ) -> tuple[Optional[Path], float]:
        """
        Pick one valid clip, preferring manual over auto-downloaded.
        Skips recently used clips (anti-repeat window = last 5).
        Returns (path, duration_seconds) or (None, 0.0) if nothing valid.
        """
        recent = self._load_usage_log()

        def try_pool(candidates: list[Path]) -> tuple[Optional[Path], float]:
            not_recent = [p for p in candidates if p.name not in recent]
            pool = not_recent if not_recent else list(candidates)
            random.shuffle(pool)
            for candidate in pool:
                dur = self._validate_clip(candidate)
                if dur is not None:
                    return candidate, dur
            return None, 0.0

        path, dur = try_pool(manual)
        if path is None:
            path, dur = try_pool(downloaded)

        if path is not None:
            self._update_usage_log(path.name)
        return path, dur

    def _validate_clip(self, path: Path) -> Optional[float]:
        """
        Return clip duration (seconds) if valid, None otherwise.
        Deletes the file if it is corrupted. Logs a warning if too short.
        """
        try:
            from moviepy import VideoFileClip
            clip = VideoFileClip(str(path))
            dur = clip.duration
            clip.close()
        except Exception as exc:
            log.warning(
                "brain_rot_fetcher.clip_corrupt",
                file=path.name,
                error=str(exc)[:120],
            )
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            return None

        if dur < _MIN_CLIP_DURATION:
            log.warning(
                "brain_rot_fetcher.clip_too_short",
                file=path.name,
                duration=round(dur, 1),
                minimum=_MIN_CLIP_DURATION,
            )
            return None

        return dur

    # ------------------------------------------------------------------ #
    #  Usage log (anti-repeat)                                            #
    # ------------------------------------------------------------------ #

    def _load_usage_log(self) -> set[str]:
        """Return the set of clip filenames used in the last _ANTI_REPEAT_WINDOW selections."""
        log_path = self._cache_dir / "usage_log.json"
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
            recent = data.get("recent", [])
            return set(recent[-_ANTI_REPEAT_WINDOW:])
        except Exception:
            return set()

    def _update_usage_log(self, filename: str) -> None:
        """Append filename to usage_log.json, keeping the last 20 entries."""
        log_path = self._cache_dir / "usage_log.json"
        try:
            try:
                data = json.loads(log_path.read_text(encoding="utf-8"))
            except Exception:
                data = {"recent": []}
            recent: list[str] = data.get("recent", [])
            recent.append(filename)
            data["recent"] = recent[-20:]
            log_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            log.warning("brain_rot_fetcher.usage_log_write_failed", error=str(exc))

    # ------------------------------------------------------------------ #
    #  Cache management                                                   #
    # ------------------------------------------------------------------ #

    def _prune_cache(self) -> None:
        """Delete oldest auto-downloaded clips when over max_cached_clips."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        auto_clips = sorted(
            [p for p in self._cache_dir.glob("*.mp4") if self._is_auto_downloaded(p)],
            key=lambda p: p.stat().st_mtime,
        )
        while len(auto_clips) > self._max_cached:
            oldest = auto_clips.pop(0)
            try:
                oldest.unlink()
                log.info("brain_rot_fetcher.cache_pruned", file=oldest.name)
            except Exception as exc:
                log.warning(
                    "brain_rot_fetcher.cache_prune_failed",
                    file=oldest.name,
                    error=str(exc),
                )

    # ------------------------------------------------------------------ #
    #  Pexels API                                                         #
    # ------------------------------------------------------------------ #

    def _fetch_from_pexels(self, category: dict) -> Optional[Path]:
        """
        Fetch a video from Pexels, download to cache, and return its Path.
        Returns None on failure.
        """
        if not self._api_key:
            log.error("brain_rot_fetcher.pexels_api_key_missing")
            return None

        headers = {"Authorization": self._api_key}
        query   = category["query"]

        # First attempt: portrait orientation
        video_url = self._search_pexels(query, headers, orientation="portrait")

        # Fallback: no orientation filter, then crop later
        if video_url is None:
            log.info("brain_rot_fetcher.pexels_portrait_fallback", query=query)
            video_url = self._search_pexels(query, headers, orientation=None)

        if video_url is None:
            log.error("brain_rot_fetcher.pexels_no_results", query=query)
            return None

        return self._download_video(video_url, category)

    def _search_pexels(
        self,
        query: str,
        headers: dict,
        orientation: Optional[str],
    ) -> Optional[str]:
        """
        Query Pexels, pick a random video from the top 5, and return the
        best download URL. Returns None if no suitable video found.
        """
        params: dict = {
            "query":    query,
            "size":     "medium",
            "per_page": 10,
        }
        if orientation:
            params["orientation"] = orientation

        try:
            resp = requests.get(
                _PEXELS_API_URL,
                headers=headers,
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            log.error("brain_rot_fetcher.pexels_request_failed", error=str(exc))
            return None

        videos = data.get("videos", [])
        if not videos:
            return None

        # Restrict to top 5 results then pick randomly
        candidates = videos[:5]
        random.shuffle(candidates)

        for video in candidates:
            url = self._best_video_file(video.get("video_files", []))
            if url:
                return url

        return None

    def _best_video_file(self, video_files: list[dict]) -> Optional[str]:
        """
        Select the best video file URL from a Pexels video_files list.

        Preference order:
          1. Portrait (height > width), quality HD, height ≥ _MIN_VIDEO_HEIGHT
          2. Portrait any quality, height ≥ _MIN_VIDEO_HEIGHT
          3. Any file height ≥ _MIN_VIDEO_HEIGHT (will crop to portrait later)
          4. Largest available (last resort)
        """
        # Sort by height descending to prefer better quality
        files = sorted(video_files, key=lambda f: f.get("height", 0), reverse=True)

        portrait_hd = [
            f for f in files
            if f.get("height", 0) > f.get("width", 0)
            and f.get("height", 0) >= _MIN_VIDEO_HEIGHT
            and f.get("quality", "") in ("hd", "HD")
        ]
        if portrait_hd:
            return portrait_hd[0].get("link")

        portrait_any = [
            f for f in files
            if f.get("height", 0) > f.get("width", 0)
            and f.get("height", 0) >= _MIN_VIDEO_HEIGHT
        ]
        if portrait_any:
            return portrait_any[0].get("link")

        tall_enough = [f for f in files if f.get("height", 0) >= _MIN_VIDEO_HEIGHT]
        if tall_enough:
            return tall_enough[0].get("link")

        if files:
            return files[0].get("link")

        return None

    def _download_video(self, url: str, category: dict) -> Optional[Path]:
        """Stream-download a video to the cache directory. Returns Path or None."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        slug      = _slug(category["query"])
        timestamp = int(time.time())
        dest      = self._cache_dir / f"{slug}_{timestamp}.mp4"

        try:
            log.info("brain_rot_fetcher.downloading", url=url[:80], dest=dest.name)
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            f.write(chunk)
            log.info(
                "brain_rot_fetcher.download_done",
                file=dest.name,
                bytes=dest.stat().st_size,
            )
            return dest
        except Exception as exc:
            log.error("brain_rot_fetcher.download_failed", error=str(exc))
            try:
                dest.unlink(missing_ok=True)
            except Exception:
                pass
            return None

    # ------------------------------------------------------------------ #
    #  Clip processing                                                    #
    # ------------------------------------------------------------------ #

    def _process_clip(self, path: Path, duration: float):
        """
        Load raw clip, trim/loop to ``duration``, crop to portrait if needed,
        resize to 1080×768, strip audio. Returns MoviePy VideoFileClip or None.
        """
        try:
            from moviepy import VideoFileClip, concatenate_videoclips
        except ImportError as exc:
            log.error("brain_rot_fetcher.moviepy_import_failed", error=str(exc))
            return None

        try:
            raw = VideoFileClip(str(path))
        except Exception as exc:
            log.error("brain_rot_fetcher.clip_load_failed", file=path.name, error=str(exc))
            return None

        try:
            # Trim or loop to match required duration
            clip = self._fit_duration(raw, duration)

            # Crop to portrait if landscape
            clip = self._ensure_portrait(clip)

            # Resize to exactly 1080×768
            clip = clip.resized((_OUT_W, _OUT_H))

            # Strip audio — brain rot panel must be silent
            clip = clip.without_audio()

            log.info(
                "brain_rot_fetcher.clip_ready",
                size=f"{_OUT_W}x{_OUT_H}",
                duration=round(clip.duration, 2),
            )
            return clip

        except Exception as exc:
            log.error("brain_rot_fetcher.clip_process_failed", error=str(exc))
            try:
                raw.close()
            except Exception:
                pass
            return None

    def _fit_duration(self, clip, duration: float):
        """
        Return a clip that is exactly ``duration`` seconds long.

        - Clip longer than needed → trim.
        - Clip shorter → loop (concatenate with itself) until long enough, then trim.
        """
        from moviepy import concatenate_videoclips

        clip_dur = clip.duration
        if clip_dur <= 0:
            raise ValueError("Source clip has zero or negative duration")

        if clip_dur >= duration:
            return clip.subclipped(0, duration)

        # Loop: concatenate copies until we exceed duration, then trim
        copies_needed = int(duration / clip_dur) + 2
        looped = concatenate_videoclips([clip] * copies_needed)
        return looped.subclipped(0, duration)

    def _ensure_portrait(self, clip):
        """
        If the clip is landscape (width > height), centre-crop it to portrait.
        Otherwise return unchanged.
        """
        w = clip.w
        h = clip.h
        if w <= h:
            return clip  # already portrait or square

        # Calculate crop: keep full height, centre-crop width to h * (9/16) aspect
        # (we'll resize to 1080×768 afterwards, so any portrait crop is fine)
        target_w = int(h * (_OUT_W / _OUT_H))
        x1 = max(0, (w - target_w) // 2)
        x2 = min(w, x1 + target_w)
        return clip.cropped(x1=x1, x2=x2)
