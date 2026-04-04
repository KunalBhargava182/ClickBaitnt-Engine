"""
single_aphantasia_short.py — 1 Psychology/Brain Fact Short.

Same pipeline as previous batches:
  TTS -> Audio -> Whisper -> Images -> Video -> Upload -> Tracker

Run:
  python single_aphantasia_short.py
"""

import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── 1 hardcoded script ────────────────────────────────────────────────────────

SCRIPTS = [
    {
        "topic":    "Aphantasia - Mind Blindness",
        "category": "psychology",
        "title":    "You Might Be Blind Inside Your Own Mind #Shorts",
        "description": (
            "When you close your eyes, do you actually see things? Aphantasia is a condition "
            "where the brain's 'mind's eye' is completely broken.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Psychology #BrainFacts #HumanBody #Aphantasia "
            "#Science #MindBlown #DidYouKnow #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "Close your eyes and picture a bright red apple. If you just saw pure darkness, "
            "you have a rare brain condition. It is called Aphantasia, or mind blindness. "
            "Most people can literally see images, colors, and faces inside their heads like "
            "a movie screen. But for two percent of the population, their mind's eye is "
            "completely broken. They can describe an apple, but they cannot visually see it "
            "in their imagination. Many people with Aphantasia go their entire lives thinking "
            "that 'picturing something in your head' is just a metaphor. When you closed your "
            "eyes, did you see the red apple, or just pitch black? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Close your eyes and picture a bright red apple. If you just saw pure darkness, you have a rare brain condition.",
                "visual_prompt": "split screen, the left side is a glowing bright red apple, the right side is complete pitch black dark static, psychological brain concept, 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 2,
                "narration": "It is called Aphantasia, or mind blindness. Most people can literally see images, colors, and faces inside their heads like a movie screen.",
                "visual_prompt": "silhouette of a human head with a glowing cinematic movie projector inside the brain showing vibrant colors and images, neuroscience aesthetic, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "But for two percent of the population, their mind's eye is completely broken. They can describe an apple, but they cannot visually see it in their imagination.",
                "visual_prompt": "person trying hard to think with their eyes closed, but a dark empty static void floats above their head, moody cinematic lighting, psychological mystery",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Many people go their entire lives thinking 'picturing something' is just a metaphor. When you closed your eyes, did you see the red apple, or just pitch black? Comment below.",
                "visual_prompt": "glowing red apple slowly fading away into dark digital static and absolute darkness, mind blowing brain fact concept, cinematic lighting",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Aphantasia", "#BrainFacts", "#Psychology", "#HumanBody", "#Science"
        ],
        "tags": [
            "shorts", "aphantasia", "mind blindness", "brain facts", "psychology",
            "human body", "imagination", "science", "clickbaitnt", "viral", "trending"
        ],
    }
]

# ── display helpers ───────────────────────────────────────────────────────────

W    = 66
PASS = "\033[92m PASS \033[0m"
FAIL = "\033[91m FAIL \033[0m"
RUN  = "\033[94m  >>  \033[0m"

def _banner(text):
    print(f"\n  [{text}]")
    print("  " + "-" * (W - 2))

def _ok(label, detail=""):
    suffix = f"  {detail}" if detail else ""
    print(f"  [{PASS}] {label}{suffix}")

def _fail(label, err):
    print(f"  [{FAIL}] {label}", file=sys.stderr)
    print(f"           {err}", file=sys.stderr)

def _running(label):
    print(f"  [{RUN}] {label} ...", flush=True)

# ── single-video pipeline ─────────────────────────────────────────────────────

