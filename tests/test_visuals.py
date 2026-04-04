"""
Tests for Phase 5: Visual Generation.

Covers:
- ImageGenerator: provider selection, Stability fallback to Pexels, image processing
- MotionEngine: each motion style produces correct clip dimensions
- OverlayEngine: layer application produces correct output

Run with: python -m pytest tests/test_visuals.py -v
"""

import io
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _make_png_bytes(width: int = 1080, height: int = 1920) -> bytes:
    """Create a minimal valid PNG image as bytes."""
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(100, 150, 200)).save(buf, "PNG")
    return buf.getvalue()


def _make_jpeg_bytes(width: int = 800, height: int = 1200) -> bytes:
    """Create a minimal valid JPEG image as bytes."""
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(200, 100, 50)).save(buf, "JPEG")
    return buf.getvalue()


# ------------------------------------------------------------------ #
#  ImageGenerator tests                                               #
# ------------------------------------------------------------------ #

class TestImageGenerator:

    def test_generate_scene_uses_pexels_when_no_stability_key(self, tmp_path):
        """When STABILITY_API_KEY is absent, falls through to Pexels."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        jpeg_bytes = _make_jpeg_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": "", "PEXELS_API_KEY": "px_test"}):
            with patch.object(gen, "_fetch_pexels", return_value=jpeg_bytes) as mock_pexels:
                result = gen.generate_scene_image("ocean waves crashing", 1, "vid_001")

        mock_pexels.assert_called_once()
        assert result.exists()
        assert result.suffix == ".png"

    def test_generate_scene_uses_stability_when_key_present(self, tmp_path):
        """When STABILITY_API_KEY is set, Stability AI is called first."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        png_bytes = _make_png_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": "sk-realkey", "PEXELS_API_KEY": "px_test"}):
            with patch.object(gen, "_generate_stability", return_value=png_bytes) as mock_stab:
                result = gen.generate_scene_image("futuristic city", 2, "vid_002")

        mock_stab.assert_called_once()
        assert result.exists()

    def test_generate_scene_falls_back_to_pexels_on_stability_failure(self, tmp_path):
        """When Stability AI raises an exception, Pexels is used as fallback."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        jpeg_bytes = _make_jpeg_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": "sk-realkey", "PEXELS_API_KEY": "px_test"}):
            with patch.object(gen, "_generate_stability", side_effect=RuntimeError("API down")):
                with patch.object(gen, "_fetch_pexels", return_value=jpeg_bytes) as mock_pexels:
                    result = gen.generate_scene_image("mountain vista", 3, "vid_003")

        mock_pexels.assert_called_once()
        assert result.exists()

    def test_generate_scene_raises_when_all_providers_fail(self, tmp_path):
        """If both Stability and Pexels fail, a RuntimeError is raised."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        with patch.dict(os.environ, {"STABILITY_API_KEY": "sk-realkey"}):
            with patch.object(gen, "_generate_stability", side_effect=RuntimeError("Stab down")):
                with patch.object(gen, "_fetch_pexels", side_effect=RuntimeError("Pexels down")):
                    with pytest.raises(RuntimeError, match="All image providers failed"):
                        gen.generate_scene_image("sunset beach", 4, "vid_004")

    def test_force_pexels_skips_stability(self, tmp_path):
        """force_pexels=True skips Stability AI entirely."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        jpeg_bytes = _make_jpeg_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": "sk-realkey"}):
            with patch.object(gen, "_generate_stability") as mock_stab:
                with patch.object(gen, "_fetch_pexels", return_value=jpeg_bytes):
                    gen.generate_scene_image("forest trail", 1, "vid_005", force_pexels=True)

        mock_stab.assert_not_called()

    def test_output_is_exactly_1080x1920(self, tmp_path):
        """Output image is exactly 1080×1920 regardless of input size."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        # Input is a non-standard size (landscape)
        landscape_bytes = _make_jpeg_bytes(width=1920, height=1080)

        with patch.dict(os.environ, {"STABILITY_API_KEY": ""}):
            with patch.object(gen, "_fetch_pexels", return_value=landscape_bytes):
                result = gen.generate_scene_image("test scene", 1, "vid_resize")

        img = Image.open(result)
        assert img.size == (1080, 1920), f"Expected 1080×1920, got {img.size}"

    def test_generate_all_returns_one_path_per_scene(self, tmp_path):
        """generate_all() returns exactly one path per scene."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        scenes = [
            {"scene_number": 1, "visual_prompt": "Prompt one"},
            {"scene_number": 2, "visual_prompt": "Prompt two"},
            {"scene_number": 3, "visual_prompt": "Prompt three"},
        ]

        jpeg_bytes = _make_jpeg_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": ""}):
            with patch.object(gen, "_fetch_pexels", return_value=jpeg_bytes):
                paths = gen.generate_all(scenes, "vid_all")

        assert len(paths) == 3
        for p in paths:
            assert p.exists()

    def test_resize_crop_center_produces_correct_size(self):
        """_resize_crop_center always returns a 1080×1920 PIL Image."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()

        for w, h in [(800, 600), (1920, 1080), (400, 800), (1080, 1920)]:
            img_bytes = _make_jpeg_bytes(w, h)
            result = gen._resize_crop_center(img_bytes)
            assert result.size == (1080, 1920), f"Input {w}×{h} → {result.size}"

    def test_color_grade_output_is_rgb(self):
        """_apply_color_grade returns an RGB image of same dimensions."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        img = Image.new("RGB", (1080, 1920), color=(128, 100, 80))
        result = gen._apply_color_grade(img)

        assert result.mode == "RGB"
        assert result.size == (1080, 1920)

    def test_dummy_stability_key_is_treated_as_absent(self, tmp_path):
        """Keys starting with 'sk-xx' are treated as placeholder (not real)."""
        from src.visuals.image_generator import ImageGenerator

        gen = ImageGenerator()
        gen._images_dir = tmp_path

        jpeg_bytes = _make_jpeg_bytes()

        with patch.dict(os.environ, {"STABILITY_API_KEY": "sk-xxplaceholder"}):
            with patch.object(gen, "_generate_stability") as mock_stab:
                with patch.object(gen, "_fetch_pexels", return_value=jpeg_bytes):
                    gen.generate_scene_image("clouds", 1, "vid_dummy_key")

        mock_stab.assert_not_called()


# ------------------------------------------------------------------ #
#  MotionEngine tests                                                 #
# ------------------------------------------------------------------ #

class TestMotionEngine:

    def _make_image_file(self, tmp_path, name="scene.png") -> Path:
        p = tmp_path / name
        img = Image.new("RGB", (1080, 1920), color=(100, 150, 200))
        img.save(str(p), "PNG")
        return p

    def test_ken_burns_clip_dimensions(self, tmp_path):
        """Ken Burns style produces a clip of the correct resolution and duration."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        clip = engine.animate(img_path, duration=5.0, scene_number=1, style="ken_burns")

        assert abs(clip.duration - 5.0) < 0.01
        frame = clip.get_frame(0)
        assert frame.shape == (1920, 1080, 3)

    def test_pan_lr_clip_dimensions(self, tmp_path):
        """Pan left-right style produces correct clip dimensions."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        clip = engine.animate(img_path, duration=4.0, scene_number=2, style="pan_lr")

        frame = clip.get_frame(1.0)
        assert frame.shape == (1920, 1080, 3)

    def test_pan_tb_clip_dimensions(self, tmp_path):
        """Pan top-bottom style produces correct clip dimensions."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        clip = engine.animate(img_path, duration=4.0, scene_number=3, style="pan_tb")

        frame = clip.get_frame(2.0)
        assert frame.shape == (1920, 1080, 3)

    def test_zoom_pulse_clip_dimensions(self, tmp_path):
        """Zoom pulse style produces correct clip dimensions."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        clip = engine.animate(img_path, duration=3.0, scene_number=4, style="zoom_pulse")

        frame = clip.get_frame(1.5)
        assert frame.shape == (1920, 1080, 3)

    def test_seed_gives_reproducible_style(self, tmp_path):
        """Same seed always picks the same style (reproducibility check)."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)

        # Call twice with same seed — frames at t=0 should be identical
        clip_a = engine.animate(img_path, duration=3.0, seed=42)
        clip_b = engine.animate(img_path, duration=3.0, seed=42)

        np.testing.assert_array_equal(clip_a.get_frame(0), clip_b.get_frame(0))

    def test_unknown_style_falls_back_to_ken_burns(self, tmp_path):
        """An unrecognised style falls back to ken_burns without raising."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        # Should not raise
        clip = engine.animate(img_path, duration=2.0, style="nonexistent_style")

        frame = clip.get_frame(0)
        assert frame.shape == (1920, 1080, 3)

    def test_fps_is_30(self, tmp_path):
        """Returned clip must be 30 fps."""
        from src.visuals.motion_engine import MotionEngine

        engine = MotionEngine()
        img_path = self._make_image_file(tmp_path)
        clip = engine.animate(img_path, duration=2.0, style="ken_burns")

        assert clip.fps == 30


# ------------------------------------------------------------------ #
#  OverlayEngine tests                                                #
# ------------------------------------------------------------------ #

class TestOverlayEngine:

    def _make_base_clip(self, duration: float = 3.0):
        """Create a solid-colour VideoClip as base input."""
        from moviepy import VideoClip

        def make_frame(t):
            frame = np.full((1920, 1080, 3), 128, dtype=np.uint8)
            return frame

        return VideoClip(make_frame, duration=duration).with_fps(30)

    def test_apply_no_overlays_passthrough(self):
        """With all overlays off, frames are visually identical to source."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip()

        result = engine.apply(
            base,
            add_gradient=False,
            add_progress_bar=False,
            add_vignette=False,
        )

        np.testing.assert_array_equal(
            base.get_frame(1.0),
            result.get_frame(1.0),
        )

    def test_apply_gradient_darkens_bottom(self):
        """Gradient overlay makes the bottom of the frame darker than the top."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip()

        result = engine.apply(
            base,
            add_gradient=True,
            add_progress_bar=False,
            add_vignette=False,
        )

        frame = result.get_frame(1.0)
        top_brightness = frame[100, 540, :].mean()    # near top centre
        bottom_brightness = frame[1850, 540, :].mean()  # near bottom centre

        assert bottom_brightness < top_brightness, (
            "Bottom should be darker than top with gradient overlay"
        )

    def test_apply_progress_bar_at_t0_is_empty(self):
        """Progress bar at t=0 should have (near) zero width."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip(duration=5.0)

        result = engine.apply(
            base,
            add_gradient=False,
            add_progress_bar=True,
            add_vignette=False,
            bar_color=(255, 0, 0),
        )

        frame_t0 = result.get_frame(0.0)
        # At t=0 the bar is width 0 — the top-left pixel should not be red
        # (it might be 1px wide due to integer rounding, test from pixel 5 onward)
        assert frame_t0[3, 50, 0] < 200, "No red bar should be visible at t=0"

    def test_apply_progress_bar_at_end_is_full_width(self):
        """Progress bar at end of clip should span full width."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        duration = 5.0
        base = self._make_base_clip(duration=duration)

        result = engine.apply(
            base,
            add_gradient=False,
            add_progress_bar=True,
            add_vignette=False,
            bar_color=(255, 0, 0),
            bar_height=6,
        )

        # Sample near the end (not exactly at end to avoid edge issues)
        frame_end = result.get_frame(duration - 0.01)
        # Right side of bar should be red (R high, G/B low)
        assert frame_end[3, 1070, 0] > 200, "Bar should be red at right edge near end"

    def test_apply_vignette_darkens_corners(self):
        """Vignette makes corners darker than the centre."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()

        # Uniform white base
        def make_frame(t):
            return np.full((1920, 1080, 3), 200, dtype=np.uint8)

        from moviepy import VideoClip
        base = VideoClip(make_frame, duration=2.0).with_fps(30)

        result = engine.apply(
            base,
            add_gradient=False,
            add_progress_bar=False,
            add_vignette=True,
            vignette_strength=0.5,
        )

        frame = result.get_frame(1.0)
        centre_val = frame[960, 540, :].mean()
        corner_val = frame[10, 10, :].mean()

        assert corner_val < centre_val, "Corners should be darker than centre"

    def test_output_clip_has_correct_duration(self):
        """Output clip has the same duration as the base clip."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip(duration=7.5)
        result = engine.apply(base)

        assert abs(result.duration - 7.5) < 0.01

    def test_output_clip_is_30fps(self):
        """Output clip is 30 fps."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip()
        result = engine.apply(base)

        assert result.fps == 30

    def test_frame_shape_unchanged(self):
        """Output frames have the same shape as input (1920, 1080, 3)."""
        from src.visuals.overlay_engine import OverlayEngine

        engine = OverlayEngine()
        base = self._make_base_clip()
        result = engine.apply(base)

        assert result.get_frame(1.0).shape == (1920, 1080, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
