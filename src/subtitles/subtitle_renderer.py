"""
Subtitle renderer — burns animated word-highlight captions onto a VideoClip.

Style: word_highlight
  - Displays up to max_words_per_line words at a time.
  - The currently spoken word is highlighted (yellow by default).
  - All other visible words are shown in the inactive colour (white).

Animation: scale_pop
  - When a new word becomes active it briefly scales up (+20 %) and
    eases back to 1.0 over 0.15 s (cosine ease-out).

Rendering pipeline:
  1. Group WordSegments into fixed-size chunks (≤ max_words_per_line).
  2. For each frame at time t, find the active chunk + active word index.
  3. Render the chunk onto a transparent RGBA PIL image using Pillow.
  4. Composite the caption image over the base VideoClip frame.

Font resolution priority:
  1. assets/fonts/<configured_font>.ttf  (e.g. Montserrat-Bold.ttf)
  2. assets/fonts/*.ttf                  (first .ttf found)
  3. C:/Windows/Fonts/Impact.ttf         (great for captions)
  4. C:/Windows/Fonts/arialbd.ttf        (fallback bold)
  5. PIL built-in bitmap font            (last resort)
"""

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

from src.subtitles.whisper_align import WordSegment
from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log

# Output dimensions (must match rest of pipeline)
OUT_W = 1080
OUT_H = 1920
FPS   = 30

# Scale-pop animation duration in seconds
_POP_DURATION = 0.15
# Scale-pop peak multiplier (1.0 = no pop)
_POP_SCALE    = 1.20


@dataclass
class _SubtitleChunk:
    """A window of consecutive words shown together on screen."""
    words:  list[WordSegment]
    start:  float   # display start (= first word start)
    end:    float   # display end   (= last word end)


