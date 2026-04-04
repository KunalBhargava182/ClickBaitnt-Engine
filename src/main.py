"""
Auto-Shorts Engine — Master Orchestrator
=========================================

Wires every pipeline stage together and drives the scheduler.

Pipeline (one video run)
------------------------
  1. Trend discovery   → pick a trending topic
  2. Script generation → Gemini writes a 45-second narration
  3. Script validation → word count, hook, duration gates
  4. Voice generation  → ElevenLabs TTS (Edge-TTS fallback)
  5. Audio processing  → trim silence, LUFS normalise, mix music
  6. Whisper alignment → word-level timestamps for subtitles
  7. Visual generation → Stability AI images (Pexels fallback)
  8. Video assembly    → motion + overlays + subtitles → MP4
  9. Video validation  → resolution, duration, codec checks
  10. YouTube upload   → resumable upload (skipped in --dry-run)
  11. Tracker update   → write row to Excel spreadsheet
  12. Cleanup          → archive final video, delete intermediates

CLI usage
---------
  python -m src.main --schedule            # start daily sequential scheduler
  python -m src.main --run-batch           # run today's 3-video batch right now
  python -m src.main --run-now             # one immediate video
  python -m src.main --run-now --topic "Your topic here"
  python -m src.main --run-now --dry-run   # full run, skip upload
  python -m src.main --test                # same as --run-now --dry-run with stage report
  python main.py --test                    # shorthand from project root
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log

# ------------------------------------------------------------------ #
#  Pipeline                                                           #
# ------------------------------------------------------------------ #

class Pipeline:
    """
    Orchestrates one complete video production run.

    All heavy components are lazy-initialised on first use so that
    importing this module doesn't incur start-up cost.
    """

    def __init__(self) -> None:
        self._cfg = get_config()
        self._root = get_project_root()

    # ---------------------------------------------------------------- #
    #  Entry point                                                      #
    # ---------------------------------------------------------------- #

    def run(
        self,
        topic:    Optional[str] = None,
        dry_run:  bool          = False,
        language: str           = "en",
    ) -> dict:
        """
        Execute the full pipeline for one video.

        Args:
            topic:   Override trend discovery with a specific topic.
                     Pass None to discover automatically.
            dry_run: If True, skip YouTube upload and Excel write.

        Returns:
            Summary dict: {video_id, topic, status, youtube_url, video_path}.

        Raises:
            RuntimeError: Any unrecoverable stage failure.
        """
        video_id = _make_video_id()
        result   = {
            "video_id":    video_id,
            "topic":       topic or "",
            "status":      "failed",
            "youtube_url": "",
            "video_path":  "",
        }

        log.info("pipeline.run.start", video_id=video_id, dry_run=dry_run, language=language)

        # --- Stage 1: Trend Discovery -----------------------------------
        trend_source = "manual"
        trend_score  = 100.0

        if not topic:
            topic, trend_source, trend_score = self._discover_topic()

        result["topic"] = topic
        log.info(
            "pipeline.topic_selected",
            topic=topic,
            source=trend_source,
            score=trend_score,
        )

        # --- Stage 2 & 3: Script Generation + Validation ---------------
        script   = self._generate_script(topic, video_id, language=language)
        category = script.get("category", "general")

        # --- Stage 4: Voice Generation ----------------------------------
        raw_audio = self._generate_voice(script, video_id, language=language)

        # --- Stage 5: Audio Processing ----------------------------------
        processed_audio = self._process_audio(raw_audio, video_id)

        # --- Stage 6: Whisper Alignment ---------------------------------
        word_segments = self._align_audio(processed_audio, language=language)

        # --- Stage 7: Visual Generation ---------------------------------
        image_paths = self._generate_images(script, video_id)

        # --- Stage 8: Video Assembly ------------------------------------
        video_path = self._assemble_video(
            script, image_paths, processed_audio, word_segments, video_id
        )
        result["video_path"] = str(video_path)

        # --- Stage 9: Video Validation ----------------------------------
        self._validate_video(video_path)

        # --- Stage 10: YouTube Upload -----------------------------------
        youtube_url = ""
        if not dry_run:
            youtube_url = self._upload(script, video_path, video_id)
            result["youtube_url"] = youtube_url

        # --- Stage 11: Tracker ------------------------------------------
        if not dry_run:
            self._update_tracker(
                script       = script,
                video_id     = video_id,
                video_path   = video_path,
                youtube_url  = youtube_url,
                trend_source = trend_source,
                trend_score  = trend_score,
            )

        # --- Stage 12: Cleanup ------------------------------------------
        self._cleanup(video_id, video_path)

        result["status"] = "uploaded" if not dry_run else "rendered"
        log.info(
            "pipeline.run.complete",
            video_id=video_id,
            status=result["status"],
            youtube_url=youtube_url or "(dry-run)",
        )
        return result

    # ---------------------------------------------------------------- #
    #  Stage implementations                                            #
    # ---------------------------------------------------------------- #

    def _discover_topic(self) -> tuple[str, str, float]:
        """Return (topic_str, source_name, trend_score)."""
        from src.trend_discovery.google_trends import GoogleTrendsFetcher
        from src.trend_discovery.newsapi_trends import NewsAPITrendsFetcher
        from src.trend_discovery.trend_scorer import TrendScorer
        from src.trend_discovery.topic_filter import TopicFilter

        cfg    = self._cfg.trends
        sources = cfg.get("sources", {})

        raw: list[dict] = []

        niches = cfg.get("niches", [])

        if sources.get("google_trends", True):
            try:
                raw.extend(GoogleTrendsFetcher(niches=niches).fetch())
                log.info("pipeline.trends.google_trends.fetched", count=len(raw))
            except Exception as exc:
                log.warning("pipeline.trends.google_trends.failed", error=str(exc))

        if sources.get("newsapi", True):
            try:
                before = len(raw)
                raw.extend(NewsAPITrendsFetcher(niches=niches).fetch())
                log.info(
                    "pipeline.trends.newsapi.fetched",
                    count=len(raw) - before,
                )
            except Exception as exc:
                log.warning("pipeline.trends.newsapi.failed", error=str(exc))

        if not raw:
            raise RuntimeError(
                "Trend discovery: all sources returned zero topics. "
                "Check API keys in .env."
            )

        blacklist = cfg.get("blacklist_keywords", [])
        min_score = cfg.get("min_trend_score", 60)

        scored   = TrendScorer(niches=niches, blacklist=blacklist, min_trend_score=min_score).get_top_topics(raw)
        filtered = TopicFilter(blacklist=blacklist).filter_topics(scored)

        if not filtered:
            raise RuntimeError(
                "All discovered topics were filtered out (safety / visual richness). "
                "Try again later or pass --topic manually."
            )

        top          = filtered[0]
        topic_str    = top["topic"]
        sources_used = top.get("sources", [trend_source_label(top)])
        source       = ", ".join(sources_used) if isinstance(sources_used, list) else str(sources_used)
        score        = float(top.get("trend_score", 0.0))

        return topic_str, source, score

    def _generate_script(self, topic: str, video_id: str, language: str = "en") -> dict:
        """Run ScriptGenerator + ScriptValidator; return validated script."""
        from src.script_engine.script_generator import ScriptGenerator
        from src.script_engine.script_validator import ScriptValidator

        log.info("pipeline.script.generate", topic=topic, language=language)
        script = ScriptGenerator().generate(topic, video_id, language=language)

        log.info("pipeline.script.validate")
        # For Hindi, skip the LLM hook check (Gemini evaluates English hooks only)
        use_llm = (language == "en")
        ScriptValidator(use_llm_hook_check=use_llm).validate(script)

        return script

    def _generate_voice(self, script: dict, video_id: str, language: str = "en") -> Path:
        """TTS → raw .mp3 audio."""
        from src.voice.tts_engine import TTSEngine

        text = script.get("script_text", "")
        log.info("pipeline.voice.generate", chars=len(text), language=language)
        return TTSEngine().generate(text, video_id, language=language)

    def _process_audio(self, raw_audio: Path, video_id: str) -> Path:
        """Normalise, mix music, export WAV."""
        from src.voice.audio_processor import AudioProcessor

        log.info("pipeline.audio.process", src=raw_audio.name)
        return AudioProcessor().process(raw_audio, video_id)

    def _align_audio(self, audio_path: Path, language: str = "en") -> list:
        """Whisper word-level alignment; returns [] on failure (subtitles skipped)."""
        from src.subtitles.whisper_align import WhisperAligner

        if not self._cfg.subtitles.get("enabled", True):
            log.info("pipeline.subtitles.disabled")
            return []

        try:
            log.info("pipeline.whisper.align", audio=audio_path.name, language=language)
            segments = WhisperAligner().align(audio_path, language=language)
            log.info("pipeline.whisper.done", words=len(segments))
            return segments
        except Exception as exc:
            log.warning(
                "pipeline.whisper.failed_skipping_subtitles",
                error=str(exc)[:120],
            )
            return []

    def _generate_images(self, script: dict, video_id: str) -> list[Path]:
        """Generate one image per scene."""
        from src.visuals.image_generator import ImageGenerator

        scenes = script.get("scenes", [])
        log.info("pipeline.images.generate", scenes=len(scenes))
        return ImageGenerator().generate_all(scenes, video_id)

    def _assemble_video(
        self,
        script:        dict,
        image_paths:   list[Path],
        audio_path:    Path,
        word_segments: list,
        video_id:      str,
    ) -> Path:
        """Compose final MP4."""
        from src.video.video_composer import VideoComposer

        scenes = script.get("scenes", [])
        log.info("pipeline.video.compose", scenes=len(scenes))
        return VideoComposer().compose(
            scenes        = scenes,
            image_paths   = image_paths,
            audio_path    = audio_path,
            word_segments = word_segments,
            video_id      = video_id,
        )

    def _validate_video(self, video_path: Path) -> None:
        """Gate: raise RuntimeError if the video fails validation."""
        from src.video.video_validator import VideoValidator

        result = VideoValidator().validate(video_path)
        if not result.valid:
            raise RuntimeError(
                f"Video validation failed:\n{result}"
            )
        log.info(
            "pipeline.video.valid",
            duration_s=result.info.get("duration_s"),
            size_mb=result.info.get("size_mb"),
        )

    def _upload(self, script: dict, video_path: Path, video_id: str) -> str:
        """Build metadata and upload to YouTube; return URL."""
        from src.upload.metadata_builder import MetadataBuilder
        from src.upload.youtube_uploader import YouTubeUploader

        metadata = MetadataBuilder().build(script, video_id)
        log.info("pipeline.upload.start", title=metadata["title"][:60])
        url = YouTubeUploader().upload(video_path, metadata, video_id)
        log.info("pipeline.upload.done", url=url)
        return url

    def _update_tracker(
        self,
        script:       dict,
        video_id:     str,
        video_path:   Path,
        youtube_url:  str,
        trend_source: str,
        trend_score:  float,
    ) -> None:
        """Write / update the Excel tracking row."""
        from src.tracker.excel_tracker import ExcelTracker
        from src.tracker.models import VideoRecord

        record = VideoRecord.from_script(
            script       = script,
            video_id     = video_id,
            trend_source = trend_source,
            trend_score  = trend_score,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.update_status("uploaded")

        ExcelTracker().append(record)
        log.info("pipeline.tracker.updated", video_id=video_id)

    def _cleanup(self, video_id: str, video_path: Path) -> None:
        """Archive the final video and delete intermediate files."""
        from src.utils.cleanup import CleanupManager

        try:
            CleanupManager().full_cleanup(video_id, video_path)
        except Exception as exc:
            log.warning("pipeline.cleanup.failed", error=str(exc)[:120])


# ------------------------------------------------------------------ #
#  Scheduler                                                          #
# ------------------------------------------------------------------ #

class Scheduler:
    """
    Sequential daily scheduler.

    Waits until daily_start_hour (IST), then runs videos_per_day videos
    one after another, sleeping post_interval_hours between each upload.
    After the batch is done, waits until the next daily_start_hour and repeats.
    Runs until SIGINT / SIGTERM.
    """

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline
        self._cfg      = get_config().scheduler
        self._stop     = False

    def start(self) -> None:
        """Run forever until SIGINT / SIGTERM."""

        def _shutdown(signum, frame):
            log.info("scheduler.shutdown_signal_received")
            self._stop = True
            sys.exit(0)

        signal.signal(signal.SIGTERM, _shutdown)

        tz_name    = self._cfg.get("timezone", "Asia/Kolkata")
        start_hour = int(self._cfg.get("daily_start_hour", 9))
        log.info("scheduler.starting", daily_start_hour=start_hour, tz=tz_name)

        try:
            while not self._stop:
                self._wait_until_daily_start()
                if self._stop:
                    break
                self._run_daily_batch()
        except (KeyboardInterrupt, SystemExit):
            log.info("scheduler.stopped")

    def _wait_until_daily_start(self) -> None:
        """Sleep until daily_start_hour in the configured timezone."""
        try:
            import pytz
        except ImportError as exc:
            raise ImportError("pytz not installed. Run: pip install pytz") from exc

        tz_name    = self._cfg.get("timezone", "Asia/Kolkata")
        start_hour = int(self._cfg.get("daily_start_hour", 9))
        tz         = pytz.timezone(tz_name)

        from datetime import timedelta
        now_local = datetime.now(tz)
        target    = now_local.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        if now_local >= target:
            target += timedelta(days=1)

        wait_s = (target - now_local).total_seconds()
        log.info(
            "scheduler.waiting_for_daily_start",
            start_hour=start_hour,
            tz=tz_name,
            wait_minutes=round(wait_s / 60),
        )

        while wait_s > 0 and not self._stop:
            chunk   = min(wait_s, 60.0)
            time.sleep(chunk)
            wait_s -= chunk

    def _run_daily_batch(self) -> None:
        """Run videos_per_day videos sequentially with post_interval_hours between each."""
        cfg            = self._cfg
        videos_per_day = int(cfg.get("videos_per_day", 3))
        interval_s     = float(cfg.get("post_interval_hours", 5)) * 3600
        lang_seq       = cfg.get("language_sequence", ["hi", "en", "hi"])
        max_retries    = int(cfg.get("max_retries", 3))
        retry_on_fail  = bool(cfg.get("retry_on_failure", True))

        log.info("scheduler.batch.start", videos=videos_per_day)

        for i in range(videos_per_day):
            if self._stop:
                break

            language = lang_seq[i % len(lang_seq)]
            log.info(
                "scheduler.batch.video",
                index=i + 1,
                total=videos_per_day,
                language=language,
            )

            for attempt in range(1, max_retries + 1):
                try:
                    self._pipeline.run(language=language)
                    log.info("scheduler.batch.video_done", index=i + 1)
                    break
                except Exception as exc:
                    log.error(
                        "scheduler.batch.video_failed",
                        index=i + 1,
                        attempt=attempt,
                        error=str(exc)[:200],
                    )
                    if not retry_on_fail or attempt == max_retries:
                        log.error("scheduler.batch.giving_up", index=i + 1)
                        break
                    wait = 60 * attempt
                    log.info("scheduler.batch.retrying", wait_s=wait)
                    time.sleep(wait)

            # Wait between uploads (skip after the last video)
            if i < videos_per_day - 1 and not self._stop:
                interval_hours = cfg.get("post_interval_hours", 5)
                log.info(
                    "scheduler.batch.waiting_between_videos",
                    interval_hours=interval_hours,
                )
                remaining = interval_s
                while remaining > 0 and not self._stop:
                    chunk      = min(remaining, 60.0)
                    time.sleep(chunk)
                    remaining -= chunk

        log.info("scheduler.batch.complete")


# ------------------------------------------------------------------ #
#  CLI                                                                #
# ------------------------------------------------------------------ #

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-shorts-engine",
        description="Automated faceless YouTube Shorts pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --schedule
  python -m src.main --run-now
  python -m src.main --run-now --topic "Scientists discover ocean waves could power the world"
  python -m src.main --run-now --dry-run
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--schedule",
        action="store_true",
        help="Start the scheduler (runs indefinitely, 3 videos/day).",
    )
    group.add_argument(
        "--run-now",
        action="store_true",
        dest="run_now",
        help="Produce one video immediately and exit.",
    )
    group.add_argument(
        "--test",
        action="store_true",
        help=(
            "Full pipeline test: trend discovery → video render. "
            "Skips YouTube upload and tracker. Prints a stage-by-stage report."
        ),
    )
    group.add_argument(
        "--run-batch",
        action="store_true",
        dest="run_batch",
        help=(
            "Run all videos_per_day videos now, back-to-back, "
            "with post_interval_hours between each upload. "
            "Uses language_sequence from config. Then exits."
        ),
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        metavar="TOPIC",
        help="Override trend discovery with a specific topic.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Run full pipeline but skip YouTube upload and tracker write.",
    )
    parser.add_argument(
        "--splitscreen",
        action="store_true",
        help="Enable split-screen brain rot mode for this run only",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """
    CLI entry point.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    # Ensure UTF-8 output on Windows (cp1252 consoles reject em-dashes etc.)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = _build_parser()
    args   = parser.parse_args(argv)

    if args.splitscreen:
        config = get_config()
        config['video']['mode'] = 'splitscreen'
        log.info("Split-screen mode activated for this run")

    pipeline  = Pipeline()

    if args.run_now:
        try:
            result = pipeline.run(topic=args.topic, dry_run=args.dry_run)
            _print_summary(result)
            return 0
        except Exception as exc:
            log.error("main.run_now.failed", error=str(exc))
            print(f"\n[ERROR] Pipeline failed: {exc}", file=sys.stderr)
            return 1

    if args.test:
        return _run_test(pipeline, args.topic)

    if args.run_batch:
        return _run_batch(pipeline)

    if args.schedule:
        if args.topic:
            print(
                "[WARN] --topic is ignored when running the scheduler.",
                file=sys.stderr,
            )
        Scheduler(pipeline).start()
        return 0

    return 0


