"""
BrainRotFetcher — supplies the bottom-panel clip for split-screen mode.

Workflow:
  1. Weighted-random category selection from config.splitscreen.brain_rot_categories.
  2. Check local cache (assets/brain_rot_clips/). If 3+ clips for the chosen
     category are cached, pick one at random — no API call.
  3. Otherwise fetch from the Pexels Video API, download the best file, and
     cache it locally.
  4. Trim or loop the raw clip to exactly ``duration`` seconds.
  5. Resize to 1080 × 768 (portrait crop if needed).
  6. Strip audio from the returned clip.
  7. On ANY failure: log the error and return None.
     The caller (VideoComposer) treats None as a signal to fall back to
     the standard fullscreen pipeline.

Environment:
  PEXELS_API_KEY  — loaded from .env via config_loader
"""

from __future__ import annotations

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

# How many cached clips per category must exist before we skip the API call
_CACHE_HIT_THRESHOLD = 3


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
        if not self._categories:
            log.error("brain_rot_fetcher.no_categories_configured")
            return None

        # 1. Choose category (weighted random)
        category = self._pick_category()
        log.info("brain_rot_fetcher.category_selected", query=category["query"])

        # 2. Try cache first
        raw_path = self._from_cache(category)
        if raw_path is None:
            # 3. Fetch from Pexels
            raw_path = self._fetch_from_pexels(category)
            if raw_path is None:
                return None
            # 4. Prune cache if over limit
            self._prune_cache()

        # 5. Process (trim/loop + resize + mute)
        return self._process_clip(raw_path, duration)

    def _pick_category(self) -> dict:
        """Weighted-random selection from brain_rot_categories."""
        weights = [float(c.get("weight", 1)) for c in self._categories]
        return random.choices(self._categories, weights=weights, k=1)[0]

    # ------------------------------------------------------------------ #
    #  Cache                                                              #
    # ------------------------------------------------------------------ #

    def _cache_files_for(self, category: dict) -> list[Path]:
        """Return cached .mp4 files matching the given category slug."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        slug = _slug(category["query"])
        return sorted(
            self._cache_dir.glob(f"{slug}_*.mp4"),
            key=lambda p: p.stat().st_mtime,
        )

    def _from_cache(self, category: dict) -> Optional[Path]:
        """
        Return a random cached clip for the category if ≥ _CACHE_HIT_THRESHOLD
        exist, otherwise None (triggers API call).
        """
        files = self._cache_files_for(category)
        if len(files) >= _CACHE_HIT_THRESHOLD:
            chosen = random.choice(files)
            log.info(
                "brain_rot_fetcher.cache_hit",
                file=chosen.name,
                total=len(files),
            )
            return chosen
        log.info(
            "brain_rot_fetcher.cache_miss",
            query=category["query"],
            cached=len(files),
        )
        return None

    def _prune_cache(self) -> None:
        """Delete oldest clips when total cached files exceed max_cached_clips."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        all_clips = sorted(
            self._cache_dir.glob("*.mp4"),
            key=lambda p: p.stat().st_mtime,
        )
        while len(all_clips) > self._max_cached:
            oldest = all_clips.pop(0)
            try:
                oldest.unlink()
                log.info("brain_rot_fetcher.cache_pruned", file=oldest.name)
            except Exception as exc:
                log.warning("brain_rot_fetcher.cache_prune_failed", file=oldest.name, error=str(exc))

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
            log.info("brain_rot_fetcher.download_done", file=dest.name, bytes=dest.stat().st_size)
            return dest
        except Exception as exc:
            log.error("brain_rot_fetcher.download_failed", error=str(exc))
            # Remove partial file if it exists
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