class SubtitleRenderer:
    """
    Composites animated word-highlight subtitles onto a base VideoClip.

    Usage:
        renderer = SubtitleRenderer()
        captioned = renderer.render(base_clip, word_segments)
    """

    def __init__(self) -> None:
        cfg = get_config()
        sub = cfg.subtitles

        self._max_words: int        = sub.get("max_words_per_line", 4)
        self._font_name: str        = sub.get("font", "Montserrat-Bold")
        self._font_size: int        = int(sub.get("font_size", 60))
        self._animation: str        = sub.get("animation", "scale_pop")
        self._position: str         = sub.get("position", "center")

        colors                      = sub.get("colors", {})
        self._active_color: str     = colors.get("active_word", "#FFFF00")
        self._inactive_color: str   = colors.get("inactive_word", "#FFFFFF")
        self._stroke_color: str     = colors.get("stroke_color", "#000000")
        self._stroke_width: int     = int(colors.get("stroke_width", 3))

        # Convert hex → RGB tuples once
        self._active_rgb   = _hex_to_rgb(self._active_color)
        self._inactive_rgb = _hex_to_rgb(self._inactive_color)
        self._stroke_rgb   = _hex_to_rgb(self._stroke_color)

        # Pre-load font; also build a pop-scaled variant
        self._font      = _load_font(self._font_name, self._font_size)
        self._font_pop  = _load_font(
            self._font_name, int(self._font_size * _POP_SCALE)
        )

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def render(
        self,
        base_clip: VideoClip,
        word_segments: list[WordSegment],
        mode: str = "fullscreen",
    ) -> VideoClip:
        """
        Composite animated subtitles onto base_clip.

        Args:
            base_clip: Source clip (must be 1080 × 1920).
            word_segments: Word-level timing from WhisperAligner.
            mode: "fullscreen" (default) or "splitscreen". In splitscreen
                  mode, subtitles are rendered at y=1100 (near the split
                  boundary) instead of the default 72%-down position.

        Returns:
            New VideoClip with captions burned in, same duration/fps.
        """
        if not word_segments:
            log.warning("subtitle_renderer.no_segments — returning base clip unchanged")
            return base_clip

        chunks = self._build_chunks(word_segments)
        duration = base_clip.duration

        # y_override=None means use the default 72%-down position.
        y_override: Optional[int] = None
        if mode == "splitscreen":
            y_override = get_config().get("splitscreen", {}).get("subtitle_y_position", 1100)

        log.info(
            "subtitle_renderer.render",
            words=len(word_segments),
            chunks=len(chunks),
            duration=duration,
            mode=mode,
        )

        def make_frame(t: float) -> np.ndarray:
            base_frame = base_clip.get_frame(t)
            caption_img = self._render_caption(t, chunks, y_override=y_override)
            if caption_img is None:
                return base_frame
            return _composite(base_frame, caption_img)

        return VideoClip(make_frame, duration=duration).with_fps(FPS)

    # ------------------------------------------------------------------ #
    #  Chunk builder                                                       #
    # ------------------------------------------------------------------ #

    def _build_chunks(self, segments: list[WordSegment]) -> list[_SubtitleChunk]:
        """Split the flat word list into fixed-size display windows."""
        chunks: list[_SubtitleChunk] = []
        n = self._max_words

        for i in range(0, len(segments), n):
            group = segments[i : i + n]
            chunks.append(
                _SubtitleChunk(
                    words=group,
                    start=group[0].start,
                    end=group[-1].end,
                )
            )

        return chunks

    # ------------------------------------------------------------------ #
    #  Caption rendering                                                   #
    # ------------------------------------------------------------------ #

    def _render_caption(
        self,
        t: float,
        chunks: list[_SubtitleChunk],
        y_override: Optional[int] = None,
    ) -> Optional[np.ndarray]:
        """
        Return an RGBA numpy array (OUT_H, OUT_W, 4) with the caption
        for time t, or None if no chunk is active.

        Args:
            y_override: If provided, use this as the vertical centre pixel
                        instead of the default 72%-down position.
        """
        chunk, active_idx = self._find_active(t, chunks)
        if chunk is None:
            return None

        # Create transparent canvas
        canvas = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        words  = chunk.words
        n      = len(words)

        # --- Measure each word at its effective font size ---
        sizes: list[tuple[int, int]] = []   # (w, h) per word
        fonts: list[ImageFont.FreeTypeFont] = []

        for idx, ws in enumerate(words):
            pop_scale = self._pop_scale_at(t, ws) if idx == active_idx else 1.0
            font = self._scaled_font(pop_scale)
            bbox = font.getbbox(ws.word)          # (left, top, right, bottom)
            word_w = bbox[2] - bbox[0]
            word_h = bbox[3] - bbox[1]
            sizes.append((word_w, word_h))
            fonts.append(font)

        # --- Layout: single line, centred ---
        gap       = 18   # pixels between words
        total_w   = sum(w for w, _ in sizes) + gap * (n - 1)
        max_h     = max(h for _, h in sizes)

        # Vertical position: use override (e.g. splitscreen boundary) or default 72%
        y_centre  = y_override if y_override is not None else int(OUT_H * 0.72)
        x_start   = (OUT_W - total_w) // 2

        # Wrap to two lines if it doesn't fit
        if total_w > OUT_W - 80:
            return self._render_two_lines(draw, canvas, words, active_idx, t, y_override=y_override)

        # --- Draw each word ---
        x = x_start
        for idx, (ws, (ww, wh), font) in enumerate(zip(words, sizes, fonts)):
            colour = self._active_rgb if idx == active_idx else self._inactive_rgb
            y = y_centre - wh // 2

            # Stroke (outline) drawn by offsetting in 8 directions
            for dx, dy in _stroke_offsets(self._stroke_width):
                draw.text(
                    (x + dx, y + dy),
                    ws.word,
                    font=font,
                    fill=(*self._stroke_rgb, 255),
                )

            # Main text
            draw.text((x, y), ws.word, font=font, fill=(*colour, 255))
            x += ww + gap

        return np.array(canvas)

    def _render_two_lines(
        self,
        draw: ImageDraw.ImageDraw,
        canvas: Image.Image,
        words: list[WordSegment],
        active_idx: int,
        t: float,
        y_override: Optional[int] = None,
    ) -> np.ndarray:
        """Fallback: split chunk across two lines."""
        mid       = len(words) // 2
        line1     = words[:mid]
        line2     = words[mid:]
        gap       = 18
        line_gap  = 20   # vertical gap between lines

        y_centre  = y_override if y_override is not None else int(OUT_H * 0.72)

        for line_words, line_offset in [(line1, -1), (line2, 1)]:
            sizes  = []
            fonts  = []
            for idx_in_chunk, ws in enumerate(line_words):
                g_idx  = (0 if line_offset == -1 else mid) + idx_in_chunk
                pop_sc = self._pop_scale_at(t, ws) if g_idx == active_idx else 1.0
                font   = self._scaled_font(pop_sc)
                bbox   = font.getbbox(ws.word)
                sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
                fonts.append(font)

            total_w = sum(w for w, _ in sizes) + gap * (len(line_words) - 1)
            max_h   = max(h for _, h in sizes)
            x       = (OUT_W - total_w) // 2
            y_base  = y_centre + line_offset * (max_h // 2 + line_gap // 2)

            for idx_in_chunk, (ws, (ww, wh), font) in enumerate(
                zip(line_words, sizes, fonts)
            ):
                g_idx  = (0 if line_offset == -1 else mid) + idx_in_chunk
                colour = self._active_rgb if g_idx == active_idx else self._inactive_rgb
                y      = y_base - wh // 2

                for dx, dy in _stroke_offsets(self._stroke_width):
                    draw.text(
                        (x + dx, y + dy),
                        ws.word,
                        font=font,
                        fill=(*self._stroke_rgb, 255),
                    )
                draw.text((x, y), ws.word, font=font, fill=(*colour, 255))
                x += ww + gap

        return np.array(canvas)

    # ------------------------------------------------------------------ #
    #  Timing helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_active(
        t: float,
        chunks: list[_SubtitleChunk],
    ) -> tuple[Optional[_SubtitleChunk], int]:
        """
        Return (active_chunk, active_word_index) at time t.
        active_word_index = -1 if no word is being spoken (gap).
        Returns (None, -1) if no chunk is active.
        """
        for chunk in chunks:
            if chunk.start <= t <= chunk.end:
                # Find the specific active word
                for i, ws in enumerate(chunk.words):
                    if ws.start <= t <= ws.end:
                        return chunk, i
                # Between words in this chunk — show last spoken word dimmed
                # Find last word whose start <= t
                last_idx = -1
                for i, ws in enumerate(chunk.words):
                    if ws.start <= t:
                        last_idx = i
                return chunk, last_idx
        return None, -1

    def _pop_scale_at(self, t: float, ws: WordSegment) -> float:
        """
        Return the pop scale factor for a word at time t.
        1.0 = no pop, _POP_SCALE = peak (at word start).
        Eases out over _POP_DURATION seconds.
        """
        if self._animation != "scale_pop":
            return 1.0
        dt = t - ws.start
        if dt < 0 or dt > _POP_DURATION:
            return 1.0
        # Cosine ease-out: 1 at dt=0, 0 at dt=_POP_DURATION
        ease = math.cos(math.pi / 2 * dt / _POP_DURATION)
        return 1.0 + (_POP_SCALE - 1.0) * ease

    def _scaled_font(self, scale: float) -> ImageFont.FreeTypeFont:
        """Return a font at the effective size after applying scale."""
        if abs(scale - 1.0) < 0.01:
            return self._font
        if abs(scale - _POP_SCALE) < 0.01:
            return self._font_pop
        # Arbitrary intermediate scale — create on the fly
        return _load_font(self._font_name, int(self._font_size * scale))


