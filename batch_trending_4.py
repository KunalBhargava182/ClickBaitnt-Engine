"""
batch_trending_4.py — 4 Shorts (1 Current Trend, 3 Evergreen), zero Gemini calls.

Same pipeline as previous batches:
  TTS -> Audio -> Whisper -> Images -> Video -> Upload -> Tracker

Run:
  python batch_trending_4.py
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

# ── 4 hardcoded scripts ───────────────────────────────────────────────────────

SCRIPTS = [

    # VIDEO 1 — CURRENT WORLD TREND (April 2026)
    {
        "topic":    "The Viral 2026 War Lockdown Prank",
        "category": "news",
        "title":    "The Fake Lockdown Notice That Panicked The Country #Shorts",
        "description": (
            "Did you get the terrifying 'War Lockdown' notice yesterday? Here is how "
            "a viral PDF tricked millions of people into panic buying.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Trending #News #FakeNews #AprilFools #India #2026 "
            "#Psychology #Viral #FYP #CurrentEvents #Delhi"
        ),
        "script_text": (
            "Yesterday, millions of people completely panicked over a fake war lockdown. "
            "On April first, 2026, an official-looking PDF started spreading like wildfire "
            "on social media and WhatsApp in India. It claimed that a partial national "
            "lockdown was being enforced immediately due to a sudden war escalation in the "
            "Middle East. People rushed to stock up on groceries, and the panic was real. "
            "But the moment you actually opened the full document, you realized it was just "
            "a massive April Fools prank. Experts say it perfectly proved how easily deepfakes "
            "and fake news can hijack human psychology in seconds, because nobody actually "
            "checks the source before forwarding a message. Did you or anyone in your family "
            "fall for this fake notice yesterday? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Yesterday, millions of people completely panicked over a fake war lockdown. On April first, 2026, an official-looking PDF started spreading like wildfire on social media and WhatsApp in India.",
                "visual_prompt": "people staring at their glowing smartphones with panicked expressions, a massive digital warning sign floating in the background, cinematic news aesthetic, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "It claimed that a partial national lockdown was being enforced immediately due to a sudden war escalation in the Middle East. People rushed to stock up on groceries, and the panic was real.",
                "visual_prompt": "chaotic blurry motion of people rushing through a modern supermarket grabbing groceries, panic buying concept, dramatic lighting, photorealistic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "But the moment you actually opened the full document, you realized it was just a massive April Fools prank. Experts say it perfectly proved how easily deepfakes and fake news can hijack human psychology.",
                "visual_prompt": "a highly official looking government document dissolving into a laughing clown emoji, fake news illusion, digital glitch effect, cinematic 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Because nobody actually checks the source before forwarding a message. Did you or anyone in your family fall for this fake notice yesterday? Comment below and follow ClickBaitnt.",
                "visual_prompt": "a glowing digital chain reaction of WhatsApp forward arrows spreading across a map of India, viral misinformation concept, dark cinematic data visualization",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Trending", "#FakeNews", "#AprilFools", "#India", "#News"
        ],
        "tags": [
            "shorts", "trending", "news", "war lockdown", "fake news", "april fools",
            "india", "whatsapp forward", "viral", "2026", "clickbaitnt", "psychology"
        ],
    },

    # VIDEO 2 — BRAIN / BODY
    {
        "topic":    "The Doorway Effect",
        "category": "science",
        "title":    "Your Brain Deletes Your Memory When You Walk Into A Room #Shorts",
        "description": (
            "Why do you always forget what you needed the second you walk into a new room? "
            "It's a biological glitch called the Doorway Effect.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #BrainFacts #HumanBody #Neuroscience #Psychology "
            "#Science #MindBlown #DidYouKnow #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "Your brain literally deletes your memory every time you walk through a doorway. "
            "Have you ever walked into a room to get something, but the second you cross the "
            "threshold, you completely forget why you are there? You are not losing your mind. "
            "It is a psychological glitch called the Doorway Effect. Your brain is a highly "
            "efficient computer that groups your memories by location. When you enter a new "
            "room, your brain registers the doorway as a physical boundary and literally hits "
            "the refresh button, dumping short-term memories from the previous room to make "
            "space for new information. To remember what you forgot, you usually have to "
            "physically walk backward into the old room to restore the deleted file. What is "
            "the dumbest thing you forgot after walking into a room? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Your brain literally deletes your memory every time you walk through a doorway. Have you ever walked into a room to get something, but the second you cross the threshold, you completely forget why you are there?",
                "visual_prompt": "person standing in a doorway looking incredibly confused with a floating loading icon above their head, memory glitch concept, cinematic lighting, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "You are not losing your mind. It is a psychological glitch called the Doorway Effect. Your brain is a highly efficient computer that groups your memories by location.",
                "visual_prompt": "abstract visualization of a glowing human brain acting like a computer hard drive with digital folders floating around it, neuroscience tech aesthetic, 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "When you enter a new room, your brain registers the doorway as a physical boundary and literally hits the refresh button, dumping short-term memories from the previous room.",
                "visual_prompt": "a glowing digital file labeled 'MEMORY' being thrown into a digital trash can the exact second a person steps through a door, cinematic glitch art",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "To remember what you forgot, you usually have to physically walk backward into the old room to restore the deleted file. What is the dumbest thing you forgot after walking into a room? Comment below and follow ClickBaitnt.",
                "visual_prompt": "person physically walking backwards through a door while a glowing memory bubble pops back into their head, funny psychological concept, warm lighting",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#Neuroscience", "#BrainFacts", "#Psychology", "#HumanBody", "#Science"
        ],
        "tags": [
            "shorts", "doorway effect", "memory", "brain facts", "neuroscience", 
            "psychology", "human body", "forgetting", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 3 — OCEAN MYSTERY
    {
        "topic":    "The Immortal Jellyfish",
        "category": "nature",
        "title":    "This Ocean Animal Literally Cured Death #Shorts",
        "description": (
            "Deep in the ocean lives a tiny jellyfish that hits a biological reset "
            "button whenever it gets old, making it completely immortal.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Ocean #Nature #Biology #Science #Animals "
            "#DeepSea #Immortality #DidYouKnow #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "There is an animal in the ocean that has literally cured death. Deep underwater "
            "lives a tiny creature called the Immortal Jellyfish. Unlike every other living "
            "thing on Earth, when this jellyfish gets old, sick, or injured, it does not die. "
            "Instead, it hits a biological reset button. It shrinks its body, absorbs its own "
            "tentacles, and transforms its cells all the way back into a baby polyp. It then "
            "starts its entire life over again from scratch. It is biologically immortal, capable "
            "of repeating this cycle forever. Scientists are currently studying its DNA to see "
            "if this reverse-aging process could ever be transferred to human cells. Imagine if "
            "humans could just reset back to being a baby when they get old. Would you want to "
            "live forever if you had to start over? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is an animal in the ocean that has literally cured death. Deep underwater lives a tiny creature called the Immortal Jellyfish.",
                "visual_prompt": "glowing bioluminescent tiny jellyfish floating in the dark deep ocean, stunning macro photography, magical underwater aesthetic, cinematic 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 2,
                "narration": "Unlike every other living thing on Earth, when this jellyfish gets old, sick, or injured, it does not die. Instead, it hits a biological reset button.",
                "visual_prompt": "abstract visualization of an aging jellyfish shrinking and transforming into a glowing orb of pure biological energy, reverse aging concept, beautiful lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "It shrinks its body, absorbs its own tentacles, and transforms its cells all the way back into a baby polyp. It then starts its entire life over again from scratch.",
                "visual_prompt": "time-lapse style visualization of a glowing underwater polyp blooming rapidly into a fully grown jellyfish, magical biology, highly detailed 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Scientists are currently studying its DNA to see if this reverse-aging process could ever be transferred to humans. Would you want to live forever if you had to start over? Comment below and follow ClickBaitnt.",
                "visual_prompt": "scientist in a dark lab looking through a microscope at glowing jellyfish DNA that looks like the infinity symbol, science fiction meets reality concept",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#Ocean", "#Nature", "#Biology", "#Immortality", "#Science"
        ],
        "tags": [
            "shorts", "ocean", "jellyfish", "immortality", "biology", "science", 
            "nature", "deep sea", "animals", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 4 — PSYCHOLOGY
    {
        "topic":    "The Spotlight Effect",
        "category": "psychology",
        "title":    "Nobody Is Judging You, You Are Just Hallucinating #Shorts",
        "description": (
            "Do you feel like everyone is staring at you in public? Psychology proves "
            "that your brain is making it all up.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Psychology #MentalHealth #Anxiety #BrainFacts "
            "#Science #HumanBehavior #MindBlown #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "Nobody is actually judging you when you walk into a room. You are just "
            "hallucinating. When you wear a weird shirt, trip in public, or have a bad "
            "hair day, you feel like everyone is staring at you and laughing. But psychology "
            "proves they are not. It is called the Spotlight Effect. Your brain is completely "
            "obsessed with your own survival, so it tricks you into believing that you are "
            "the main character of reality and everyone else is just an audience watching you. "
            "In reality, every single person walking past you is also trapped in their own "
            "Spotlight Effect, worrying entirely about how they look to you. You could walk "
            "outside with your shirt on backwards, and ninety percent of people wouldn't even "
            "notice. What is the most embarrassing thing you thought everyone saw? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Nobody is actually judging you when you walk into a room. You are just hallucinating. When you wear a weird shirt, trip in public, or have a bad hair day...",
                "visual_prompt": "person standing in a crowded room with a massive literal glowing theatrical spotlight shining only on them, feeling anxious, psychological concept art, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "...you feel like everyone is staring at you and laughing. But psychology proves they are not. It is called the Spotlight Effect. Your brain is completely obsessed with your own survival...",
                "visual_prompt": "POV shot walking into a room where every single person's face is replaced by giant judging eyeballs, anxiety hallucination concept, dramatic thriller lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "...so it tricks you into believing that you are the main character of reality and everyone else is just an audience. In reality, every single person walking past you is also trapped in their own Spotlight Effect...",
                "visual_prompt": "crowded city street where every single person has a tiny personal spotlight shining on themselves, ignoring everyone else, deep psychological visualization, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "You could walk outside with your shirt on backwards, and ninety percent of people wouldn't even notice. What is the most embarrassing thing you thought everyone saw? Comment below.",
                "visual_prompt": "person looking relieved while walking through a blurry crowd of people who are all staring down at their own phones, realistic street photography, cinematic",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Psychology", "#MentalHealth", "#Anxiety", "#BrainFacts", "#HumanBehavior"
        ],
        "tags": [
            "shorts", "spotlight effect", "psychology", "anxiety", "mental health", 
            "brain facts", "embarrassing", "human behavior", "clickbaitnt", "viral", "trending"
        ],
    },

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
            trend_source = "batch_trending_4",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"batch_trending_4.py — {script['topic']}"
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
    print("  AUTO-SHORTS-ENGINE — Trending Mix (Batch of 4)")
    print(f"  Uploading {len(SCRIPTS)} videos as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_trend{idx}"

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

        # 45-second delay between uploads
        if idx < len(SCRIPTS):
            print(f"\n  Waiting 45 seconds before next upload...")
            for remaining in range(45, 0, -5):
                print(f"    {remaining}s remaining...", flush=True)
                time.sleep(5)
            print("  Delay complete. Starting next video.\n")

    # ── Summary ────────────────────────────────────────────────────────────
    total_elapsed      = time.monotonic() - total_t0
    total_mm, total_ss = divmod(int(total_elapsed), 60)
    succeeded          = [r for r in results if r["url"]]
    failed             = [r for r in results if r["url"] is None]

    print()
    print("=" * W)
    print("  BATCH COMPLETE — SUMMARY")
    print(f"  {len(succeeded)}/{len(SCRIPTS)} videos uploaded successfully")
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
        print("  YouTube URLs:")
        for r in succeeded:
            print(f"    Video {r['num']:>2}: {r['url']}")

    print()
    print("=" * W)

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())