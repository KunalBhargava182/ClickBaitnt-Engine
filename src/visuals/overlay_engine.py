"""
Overlay engine — composites UI layers onto scene video clips.

Layers (applied in order):
  1. Gradient overlay  : Semi-transparent dark gradient at the bottom 40 % of frame.
                         Makes white subtitle text legible over any background.
  2. Progress bar      : Thin coloured bar at the very top of the frame
                         that fills left→right over the clip duration.
  3. Vignette          : Darkened edges (subtle, cinematic look).

All layers are optional and configurable.
Input / output resolution: 1080 × 1920 (9:16).
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy import VideoClip

from src.utils.logger import log

OUT_W = 1080
OUT_H = 1920
FPS   = 30


class OverlayEngine:
    """
    Composites decorative / functional overlays onto a MoviePy VideoClip.

    Usage:
        engine = OverlayEngine()
        final_clip = engine.apply(
            base_clip,
            add_gradient=True,
            add_progress_bar=True,
            add_vignette=True,
            bar_color=(255, 200, 0),
        )
    """

    def apply(
        self,
        base_clip: VideoClip,
        add_gradient: bool = True,
        add_progress_bar: bool = True,
        add_vignette: bool = True,
        bar_color: tuple[int, int, int] = (255, 200, 0),
        bar_height: int = 6,
        gradient_height_frac: float = 0.40,
        vignette_strength: float = 0.45,
    ) -> VideoClip:
        """
        Apply overlay layers and return a new VideoClip.

        Args:
            base_clip: Source clip (must be 1080×1920).
            add_gradient: Whether to add the bottom gradient overlay.
            add_progress_bar: Whether to add the top progress bar.
            add_vignette: Whether to add edge vignette.
            bar_color: RGB tuple for the progress bar colour.
            bar_height: Height of the progress bar in pixels.
            gradient_height_frac: Fraction of frame height covered by gradient.
            vignette_strength: 0.0 (no vignette) – 1.0 (fully black edges).

        Returns:
            New VideoClip with overlays composited.
        """
        duration = base_clip.duration

        log.info(
            "overlay_engine.apply",
            gradient=add_gradient,
            progress_bar=add_progress_bar,
            vignette=add_vignette,
            duration=duration,
        )

        # Pre-build static layers (computed once, reused per frame)
        gradient_layer: np.ndarray | None = None
        vignette_layer: np.ndarray | None = None

        if add_gradient:
            gradient_layer = _make_gradient_layer(OUT_W, OUT_H, gradient_height_frac)

        if add_vignette:
            vignette_layer = _make_vignette_layer(OUT_W, OUT_H, vignette_strength)

        def make_frame(t: float) -> np.ndarray:
            # Get base frame
            frame = base_clip.get_frame(t)  # (H, W, 3) uint8
            out = frame.astype(np.float32)

            # 1. Vignette (darkens edges multiplicatively)
            if vignette_layer is not None:
                out = out * vignette_layer

            # 2. Gradient (alpha-blend over bottom portion)
            if gradient_layer is not None:
                grad_rgb   = gradient_layer[:, :, :3].astype(np.float32)
                grad_alpha = gradient_layer[:, :, 3:4].astype(np.float32) / 255.0
                out = out * (1 - grad_alpha) + grad_rgb * grad_alpha

            # 3. Progress bar (draws a coloured rectangle at the top)
            if add_progress_bar:
                progress = min(t / max(duration, 1e-6), 1.0)
                bar_w = int(OUT_W * progress)
                if bar_w > 0:
                    r, g, b = bar_color
                    out[:bar_height, :bar_w, 0] = r
                    out[:bar_height, :bar_w, 1] = g
                    out[:bar_height, :bar_w, 2] = b

            return np.clip(out, 0, 255).astype(np.uint8)

        return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ------------------------------------------------------------------ #
#  Static layer builders                                             #
# ------------------------------------------------------------------ #

def _make_gradient_layer(
    width: int,
    height: int,
    height_frac: float,
) -> np.ndarray:
    """
    Build an RGBA array (H, W, 4) for a bottom-anchored dark gradient.

    The gradient goes from fully transparent at height_frac from bottom
    to 75 % opacity at the very bottom.
    """
    layer = np.zeros((height, width, 4), dtype=np.uint8)

    grad_h = int(height * height_frac)
    start_y = height - grad_h  # y coordinate where gradient starts

    for row_idx in range(grad_h):
        # 0 = top of gradient region, 1 = bottom of frame
        frac = row_idx / max(grad_h - 1, 1)
        # Ease-in: slow start, ramps up faster toward bottom
        alpha = int(frac ** 1.5 * 190)  # max 190 / 255 ≈ 75 %
        y = start_y + row_idx
        layer[y, :, 3] = alpha  # R=0, G=0, B=0, A=alpha

    return layer


def _make_vignette_layer(
    width: int,
    height: int,
    strength: float,
) -> np.ndarray:
    """
    Build a float multiplier array (H, W, 1) for edge darkening.

    Centre = 1.0 (no change), corners approach (1 - strength).
    """
    cx, cy = width / 2, height / 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)

    ys = np.arange(height)
    xs = np.arange(width)
    xx, yy = np.meshgrid(xs, ys)

    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    norm = dist / max_dist  # 0 at centre, 1 at corners

    # Smooth cosine falloff
    factor = 1.0 - strength * (1.0 - np.cos(np.pi * norm / 2))
    factor = np.clip(factor, 0.0, 1.0)

    return factor[:, :, np.newaxis].astype(np.float32)  # (H, W, 1)