# ------------------------------------------------------------------ #
#  Module-level helpers                                               #
# ------------------------------------------------------------------ #

def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' to (R, G, B) tuple."""
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _stroke_offsets(width: int) -> list[tuple[int, int]]:
    """Return 8-directional pixel offsets for drawing text stroke."""
    w = max(1, width)
    return [
        (-w, -w), (0, -w), (w, -w),
        (-w,  0),           (w,  0),
        (-w,  w), (0,  w), (w,  w),
    ]


def _load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Resolve and load a TrueType font by name and size.

    Search order:
      1. assets/fonts/<font_name>.ttf
      2. assets/fonts/*.ttf (first found)
      3. C:/Windows/Fonts/Impact.ttf
      4. C:/Windows/Fonts/arialbd.ttf
      5. PIL built-in bitmap (last resort, ignores size)
    """
    root = get_project_root()

    candidates: list[Path] = []

    # 1. Exact match in assets/fonts/
    candidates.append(root / "assets" / "fonts" / f"{font_name}.ttf")

    # 2. Any TTF in assets/fonts/
    fonts_dir = root / "assets" / "fonts"
    if fonts_dir.exists():
        candidates.extend(sorted(fonts_dir.glob("*.ttf")))

    # 3 & 4. Common Windows bold fonts
    win_fonts = Path("C:/Windows/Fonts")
    for name in ("Impact.ttf", "arialbd.ttf", "verdanab.ttf", "arial.ttf"):
        candidates.append(win_fonts / name)

    for path in candidates:
        if path.exists():
            try:
                font = ImageFont.truetype(str(path), size)
                return font
            except Exception:
                continue

    log.warning("subtitle_renderer.font_not_found", name=font_name, size=size)
    # PIL built-in — size parameter supported in Pillow >= 10.1
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _composite(base: np.ndarray, caption: np.ndarray) -> np.ndarray:
    """
    Alpha-composite an RGBA caption image over an RGB base frame.

    Args:
        base:    (H, W, 3) uint8 — the video frame.
        caption: (H, W, 4) uint8 — the caption with alpha channel.

    Returns:
        (H, W, 3) uint8 composited result.
    """
    alpha = caption[:, :, 3:4].astype(np.float32) / 255.0
    fg    = caption[:, :, :3].astype(np.float32)
    bg    = base.astype(np.float32)
    out   = bg * (1 - alpha) + fg * alpha
    return np.clip(out, 0, 255).astype(np.uint8)