def _run_test(pipeline: "Pipeline", topic: Optional[str] = None) -> int:
    """
    Full pipeline integration test (no upload).

    Runs every stage and prints a pass/fail report for each one.
    Returns 0 on success, 1 if any stage fails.
    """
    import traceback

    W = 60
    PASS = "\033[92m PASS \033[0m"
    FAIL = "\033[91m FAIL \033[0m"

    print("\n" + "=" * W)
    print("  AUTO-SHORTS-ENGINE — Integration Test")
    print("  Trend discovery -> script -> voice -> video (no upload)")
    print("=" * W + "\n")

    # Override the pipeline to instrument each stage
    stages = [
        "trend_discovery",
        "script_generation",
        "voice_generation",
        "audio_processing",
        "whisper_alignment",
        "image_generation",
        "video_assembly",
        "video_validation",
        "cleanup",
    ]
    results: dict[str, tuple[bool, str]] = {}

    # ── Run the pipeline with per-stage timing ──────────────────────
    video_id = _make_video_id()
    print(f"  Video ID : {video_id}")
    print(f"  Topic    : {topic or '(auto-discover)'}\n")

    try:
        # Stage 1: Trend discovery (or use provided topic)
        t0 = time.monotonic()
        if topic:
            discovered_topic  = topic
            trend_source      = "manual"
            trend_score       = 100.0
        else:
            discovered_topic, trend_source, trend_score = pipeline._discover_topic()
        elapsed = time.monotonic() - t0
        results["trend_discovery"] = (True, f"{discovered_topic!r}  [{elapsed:.1f}s]")
        print(f"  [{PASS}] trend_discovery  — {discovered_topic[:50]}  ({elapsed:.1f}s)")

        # Stage 2: Script generation
        t0 = time.monotonic()
        script = pipeline._generate_script(discovered_topic, video_id)
        elapsed = time.monotonic() - t0
        word_count = len(script.get("script_text", "").split())
        results["script_generation"] = (True, f"{word_count} words  [{elapsed:.1f}s]")
        print(f"  [{PASS}] script_generation — {word_count} words  ({elapsed:.1f}s)")

        # Stage 3: Voice generation
        t0 = time.monotonic()
        raw_audio = pipeline._generate_voice(script, video_id)
        elapsed = time.monotonic() - t0
        size_kb = raw_audio.stat().st_size // 1024 if raw_audio.exists() else 0
        results["voice_generation"] = (True, f"{raw_audio.name}  {size_kb} KB  [{elapsed:.1f}s]")
        print(f"  [{PASS}] voice_generation  — {raw_audio.name}  ({size_kb} KB, {elapsed:.1f}s)")

        # Stage 4: Audio processing
        t0 = time.monotonic()
        processed_audio = pipeline._process_audio(raw_audio, video_id)
        elapsed = time.monotonic() - t0
        results["audio_processing"] = (True, f"{processed_audio.name}  [{elapsed:.1f}s]")
        print(f"  [{PASS}] audio_processing  — {processed_audio.name}  ({elapsed:.1f}s)")

        # Stage 5: Whisper alignment
        t0 = time.monotonic()
        word_segments = pipeline._align_audio(processed_audio)
        elapsed = time.monotonic() - t0
        results["whisper_alignment"] = (True, f"{len(word_segments)} word segments  [{elapsed:.1f}s]")
        print(f"  [{PASS}] whisper_alignment — {len(word_segments)} word segments  ({elapsed:.1f}s)")

        # Stage 6: Image generation
        t0 = time.monotonic()
        image_paths = pipeline._generate_images(script, video_id)
        elapsed = time.monotonic() - t0
        results["image_generation"] = (True, f"{len(image_paths)} images  [{elapsed:.1f}s]")
        print(f"  [{PASS}] image_generation  — {len(image_paths)} images  ({elapsed:.1f}s)")

        # Stage 7: Video assembly
        t0 = time.monotonic()
        video_path = pipeline._assemble_video(
            script, image_paths, processed_audio, word_segments, video_id
        )
        elapsed = time.monotonic() - t0
        size_mb = video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0
        results["video_assembly"] = (True, f"{video_path.name}  {size_mb:.1f} MB  [{elapsed:.1f}s]")
        print(f"  [{PASS}] video_assembly    — {video_path.name}  ({size_mb:.1f} MB, {elapsed:.1f}s)")

        # Stage 8: Video validation
        t0 = time.monotonic()
        pipeline._validate_video(video_path)
        elapsed = time.monotonic() - t0
        results["video_validation"] = (True, f"[{elapsed:.1f}s]")
        print(f"  [{PASS}] video_validation  — all gates passed  ({elapsed:.1f}s)")

        # Stage 9: Cleanup
        t0 = time.monotonic()
        pipeline._cleanup(video_id, video_path)
        elapsed = time.monotonic() - t0
        results["cleanup"] = (True, f"[{elapsed:.1f}s]")
        print(f"  [{PASS}] cleanup           — intermediates removed  ({elapsed:.1f}s)")

    except Exception as exc:
        # Find which stage failed by seeing which results are missing
        for stage in stages:
            if stage not in results:
                results[stage] = (False, str(exc)[:120])
                print(f"\n  [{FAIL}] {stage}")
                print(f"         Error: {exc}")
                if log:
                    log.error(f"test.{stage}.failed", error=str(exc))
                traceback.print_exc()
                break

    # ── Final report ────────────────────────────────────────────────
    passed = sum(1 for ok, _ in results.values() if ok)
    total  = len(stages)
    all_ok = passed == total

    print()
    print("─" * W)
    print(f"  Result : {'ALL STAGES PASSED' if all_ok else f'{passed}/{total} stages passed'}")
    if all_ok:
        print("  Status : READY TO PRODUCE VIDEOS")
    else:
        print("  Status : FIX ERRORS ABOVE BEFORE SCHEDULING")
    print("─" * W + "\n")

    return 0 if all_ok else 1