def run_video(script: dict, video_id: str) -> str:
    """Run all 8 pipeline stages. Returns YouTube URL. Raises on failure."""

    # Stage 1: Voice
    _banner("Stage 1 / 8  —  Voice Generation (TTS)")
    _running("Generating narration audio")
    from src.voice.tts_engine import TTSEngine
    t0        = time.monotonic()
    raw_audio = TTSEngine().generate(script["script_text"], video_id)
    elapsed   = time.monotonic() - t0
    _ok("Voice generated", f"{raw_audio.name}  ({raw_audio.stat().st_size // 1024} KB, {elapsed:.1f}s)")

    # Stage 2: Audio processing
    _banner("Stage 2 / 8  —  Audio Processing (normalise + music mix)")
    _running("Trimming silence, normalising, mixing music")
    from src.voice.audio_processor import AudioProcessor
    t0              = time.monotonic()
    processed_audio = AudioProcessor().process(raw_audio, video_id)
    elapsed         = time.monotonic() - t0
    _ok("Audio processed", f"{processed_audio.name}  ({elapsed:.1f}s)")

    # Stage 3: Whisper alignment
    _banner("Stage 3 / 8  —  Whisper Alignment (word-level timestamps)")
    _running("Running local Whisper model")
    try:
        from src.subtitles.whisper_align import WhisperAligner
        t0            = time.monotonic()
        word_segments = WhisperAligner().align(processed_audio)
        elapsed       = time.monotonic() - t0
        _ok("Alignment complete", f"{len(word_segments)} word segments  ({elapsed:.1f}s)")
        if not word_segments:
            print("  (no word segments — subtitles will be skipped)")
    except Exception as exc:
        print(f"  [WARN] Whisper failed ({exc!s:.80}) — continuing without subtitles")
        word_segments = []

    # Stage 4: Image generation
    _banner("Stage 4 / 8  —  Image Generation (Stability AI / Pexels fallback)")
    from src.visuals.image_generator import ImageGenerator
    gen         = ImageGenerator()
    image_paths = []
    for scene in script["scenes"]:
        n       = scene["scene_number"]
        prompt  = scene["visual_prompt"]
        _running(f"Scene {n}: {prompt[:55]}...")
        t0      = time.monotonic()
        path    = gen.generate_scene_image(prompt, n, video_id)
        elapsed = time.monotonic() - t0
        _ok(f"Scene {n} saved", f"{path.name}  ({path.stat().st_size // 1024} KB, {elapsed:.1f}s)")
        image_paths.append(path)

    # Stage 5: Video assembly
    _banner("Stage 5 / 8  —  Video Assembly (motion + overlays + subtitles)")
    _running("Composing scenes with Ken Burns, gradients, animated captions")
    from src.video.video_composer import VideoComposer
    t0         = time.monotonic()
    video_path = VideoComposer().compose(
        scenes        = script["scenes"],
        image_paths   = image_paths,
        audio_path    = processed_audio,
        word_segments = word_segments,
        video_id      = video_id,
    )
    elapsed = time.monotonic() - t0
    size_mb = video_path.stat().st_size / (1024 * 1024)
    _ok("Video assembled", f"{video_path.name}  ({size_mb:.1f} MB, {elapsed:.1f}s)")

    # Stage 6: Validation
    _banner("Stage 6 / 8  —  Video Validation (ffprobe gates)")
    _running("Checking resolution, duration, codec, audio stream")
    from src.video.video_validator import VideoValidator
    result = VideoValidator().validate(video_path)
    if result.valid:
        dur = result.info.get("duration_s", "?")
        res = f"{result.info.get('width', '?')}x{result.info.get('height', '?')}"
        _ok("Validation passed", f"{res}  {dur}s  {size_mb:.1f} MB")
        for w in result.warnings:
            print(f"  [WARN] {w}")
    else:
        raise RuntimeError(f"Video validation failed: {result}")

    # Stage 7: YouTube upload
    _banner("Stage 7 / 8  —  YouTube Upload (PUBLIC)")
    _running("Building metadata")
    from src.upload.metadata_builder import MetadataBuilder
    metadata = MetadataBuilder().build(script, video_id)
    _ok("Metadata built", f"title={len(metadata['title'])} chars  tags={len(metadata['tags'])}")

    _running("Uploading to YouTube")
    from src.upload.youtube_uploader import YouTubeUploader
    t0          = time.monotonic()
    youtube_url = YouTubeUploader().upload(video_path, metadata, video_id)
    elapsed     = time.monotonic() - t0
    _ok("Uploaded to YouTube", f"{youtube_url}  ({elapsed:.1f}s)")

    # Stage 8: Excel tracker
    _banner("Stage 8 / 8  —  Excel Tracker")
    _running("Writing row to tracking spreadsheet")
    try:
        from src.tracker.excel_tracker import ExcelTracker
        from src.tracker.models import VideoRecord
        record             = VideoRecord.from_script(
            script       = script,
            video_id     = video_id,
            trend_source = "single_aphantasia_short",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"single_aphantasia_short.py — {script['topic']}"
        ExcelTracker().append(record)
        _ok("Tracker updated", "status = 'Posted & Live'")
    except Exception as exc:
        print(f"  [WARN] Tracker write failed: {exc}")

    return youtube_url

# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    total_t0 = time.monotonic()

    print()
    print("=" * W)
    print("  AUTO-SHORTS-ENGINE — Single Psychology Fact")
    print(f"  Uploading {len(SCRIPTS)} video as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_aphantasia"

        print()
        print("=" * W)
        print(f"  VIDEO {idx} / {len(SCRIPTS)}  —  {short_title}")
        print(f"  Video ID : {video_id}")
        print("=" * W)

        t0 = time.monotonic()
        try:
            youtube_url = run_video(script, video_id)
            elapsed     = time.monotonic() - t0
            mm, ss      = divmod(int(elapsed), 60)
            print(f"\n  [{PASS}] VIDEO {idx} LIVE: {youtube_url}  ({mm}m {ss}s)")
            results.append({"num": idx, "title": script["title"], "url": youtube_url, "error": None})
        except Exception as exc:
            elapsed = time.monotonic() - t0
            import traceback
            traceback.print_exc()
            print(f"\n  [{FAIL}] VIDEO {idx} FAILED after {elapsed:.0f}s: {exc}", file=sys.stderr)
            results.append({"num": idx, "title": script["title"], "url": None, "error": str(exc)})

    # ── Summary ────────────────────────────────────────────────────────────
    total_elapsed      = time.monotonic() - total_t0
    total_mm, total_ss = divmod(int(total_elapsed), 60)
    succeeded          = [r for r in results if r["url"]]
    failed             = [r for r in results if r["url"] is None]

    print()
    print("=" * W)
    print("  COMPLETE — SUMMARY")
    print(f"  {len(succeeded)}/{len(SCRIPTS)} video uploaded successfully")
    print(f"  Total time: {total_mm}m {total_ss}s")
    print("=" * W)
    print()
    print(f"  {'#':<3}  {'STATUS':<8}  YOUTUBE URL / ERROR")
    print("  " + "-" * (W - 2))
    for r in results:
        if r["url"]:
            print(f"  {r['num']:<3}  {'OK':<8}  {r['url']}")
        else:
            print(f"  {r['num']:<3}  {'FAILED':<8}  {str(r['error'])[:45]}")

    if succeeded:
        print()
        print("  YouTube URL:")
        for r in succeeded:
            print(f"    Video {r['num']:>2}: {r['url']}")

    print()
    print("=" * W)

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())