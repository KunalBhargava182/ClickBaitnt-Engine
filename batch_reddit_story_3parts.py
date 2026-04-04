"""
batch_reddit_story_3parts.py — 3-Part Reddit Story, zero Gemini calls.

Same pipeline as previous batches, but with a custom Pillow intercept
to burn "PART X" into the top center of every generated image.

Run:
  python batch_reddit_story_3parts.py
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Need Pillow for the text overlay
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is not installed. Please run: pip install Pillow")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── 3 hardcoded scripts ───────────────────────────────────────────────────────

SCRIPTS = [
    {
        "part": 1, 
        "title": "I Accidentally Flirted My Way Out Of A Fight Part 1 #Shorts", 
        "description": "Part 1 of 3 — My friend has a crush. She sends me on a mission. But there's a girl giving me death stares and I have no idea why. Yet.\n\n---\nWAIT FOR PART 2. Hit plus so you don't miss it! @ClickBaitn't\n\n#Shorts #ClickBaitnt #StoryTime #Reddit #Funny #CollegeLife #Crush #Drama #Relatable #FYP #Viral #Trending #Part1 #Comedy #IndianCollege #CampusLife #MindBlown #WTF #GirlsDrama #Flirting #India", 
        "script_text": "This is the funniest thing that ever happened to me in college. Part one. So my best friend tells me she has a massive crush on this cute guy from another department. And because I apparently have friends in every department like some unofficial campus detective she gives me a mission. Find out everything about him. She drags me to a corridor where he's standing with his friends. She points him out. I look at him and I swear to god this man looked like Stuart Little to me. I don't see it but okay girl whatever makes you happy. But standing right next to Stuart Little is this girl. And she is giving me the most aggressive side eye I have ever experienced in my life. Like she has already murdered me a thousand times in her head. I tell my friend I'll gather the information and we leave. But this was just the beginning. Because over the next few days something insane started happening. Wait for Part two.", 
        "scenes": [
            {"scene_number": 1, "narration": "This is the funniest thing that ever happened to me in college. Part one. So my best friend tells me she has a massive crush on this cute guy from another department.", "visual_prompt": "colorful cartoon style illustration of two college girls whispering and giggling in Indian college corridor, fun vibrant anime inspired art style, warm campus atmosphere, cinematic 8k", "duration_estimate": 6}, 
            {"scene_number": 2, "narration": "And because I apparently have friends in every department like some unofficial campus detective she gives me a mission. Find out everything about him.", "visual_prompt": "funny cartoon illustration of girl wearing detective hat and magnifying glass in college campus, spy mission comedy concept, colorful playful art style, cinematic", "duration_estimate": 5}, 
            {"scene_number": 3, "narration": "She points him out. I look at him and I swear to god this man looked like Stuart Little to me. But standing right next to Stuart Little is this girl giving me the most aggressive side eye I have ever experienced.", "visual_prompt": "cartoon illustration of angry jealous girlfriend giving intense death stare side eye while standing next to her clueless boyfriend in college, comedy drama moment, vibrant art, cinematic", "duration_estimate": 8}, 
            {"scene_number": 4, "narration": "Like she has already murdered me a thousand times in her head. I tell my friend I'll gather the information and we leave. But this was just the beginning. Because over the next few days something insane started happening. Wait for Part two.", "visual_prompt": "dramatic cartoon cliffhanger scene with girl walking away while angry girl watches from background with fire in her eyes, comedy tension building, vibrant colors, cinematic", "duration_estimate": 6}
        ], 
        "tags": ["shorts", "story time", "reddit", "funny", "college", "crush", "drama", "relatable", "comedy", "indian college", "campus life", "flirting", "girls drama", "part 1", "clickbaitnt", "viral", "trending", "india", "fyp"]
    },
    {
        "part": 2, 
        "title": "I Accidentally Flirted My Way Out Of A Fight Part 2 #Shorts", 
        "description": "Part 2 of 3 — TEN of my friends have a crush on the SAME guy. Side-Eye Girl is getting angrier. And then she marches toward me in the cafeteria. I knew it was over.\n\n---\nPART 3 IS WHERE IT GETS CRAZY. Hit plus now! @ClickBaitn't\n\n#Shorts #ClickBaitnt #StoryTime #Reddit #Funny #CollegeLife #Crush #Drama #Relatable #FYP #Viral #Trending #Part2 #Comedy #IndianCollege #CampusLife #Confrontation #GirlFight #India", 
        "script_text": "Part two. Remember Stuart Little and Side Eye Girl. Over the next few days more than ten of my friends come to me saying they have a crush on this really cute guy. Every single time it's the same guy. Stuart Little. This man is collecting crushes like Pokemon cards. And every single time I go to check on him Side Eye Girl is standing right there giving me looks that could end my bloodline. Eventually I find out that Stuart Little and Side Eye Girl are actually dating. I inform all my friends. They grieve for half a day and then move on to new crushes because it's pathetic to want someone else's man. Story over right. Wrong. Yesterday I'm sitting alone in the cafeteria minding my own business when I see Side Eye Girl marching toward me like she's about to declare war. The rage in her eyes. The speed of her walk. She comes up to my table and slams her hand down. I knew right then. This girl is about to fight me. And what I did next was either the smartest or the dumbest thing I've ever done. Part three is coming.", 
        "scenes": [
            {"scene_number": 1, "narration": "Part two. Over the next few days more than ten of my friends come to me saying they have a crush on this really cute guy. Every single time it's the same guy. Stuart Little.", "visual_prompt": "funny cartoon montage of different girls all pointing at same confused looking boy with heart eyes, one guy ten crushes comedy, colorful vibrant art style, cinematic 8k", "duration_estimate": 7}, 
            {"scene_number": 2, "narration": "This man is collecting crushes like Pokemon cards. And every single time I go to check on him Side Eye Girl is standing right there giving me looks that could end my bloodline.", "visual_prompt": "cartoon angry girlfriend with literal fire in her eyes staring down another girl across college corridor, jealousy rage comedy, dramatic anime inspired art, cinematic", "duration_estimate": 6}, 
            {"scene_number": 3, "narration": "Eventually I find out they're dating. I inform all my friends. They grieve for half a day then move on. Story over right. Wrong.", "visual_prompt": "group of cartoon girls dramatically crying then immediately smiling and pointing at new boys, moving on speed comedy, funny exaggerated expressions, colorful art, cinematic", "duration_estimate": 5}, 
            {"scene_number": 4, "narration": "Yesterday I'm sitting alone in the cafeteria when Side Eye Girl marches toward me like she's about to declare war. She slams her hand on my table. This girl is about to fight me. And what I did next was either the smartest or the dumbest thing I've ever done. Part three is coming.", "visual_prompt": "dramatic cartoon scene of angry girl slamming hand on cafeteria table while other girl sits calmly with wide eyes, confrontation moment, dramatic anime style zoom in, cinematic cliffhanger", "duration_estimate": 7}
        ], 
        "tags": ["shorts", "story time", "reddit", "funny", "college", "crush", "drama", "confrontation", "comedy", "indian college", "campus life", "girl fight", "part 2", "clickbaitnt", "viral", "trending", "india", "fyp"]
    },
    {
        "part": 3, 
        "title": "I Accidentally Flirted My Way Out Of A Fight Part 3 FINALE #Shorts", 
        "description": "Part 3 of 3 — FINALE. She asked if I'm after her boyfriend. What I said next broke her brain completely. She was NOT ready for this.\n\n---\nDid NOT see that coming right? Follow @ClickBaitn't for more insane stories!\n\n#Shorts #ClickBaitnt #StoryTime #Reddit #Funny #CollegeLife #Crush #Drama #Relatable #FYP #Viral #Trending #Part3 #Finale #Comedy #IndianCollege #Flirting #PlotTwist #Unexpected #GirlsDrama #India", 
        "script_text": "Part three. The finale. Side Eye Girl is sitting across from me. Furious. Ready to end me. She says are you after my boyfriend. I say no. She says weren't you staring at him all these days. I say no. She says don't lie I've caught you looking at us multiple times. And this is where my brain chose chaos over peace. Instead of explaining the truth like a normal human being I looked her dead in the eyes and said. Yes I was looking at you guys. But I wasn't looking at him. She pauses. What do you mean. I said. I was looking at you babygirl. I got lost in your beauty. Silence. Complete system shutdown. This girl went from furious girlfriend to flustered mess in zero point two seconds. Out of every possible response she expected that was not on the list. She got shy. She didn't know what to say. The confrontation just dissolved. And that's how I accidentally flirted my way out of a potential campus war. Has something like this ever happened to you. Comment below I need to know.", 
        "scenes": [
            {"scene_number": 1, "narration": "Part three. The finale. Side Eye Girl is sitting across from me. Furious. She says are you after my boyfriend. I say no. She says weren't you staring at him. I say no. She says don't lie I caught you looking.", "visual_prompt": "intense cartoon confrontation across cafeteria table, angry girl interrogating calm girl, dramatic close up face off, anime style tension, vibrant colors, cinematic 8k", "duration_estimate": 8}, 
            {"scene_number": 2, "narration": "And this is where my brain chose chaos over peace. I looked her dead in the eyes and said. Yes I was looking at you guys. But I wasn't looking at him.", "visual_prompt": "dramatic cartoon moment of calm girl smirking with confident energy while other girl looks confused, the plot twist incoming, dramatic zoom in on smirk, anime comedy style, cinematic", "duration_estimate": 5}, 
            {"scene_number": 3, "narration": "She pauses. What do you mean. I said. I was looking at you babygirl. I got lost in your beauty. Silence. Complete system shutdown.", "visual_prompt": "cartoon girl completely frozen with error 404 brain shutdown visual effect, system crash comedy moment, the other girl smiling smugly, vibrant hilarious anime style, cinematic", "duration_estimate": 7}, 
            {"scene_number": 4, "narration": "This girl went from furious to flustered in zero point two seconds. The confrontation just dissolved. And that's how I accidentally flirted my way out of a campus war. Has something like this ever happened to you. Comment below I need to know.", "visual_prompt": "both cartoon girls now laughing together in cafeteria with hearts and comedy sparkles around them, enemies to confused friends, happy resolution, warm colorful vibrant art, cinematic", "duration_estimate": 5}
        ], 
        "tags": ["shorts", "story time", "reddit", "funny", "college", "crush", "drama", "flirting", "plot twist", "unexpected", "comedy", "indian college", "campus life", "finale", "part 3", "clickbaitnt", "viral", "trending", "india", "fyp", "babygirl"]
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

# ── pillow image overlay helper ───────────────────────────────────────────────

def burn_part_text_into_image(image_path: Path, part_number: int):
    """
    Opens the generated image, adds "PART X" to the top center,
    and saves it back to the same path.
    """
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    text = f"PART {part_number}"
    
    # Try to load a bold font, fallback if not available
    try:
        # Windows standard bold
        font = ImageFont.truetype("arialbd.ttf", 70)
    except IOError:
        try:
            # Mac/Linux standard bold
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        except IOError:
            # Absolute fallback (size might not be respected by default font)
            font = ImageFont.load_default()

    W_img, H_img = img.size
    y_pos = 120  # Distance from the top

    # Modern Pillow supports text anchoring and stroke directly
    try:
        x_pos = W_img / 2
        draw.text(
            (x_pos, y_pos), 
            text, 
            font=font, 
            fill="white", 
            stroke_width=5, 
            stroke_fill="black", 
            anchor="ma" # Middle-Ascender (centered horizontally, top aligned vertically)
        )
    except (TypeError, ValueError):
        # Fallback for older versions of Pillow
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
        except AttributeError:
            text_w, _ = draw.textsize(text, font=font)
            
        x_pos = (W_img - text_w) / 2
        
        # Manual stroke rendering by drawing black text slightly offset in all directions
        stroke_width = 5
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x_pos + dx, y_pos + dy), text, font=font, fill="black")
        # Draw the main white text over the black stroke
        draw.text((x_pos, y_pos), text, font=font, fill="white")

    # Save it back (converting to RGB to save as JPG if necessary, or keep as PNG)
    final_img = img.convert("RGB")
    final_img.save(image_path)

# ── single-video pipeline ─────────────────────────────────────────────────────

def run_video(script: dict, video_id: str) -> str:
    """Run all 8 pipeline stages. Returns YouTube URL. Raises on failure."""
    part_number = script.get("part", 1)

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

    # Stage 4: Image generation & PIL Overlay
    _banner("Stage 4 / 8  —  Image Generation (with PIL Overlay)")
    from src.visuals.image_generator import ImageGenerator
    gen         = ImageGenerator()
    image_paths = []
    for scene in script["scenes"]:
        n       = scene["scene_number"]
        prompt  = scene["visual_prompt"]
        _running(f"Scene {n}: {prompt[:55]}...")
        t0      = time.monotonic()
        
        # Generate the base image
        path = gen.generate_scene_image(prompt, n, video_id)
        
        # Burn the "PART X" text into the image
        burn_part_text_into_image(path, part_number)
        
        elapsed = time.monotonic() - t0
        _ok(f"Scene {n} saved & overlay added", f"{path.name}  ({path.stat().st_size // 1024} KB, {elapsed:.1f}s)")
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
            trend_source = "reddit_story_3parts",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"batch_reddit_story_3parts.py — Part {part_number}"
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
    print("  AUTO-SHORTS-ENGINE — Reddit Story (3 Parts)")
    print(f"  Uploading {len(SCRIPTS)} videos as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_redditpt{idx}"

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
            print(f"    Part {r['num']:>2}: {r['url']}")

    print()
    print("=" * W)

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())