def _run_batch(pipeline: "Pipeline") -> int:
    """
    Run all videos_per_day videos immediately, one after another,
    sleeping post_interval_hours between each upload.

    Language for each video comes from config.scheduler.language_sequence.
    Returns 0 when done (errors per-video are logged but don't abort the batch).
    """
    cfg_s          = get_config().scheduler
    videos_per_day = int(cfg_s.get("videos_per_day", 3))
    interval_s     = float(cfg_s.get("post_interval_hours", 5)) * 3600
    lang_seq       = cfg_s.get("language_sequence", ["hi", "en", "hi"])

    W = 60
    print("\n" + "=" * W)
    print("  Auto-Shorts Engine — Batch Run")
    print(f"  Videos: {videos_per_day}  |  Interval: {cfg_s.get('post_interval_hours', 5)}h between posts")
    print(f"  Languages: {lang_seq}")
    print("=" * W + "\n")

    log.info("main.run_batch.start", videos=videos_per_day)

    for i in range(videos_per_day):
        language = lang_seq[i % len(lang_seq)]
        print(f"\n[{i+1}/{videos_per_day}] Starting video — language={language}")
        log.info("main.run_batch.video", index=i + 1, total=videos_per_day, language=language)

        try:
            result = pipeline.run(language=language)
            _print_summary(result)
        except Exception as exc:
            log.error("main.run_batch.video_failed", index=i + 1, error=str(exc))
            print(f"\n  [ERROR] Video {i+1} failed: {exc}", file=sys.stderr)

        if i < videos_per_day - 1:
            hours = cfg_s.get("post_interval_hours", 5)
            print(f"\n  Waiting {hours}h before next video...")
            log.info("main.run_batch.waiting", interval_hours=hours)
            time.sleep(interval_s)

    print("\n" + "=" * W)
    print("  Batch complete.")
    print("=" * W + "\n")
    log.info("main.run_batch.complete")
    return 0


def _print_summary(result: dict) -> None:
    """Print a human-readable summary after a --run-now run."""
    print("\n" + "=" * 60)
    print("  Auto-Shorts Engine — Run Complete")
    print("=" * 60)
    print(f"  Video ID    : {result['video_id']}")
    print(f"  Topic       : {result['topic']}")
    print(f"  Status      : {result['status']}")
    if result.get("youtube_url"):
        print(f"  YouTube URL : {result['youtube_url']}")
    if result.get("video_path"):
        print(f"  Video file  : {result['video_path']}")
    print("=" * 60 + "\n")


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _make_video_id() -> str:
    """Return a timestamp-based unique video identifier."""
    return f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def trend_source_label(topic_dict: dict) -> str:
    """Extract a readable source label from a raw topic dict."""
    return topic_dict.get("source", topic_dict.get("niche", "unknown"))


# ------------------------------------------------------------------ #
#  Entry point                                                        #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    sys.exit(main())
