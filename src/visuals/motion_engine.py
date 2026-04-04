"""
Motion engine — adds animated motion to static scene images.

Supported effects (chosen randomly per scene, seeded for reproducibility):
  - ken_burns   : Slow zoom 1.0x → 1.15x over scene duration
  - pan_lr      : Slow left-to-right drift
  - pan_tb      : Slow top-to-bottom drift
  - zoom_pulse  : Subtle breathe / pulse effect

All output clips are 1080 × 1920 (9:16), 30 fps.
Returns a MoviePy VideoClip — does NOT write to disk.
"""

import math
import random
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image
from moviepy import VideoClip

from src.utils.logger import log

# Output resolution — must match image_generator.py constants
OUT_W = 1080
OUT_H = 1920
FPS   = 30

# Available motion styles and their selection weights
_STYLES = ["ken_burns", "pan_lr", "pan_tb", "zoom_pulse"]
_WEIGHTS = [0.40, 0.25, 0.25, 0.10]


class MotionEngine:
    """
    Animates a static 1080×1920 image into a video clip with subtle motion.

    Usage:
        engine = MotionEngine()
        clip = engine.animate(image_path, duration=5.0, scene_number=1, seed=42)
        # clip is a moviepy VideoClip ready for compositing
    """

    def animate(
        self,
        image_path: Path,
        duration: float,
        scene_number: int = 1,
        seed: int | None = None,
        style: str | None = None,
    ) -> VideoClip:
        """
        Animate a static image and return a VideoClip.

        Args:
            image_path: Path to a 1080×1920 PNG image.
            duration: Clip length in seconds.
            scene_number: Used to derive per-scene seed if seed is None.
            seed: Explicit RNG seed for reproducibility.
            style: Force a specific motion style (skips random selection).

        Returns:
            MoviePy VideoClip (no audio, 30 fps).
        """
        if seed is None:
            seed = scene_number * 137 + 42  # deterministic per scene

        rng = random.Random(seed)

        chosen = style or rng.choices(_STYLES, weights=_WEIGHTS, k=1)[0]

        log.info(
            "motion_engine.animate",
            scene=scene_number,
            style=chosen,
            duration=duration,
        )

        # Load image as a numpy array (H, W, 3) uint8
        img_array = np.array(Image.open(image_path).convert("RGB"))

        make_frame = self._get_make_frame(chosen, img_array, duration, rng)

        clip = VideoClip(make_frame, duration=duration).with_fps(FPS)
        return clip

    # ------------------------------------------------------------------ #
    #  Effect builders                                                     #
    # ------------------------------------------------------------------ #

    def _get_make_frame(
        self,
        style: str,
        img: np.ndarray,
        duration: float,
        rng: random.Random,
    ) -> Callable[[float], np.ndarray]:
        """Return the make_frame callable for the chosen style."""
        if style == "ken_burns":
            return self._ken_burns(img, duration, rng)
        elif style == "pan_lr":
            return self._pan_lr(img, duration, rng)
        elif style == "pan_tb":
            return self._pan_tb(img, duration, rng)
        elif style == "zoom_pulse":
            return self._zoom_pulse(img, duration)
        else:
            log.warning("motion_engine.unknown_style", style=style)
            return self._ken_burns(img, duration, rng)

    # -- Ken Burns --------------------------------------------------------

    def _ken_burns(
        self,
        img: np.ndarray,
        duration: float,
        rng: random.Random,
    ) -> Callable[[float], np.ndarray]:
        """
        Slow zoom-in: scale goes from start_scale → end_scale linearly.
        The anchor point is randomised slightly around the centre.
        """
        start_scale = 1.0
        end_scale   = 1.15

        # Anchor: where the zoom is centred (fraction of image size)
        ax = rng.uniform(0.35, 0.65)
        ay = rng.uniform(0.35, 0.65)

        h, w = img.shape[:2]

        def make_frame(t: float) -> np.ndarray:
            progress = t / max(duration, 1e-6)
            scale = start_scale + (end_scale - start_scale) * progress
            return _zoom_crop(img, scale, ax, ay, OUT_W, OUT_H)

        return make_frame

    # -- Pan left-to-right ------------------------------------------------

    def _pan_lr(
        self,
        img: np.ndarray,
        duration: float,
        rng: random.Random,
    ) -> Callable[[float], np.ndarray]:
        """
        Horizontal pan: crops a 1080-wide window that drifts left→right (or reverse).
        The image must be wider than 1080px; we use a slightly wider source window.
        """
        direction = rng.choice([-1, 1])  # -1 = right→left, +1 = left→right
        max_pan_px = 80  # pixels to drift over full duration

        def make_frame(t: float) -> np.ndarray:
            progress = t / max(duration, 1e-6)
            offset_x = int(direction * max_pan_px * progress)
            return _pan_crop(img, offset_x=offset_x, offset_y=0, out_w=OUT_W, out_h=OUT_H)

        return make_frame

    # -- Pan top-to-bottom ------------------------------------------------

    def _pan_tb(
        self,
        img: np.ndarray,
        duration: float,
        rng: random.Random,
    ) -> Callable[[float], np.ndarray]:
        """Vertical pan: crops a 1920-tall window that drifts top→bottom."""
        direction = rng.choice([-1, 1])
        max_pan_px = 60

        def make_frame(t: float) -> np.ndarray:
            progress = t / max(duration, 1e-6)
            offset_y = int(direction * max_pan_px * progress)
            return _pan_crop(img, offset_x=0, offset_y=offset_y, out_w=OUT_W, out_h=OUT_H)

        return make_frame

    # -- Zoom pulse -------------------------------------------------------

    def _zoom_pulse(
        self,
        img: np.ndarray,
        duration: float,
    ) -> Callable[[float], np.ndarray]:
        """
        Subtle breathe effect: scale oscillates between 1.0 and 1.04
        with a sine wave (one full cycle = duration).
        """
        base_scale = 1.02
        amplitude  = 0.02
        freq       = 1.0 / max(duration, 1e-6)  # one cycle over clip

        def make_frame(t: float) -> np.ndarray:
            scale = base_scale + amplitude * math.sin(2 * math.pi * freq * t)
            return _zoom_crop(img, scale, 0.5, 0.5, OUT_W, OUT_H)

        return make_frame


