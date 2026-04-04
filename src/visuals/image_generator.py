"""
Scene image generator.

Priority chain:
  1. Pollinations.AI — free, no key, FLUX model  (new primary)
  2. Stability AI    — v2beta REST API            (if key present)
  3. Pexels          — royalty-free stock photos  (final fallback)

All output images are resized/cropped to exactly 1080 × 1920 (9:16)
and colour-graded (slight contrast + warmth boost) for video use.
"""

import io
import os
import random
import urllib.parse
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageEnhance, ImageFilter

from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log
from src.utils.retry import with_retry

# Target resolution for all output images
TARGET_W = 1080
TARGET_H = 1920

# Pollinations.AI  (free, no API key required)
_POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"

# Stability AI
_STABILITY_BASE = "https://api.stability.ai/v2beta/stable-image/generate"
_STABILITY_ENGINE = "core"          # core = best free-tier model

# Pexels
_PEXELS_SEARCH = "https://api.pexels.com/v1/search"


class ImageGenerator:
    """
    Generates or retrieves scene images for each script scene.

    Usage:
        gen = ImageGenerator()
        paths = gen.generate_all(script["scenes"], "video_001")
    """

    def __init__(self):
        cfg = get_config()
        self.cfg = cfg.visuals
        self._images_dir = get_project_root() / "output" / "images"
        self._images_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- #
    #  Pollinations.AI  (free, no key)                                 #
    # ---------------------------------------------------------------- #

    @with_retry(max_attempts=3, backoff_factor=2,
                exceptions=(requests.RequestException, Exception))
    def _generate_pollinations(self, prompt: str) -> bytes:
        """
        Call Pollinations.AI to generate a 1080×1920 portrait image using FLUX.

        No API key required.  Returns raw PNG/JPEG bytes.
        """
        encoded = urllib.parse.quote(prompt, safe="")
        url = f"{_POLLINATIONS_BASE}{encoded}"
        params = {
            "width":   TARGET_W,
            "height":  TARGET_H,
            "model":   "flux",
            "seed":    random.randint(1, 999999),
            "nologo":  "true",
            "enhance": "true",
        }
        resp = requests.get(url, params=params, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 1024:
            log.info("image_generator.pollinations.success", prompt=prompt[:60])
            return resp.content
        raise RuntimeError(
            f"Pollinations returned {resp.status_code}, size={len(resp.content)}"
        )

    # ---------------------------------------------------------------- #
    #  Stability AI                                                     #
    # ---------------------------------------------------------------- #

    @with_retry(max_attempts=3, backoff_factor=2,
                exceptions=(requests.RequestException, Exception))
    def _generate_stability(self, prompt: str) -> bytes:
        """
        Call Stability AI v2beta to generate a 9:16 portrait image.

        Args:
            prompt: Detailed visual description for the scene.

        Returns:
            Raw PNG bytes of the generated image.
        """
        api_key = os.environ.get("STABILITY_API_KEY", "")
        if not api_key:
            raise ValueError("STABILITY_API_KEY not set")

        url = f"{_STABILITY_BASE}/{_STABILITY_ENGINE}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*",
        }
        data = {
            "prompt": prompt,
            "aspect_ratio": "9:16",
            "output_format": "png",
        }

        resp = requests.post(url, headers=headers, files={"none": ""}, data=data, timeout=60)

        if resp.status_code == 200:
            log.info("image_generator.stability.success", prompt=prompt[:60])
            return resp.content
        else:
            raise RuntimeError(
                f"Stability AI returned {resp.status_code}: {resp.text[:200]}"
            )

    # ---------------------------------------------------------------- #
    #  Pexels fallback                                                  #
    # ---------------------------------------------------------------- #

    @with_retry(max_attempts=3, backoff_factor=2,
                exceptions=(requests.RequestException, Exception))
    def _fetch_pexels(self, query: str) -> bytes:
        """
        Search Pexels for a portrait photo matching the query.

        Args:
            query: Search keywords extracted from the visual prompt.

        Returns:
            Raw JPEG bytes of a portrait stock photo.
        """
        api_key = os.environ.get("PEXELS_API_KEY", "")
        if not api_key:
            raise ValueError("PEXELS_API_KEY not set")

        # Condense the prompt to key nouns for better search results
        keywords = " ".join(query.split()[:6])

        params = {
            "query": keywords,
            "per_page": 5,
            "orientation": "portrait",
        }
        headers = {"Authorization": api_key}

        resp = requests.get(_PEXELS_SEARCH, headers=headers, params=params, timeout=15)
        resp.raise_for_status()

        photos = resp.json().get("photos", [])
        if not photos:
            # Retry with a simpler query (first 2 words)
            simple = " ".join(query.split()[:2])
            params["query"] = simple
            resp = requests.get(_PEXELS_SEARCH, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            photos = resp.json().get("photos", [])

        if not photos:
            raise RuntimeError(f"Pexels returned no photos for: {query[:60]}")

        # Pick randomly from the top results for variety
        photo = random.choice(photos[:min(len(photos), 3)])
        img_url = photo["src"].get("large2x") or photo["src"]["original"]

        img_resp = requests.get(img_url, timeout=30)
        img_resp.raise_for_status()

        log.info("image_generator.pexels.success", query=keywords, url=img_url[:60])
        return img_resp.content

    # ---------------------------------------------------------------- #
    #  Image processing                                                 #
    # ---------------------------------------------------------------- #

    def _resize_crop_center(self, image_bytes: bytes) -> Image.Image:
        """
        Resize and centre-crop image to exactly TARGET_W × TARGET_H (1080×1920).
        Preserves aspect ratio by cropping the longer dimension.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        src_w, src_h = img.size

        # Scale so the shorter side fits the target
        scale = max(TARGET_W / src_w, TARGET_H / src_h)
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

        # Centre crop
        left = (new_w - TARGET_W) // 2
        top  = (new_h - TARGET_H) // 2
        img  = img.crop((left, top, left + TARGET_W, top + TARGET_H))

        return img

    def _apply_color_grade(self, img: Image.Image) -> Image.Image:
        """
        Apply subtle colour grading for a cinematic YouTube look:
        - Slight contrast boost (+10 %)
        - Slight saturation boost (+8 %)
        - Subtle warmth (shift R channel up, B channel down slightly)
        """
        # Contrast
        img = ImageEnhance.Contrast(img).enhance(1.10)
        # Saturation
        img = ImageEnhance.Color(img).enhance(1.08)
        # Warmth: split channels, nudge R up / B down
        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * 1.04)))
        b = b.point(lambda x: int(x * 0.96))
        img = Image.merge("RGB", (r, g, b))
        return img

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def generate_scene_image(
        self,
        visual_prompt: str,
        scene_number: int,
        video_id: str,
        force_pexels: bool = False,
    ) -> Path:
        """
        Generate or fetch one scene image, apply grading, save to disk.

        Args:
            visual_prompt: Detailed visual description from the script.
            scene_number: Scene index (1-based) for file naming.
            video_id: Unique video identifier for file naming.
            force_pexels: Skip Stability AI and go straight to Pexels.

        Returns:
            Path to the saved 1080×1920 PNG file.
        """
        out_path = self._images_dir / f"{video_id}_scene_{scene_number:02d}.png"

        provider = self.cfg.get("provider", "stability")
        stability_key = os.environ.get("STABILITY_API_KEY", "")
        has_stability = bool(stability_key) and not stability_key.startswith("sk-xx")

        raw_bytes: Optional[bytes] = None

        # 1. Pollinations.AI (free, no key needed)
        if not force_pexels and provider == "pollinations":
            try:
                raw_bytes = self._generate_pollinations(visual_prompt)
            except Exception as exc:
                log.warning(
                    "image_generator.pollinations_failed_fallback",
                    scene=scene_number,
                    error=str(exc),
                )

        # 2. Stability AI
        if raw_bytes is None and not force_pexels and has_stability and provider not in ("pexels", "pollinations"):
            try:
                raw_bytes = self._generate_stability(visual_prompt)
            except Exception as exc:
                log.warning(
                    "image_generator.stability_failed_fallback",
                    scene=scene_number,
                    error=str(exc),
                )

        # 3. Pexels fallback
        if raw_bytes is None:
            try:
                raw_bytes = self._fetch_pexels(visual_prompt)
            except Exception as exc:
                log.error(
                    "image_generator.pexels_failed",
                    scene=scene_number,
                    error=str(exc),
                )
                raise RuntimeError(
                    f"All image providers failed for scene {scene_number}: {exc}"
                ) from exc

        # Process and save
        img = self._resize_crop_center(raw_bytes)
        img = self._apply_color_grade(img)
        img.save(str(out_path), "PNG", optimize=False)

        log.info(
            "image_generator.scene_saved",
            scene=scene_number,
            path=str(out_path),
            size_kb=round(out_path.stat().st_size / 1024, 1),
        )
        return out_path

    def generate_all(
        self,
        scenes: list[dict],
        video_id: str,
    ) -> list[Path]:
        """
        Generate images for all scenes in the script.

        Args:
            scenes: List of scene dicts from the script (must have 'visual_prompt'
                    and 'scene_number').
            video_id: Unique video identifier.

        Returns:
            List of Paths (one per scene), in scene order.
        """
        paths: list[Path] = []
        for scene in scenes:
            scene_num = scene.get("scene_number", len(paths) + 1)
            prompt = scene.get("visual_prompt", "")
            log.info(
                "image_generator.generate_all.scene",
                scene=scene_num,
                prompt=prompt[:60],
            )
            path = self.generate_scene_image(prompt, scene_num, video_id)
            paths.append(path)

        log.info(
            "image_generator.generate_all.done",
            video_id=video_id,
            scenes=len(paths),
        )
        return paths
