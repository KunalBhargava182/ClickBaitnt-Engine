"""
Video composer — assembles the final YouTube Short.

Pipeline:
  1. Load processed audio (WAV/MP3) → measure total duration.
  2. Scale each scene's duration_estimate proportionally to fill the audio.
  3. Per scene: animate image (MotionEngine) → apply overlays (OverlayEngine).
  4. Concatenate scene clips with crossfade transitions.
  5. Render animated word-highlight subtitles (SubtitleRenderer).
  6. Attach audio track.
  7. Export to H.264 / AAC MP4 at 1080 × 1920, 30 fps.

Output: output/videos/{video_id}.mp4
"""

import subprocess
from pathlib import Path
from typing import Optional

from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, VideoClip
from moviepy import concatenate_videoclips

from src.subtitles.subtitle_renderer import SubtitleRenderer
from src.subtitles.whisper_align import WordSegment
from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log
from src.visuals.motion_engine import MotionEngine
from src.visuals.overlay_engine import OverlayEngine

# Pipeline constants
OUT_W = 1080
OUT_H = 1920
FPS   = 30


class VideoComposer:
    """
    Assembles all pipeline artefacts into a single MP4 Short.

    Usage:
        composer = VideoComposer()
        output   = composer.compose(
            scenes        = script["scenes"],
            image_paths   = image_paths,
            audio_path    = processed_audio,
            word_segments = segments,
            video_id      = "vid_001",
        )
    """

    def __init__(self) -> None:
        cfg = get_config()
        vis = cfg.visuals

        self._xfade_dur: float  = float(vis.transitions.get("duration", 0.5))
        self._xfade_type: str   = vis.transitions.get("type", "crossfade")
        self._motion  = MotionEngine()
        self._overlay = OverlayEngine()
        self._sub     = SubtitleRenderer()

        self._output_dir = get_project_root() / "output" / "videos"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def compose(
        self,
        scenes:        list[dict],
        image_paths:   list[Path],
        audio_path:    Path,
        word_segments: list[WordSegment],
        video_id:      str,
        output_path:   Optional[Path] = None,
    ) -> Path:
        """
        Assemble and export the final video.

        Dispatches to _compose_splitscreen() when config video.mode == "splitscreen",
        otherwise runs the standard fullscreen pipeline via _compose_fullscreen().

        Args:
            scenes:        Script scene dicts (need 'scene_number',
                           'duration_estimate').
            image_paths:   1080×1920 scene PNG paths (one per scene, same order).
            audio_path:    Processed audio file (WAV or MP3).
            word_segments: Word-level timestamps from WhisperAligner.
                           Pass [] to skip subtitles.
            video_id:      Unique identifier used for file naming.
            output_path:   Override default output path.

        Returns:
            Path to the exported MP4 file.

        Raises:
            FileNotFoundError: audio_path or any image_path is missing.
            RuntimeError:      FFmpeg not available for video export.
        """
        mode = get_config().get("video", {}).get("mode", "fullscreen")
        if mode == "splitscreen":
            return self._compose_splitscreen(
                scenes, image_paths, audio_path, word_segments, video_id, output_path
            )
        return self._compose_fullscreen(
            scenes, image_paths, audio_path, word_segments, video_id, output_path
        )

    # ------------------------------------------------------------------ #
    #  Fullscreen pipeline (original logic — untouched)                  #
    # ------------------------------------------------------------------ #

    def _compose_fullscreen(
        self,
        scenes:        list[dict],
        image_paths:   list[Path],
        audio_path:    Path,
        word_segments: list[WordSegment],
        video_id:      str,
        output_path:   Optional[Path] = None,
    ) -> Path:
        """Standard fullscreen assembly (original compose() logic)."""
        if output_path is None:
            output_path = self._output_dir / f"{video_id}.mp4"

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        for p in image_paths:
            if not Path(p).exists():
                raise FileNotFoundError(f"Scene image not found: {p}")

        log.info(
            "video_composer.compose.start",
            video_id=video_id,
            scenes=len(scenes),
            images=len(image_paths),
            audio=audio_path.name,
        )

        # 1. Load audio → get total duration
        audio_clip   = AudioFileClip(str(audio_path))
        audio_dur    = audio_clip.duration

        # 2. Scale scene durations to match audio length
        durations = self._scale_durations(scenes, audio_dur)

        # 3. Build per-scene clips (motion + overlay)
        scene_clips: list[VideoClip] = []
        for i, (scene, img_path, dur) in enumerate(
            zip(scenes, image_paths, durations)
        ):
            scene_num = scene.get("scene_number", i + 1)
            log.info(
                "video_composer.build_scene",
                scene=scene_num,
                duration=round(dur, 2),
            )

            # a. Motion animation
            clip = self._motion.animate(
                image_path=Path(img_path),
                duration=dur,
                scene_number=scene_num,
            )

            # b. Overlays (gradient + progress bar + vignette)
            clip = self._overlay.apply(clip)

            scene_clips.append(clip)

        # 4. Concatenate with crossfade transitions
        full_clip = self._concat_with_crossfade(scene_clips)

        # 5. Subtitles
        if word_segments:
            log.info(
                "video_composer.apply_subtitles",
                words=len(word_segments),
            )
            full_clip = self._sub.render(full_clip, word_segments)

        # 6. Attach audio (clamp to shorter of video/audio)
        final_dur = min(full_clip.duration, audio_dur)
        full_clip  = full_clip.subclipped(0, final_dur)
        audio_clip = audio_clip.subclipped(0, final_dur)
        full_clip  = full_clip.with_audio(audio_clip)

        # 7. Export
        log.info(
            "video_composer.exporting",
            output=str(output_path),
            duration=round(final_dur, 2),
        )
        full_clip.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium",
            logger=None,
        )

        audio_clip.close()
        full_clip.close()

        size_mb = output_path.stat().st_size / (1024 * 1024)
        log.info(
            "video_composer.compose.done",
            video_id=video_id,
            output=str(output_path),
            size_mb=round(size_mb, 2),
            duration_s=round(final_dur, 2),
        )
        return output_path

    # ------------------------------------------------------------------ #
    #  Split-screen pipeline                                              #
    # ------------------------------------------------------------------ #

    def _compose_splitscreen(
        self,
        scenes:        list[dict],
        image_paths:   list[Path],
        audio_path:    Path,
        word_segments: list[WordSegment],
        video_id:      str,
        output_path:   Optional[Path] = None,
    ) -> Path:
        """
        Split-screen assembly:
          - Top 60%  (1080×1152): content clip with Ken Burns motion + overlays
          - Bottom 40% (1080×768): looping brain-rot clip (muted)
          - Subtitles near the split boundary (y=1100)
          - Voice audio only (brain-rot audio is stripped)

        Falls back to _compose_fullscreen() if BrainRotFetcher returns None.
        """
        from src.visuals.brain_rot_fetcher import BrainRotFetcher

        ss_cfg      = get_config().get("splitscreen", {})
        top_h:  int = int(ss_cfg.get("top_height",    1152))
        bot_h:  int = int(ss_cfg.get("bottom_height",  768))

        if output_path is None:
            output_path = self._output_dir / f"{video_id}.mp4"

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        for p in image_paths:
            if not Path(p).exists():
                raise FileNotFoundError(f"Scene image not found: {p}")

        log.info(
            "video_composer.splitscreen.start",
            video_id=video_id,
            scenes=len(scenes),
            top_h=top_h,
            bot_h=bot_h,
        )

        # 1. Load audio → duration
        audio_clip = AudioFileClip(str(audio_path))
        audio_dur  = audio_clip.duration

        # 2. Fetch brain-rot bottom panel
        brain_rot_clip = BrainRotFetcher().get_clip(audio_dur)
        if brain_rot_clip is None:
            log.warning(
                "video_composer.splitscreen.brain_rot_none — falling back to fullscreen"
            )
            audio_clip.close()
            return self._compose_fullscreen(
                scenes, image_paths, audio_path, word_segments, video_id, output_path
            )

        # 3. Scale scene durations
        durations = self._scale_durations(scenes, audio_dur)

        # 4. Build per-scene content clips (full 1080×1920 motion + overlay)
        scene_clips: list[VideoClip] = []
        for i, (scene, img_path, dur) in enumerate(zip(scenes, image_paths, durations)):
            scene_num = scene.get("scene_number", i + 1)
            log.info(
                "video_composer.splitscreen.build_scene",
                scene=scene_num,
                duration=round(dur, 2),
            )
            clip = self._motion.animate(
                image_path=Path(img_path),
                duration=dur,
                scene_number=scene_num,
            )
            clip = self._overlay.apply(clip)
            scene_clips.append(clip)

        # 5. Concatenate content scenes
        content_clip = self._concat_with_crossfade(scene_clips)

        # 6. Clamp content to audio duration
        final_dur    = min(content_clip.duration, audio_dur)
        content_clip = content_clip.subclipped(0, final_dur)
        audio_clip   = audio_clip.subclipped(0, final_dur)

        # 7. Resize content to top panel (1080 × top_h)
        content_top = content_clip.resized((OUT_W, top_h))

        # 8. Ensure brain-rot clip matches final duration
        #    (BrainRotFetcher already trims/loops, but guard against rounding)
        brain_rot = brain_rot_clip.subclipped(0, min(brain_rot_clip.duration, final_dur))

        # 9. Composite: black canvas + top panel + bottom panel
        background = (
            ColorClip(size=(OUT_W, OUT_H), color=(0, 0, 0))
            .with_duration(final_dur)
        )
        composite = CompositeVideoClip(
            [
                background,
                content_top.with_position((0, 0)),
                brain_rot.with_position((0, top_h)),
            ],
            size=(OUT_W, OUT_H),
        )

        # 10. Subtitles at split boundary (y=1100)
        if word_segments:
            log.info(
                "video_composer.splitscreen.apply_subtitles",
                words=len(word_segments),
            )
            composite = self._sub.render(composite, word_segments, mode="splitscreen")

        # 11. Attach voice audio (brain-rot clip audio already stripped)
        composite = composite.with_audio(audio_clip)

        # 12. Export — identical settings to fullscreen
        log.info(
            "video_composer.splitscreen.exporting",
            output=str(output_path),
            duration=round(final_dur, 2),
        )
        composite.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium",
            logger=None,
        )

        audio_clip.close()
        brain_rot_clip.close()
        composite.close()

        size_mb = output_path.stat().st_size / (1024 * 1024)
        log.info(
            "video_composer.splitscreen.done",
            video_id=video_id,
            output=str(output_path),
            size_mb=round(size_mb, 2),
            duration_s=round(final_dur, 2),
        )
        return output_path

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _scale_durations(
        self,
        scenes: list[dict],
        audio_duration: float,
    ) -> list[float]:
        """
        Scale per-scene duration_estimate values so they sum to audio_duration.

        If no estimates are present, distributes time evenly.
        """
        raw = [float(s.get("duration_estimate", 10.0)) for s in scenes]
        total_raw = sum(raw)

        if total_raw <= 0 or len(scenes) == 0:
            even = audio_duration / max(len(scenes), 1)
            return [even] * len(scenes)

        scale = audio_duration / total_raw
        return [round(r * scale, 4) for r in raw]

    def _concat_with_crossfade(self, clips: list[VideoClip]) -> VideoClip:
        """
        Concatenate clips. If more than one clip and crossfade is configured,
        apply crossfadein/crossfadeout with padding overlap.
        Falls back to simple cut concatenation if the effect API is unavailable.
        """
        if len(clips) == 1:
            return clips[0]

        xd = self._xfade_dur
        if xd <= 0 or self._xfade_type != "crossfade":
            return concatenate_videoclips(clips)

        try:
            faded: list[VideoClip] = []
            for i, clip in enumerate(clips):
                if i > 0:
                    clip = clip.crossfadein(xd)
                if i < len(clips) - 1:
                    clip = clip.crossfadeout(xd)
                faded.append(clip)

            return concatenate_videoclips(faded, padding=-xd, method="compose")

        except (AttributeError, TypeError, Exception) as exc:
            log.warning(
                "video_composer.crossfade.fallback_to_cut",
                reason=str(exc)[:100],
            )
            return concatenate_videoclips(clips)