# ------------------------------------------------------------------ #
#  Low-level crop helpers (module-level, pure functions)             #
# ------------------------------------------------------------------ #

def _zoom_crop(
    img: np.ndarray,
    scale: float,
    anchor_x: float,
    anchor_y: float,
    out_w: int,
    out_h: int,
) -> np.ndarray:
    """
    Crop a out_w×out_h window from img after virtual zoom by scale.
    anchor_x/y are the zoom-centre fractions (0–1).
    """
    h, w = img.shape[:2]

    # Size of the crop window in source pixels
    crop_w = int(out_w / scale)
    crop_h = int(out_h / scale)

    # Clamp so we never ask for more than the image provides
    crop_w = min(crop_w, w)
    crop_h = min(crop_h, h)

    # Top-left corner anchored around the specified point
    cx = int(anchor_x * w)
    cy = int(anchor_y * h)

    x0 = cx - crop_w // 2
    y0 = cy - crop_h // 2

    # Clamp to image boundaries
    x0 = max(0, min(x0, w - crop_w))
    y0 = max(0, min(y0, h - crop_h))

    crop = img[y0 : y0 + crop_h, x0 : x0 + crop_w]

    # Resize back to output resolution
    from PIL import Image as _PILImage
    pil = _PILImage.fromarray(crop)
    pil = pil.resize((out_w, out_h), _PILImage.LANCZOS)
    return np.array(pil)


def _pan_crop(
    img: np.ndarray,
    offset_x: int,
    offset_y: int,
    out_w: int,
    out_h: int,
) -> np.ndarray:
    """
    Crop a out_w×out_h window offset from the centre.
    If the offset would go out of bounds, it is clamped.
    The source image is slightly over-cropped to allow room for pan.
    """
    h, w = img.shape[:2]

    # Centre crop start
    base_x = (w - out_w) // 2
    base_y = (h - out_h) // 2

    x0 = base_x + offset_x
    y0 = base_y + offset_y

    # Clamp
    x0 = max(0, min(x0, w - out_w))
    y0 = max(0, min(y0, h - out_h))

    if x0 + out_w > w or y0 + out_h > h:
        # Fallback: centre crop (shouldn't happen after clamping)
        x0 = base_x
        y0 = base_y

    return img[y0 : y0 + out_h, x0 : x0 + out_w]
