"""
batch_kunafa_trend.py
---------------------
One-shot render + upload for the Kunafa trend video.
Uses the actual auto-shorts-engine pipeline API directly.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import log
from src.utils.config_loader import get_config
from src.voice.tts_engine import TTSEngine
from src.voice.audio_processor import AudioProcessor
from src.subtitles.whisper_align import WhisperAligner
from src.visuals.image_generator import ImageGenerator
from src.video.video_composer import VideoComposer
from src.video.video_validator import VideoValidator
from src.upload.metadata_builder import MetadataBuilder
from src.upload.youtube_uploader import YouTubeUploader
from src.tracker.excel_tracker import ExcelTracker
from src.tracker.models import VideoRecord

# ---------------------------------------------------------------------------
# Script definition
# ---------------------------------------------------------------------------

SCRIPT = {
    "topic": "Why India Is Obsessed With This Middle Eastern Dessert",
    "title": "Why India Is Obsessed With This Middle Eastern Dessert",
    "description": (
        "Kunafa went from a Middle Eastern street stall to every Indian city in under "
        "12 months. Here's the science behind why your brain can't resist it. "
        "#ClickBaitnt #Kunafa #FoodTrends #IndianFood #ViralFood "
        "#Dessert #FoodScience #Shorts #Viral #Trending"
    ),
    "script_text": (
        "This dessert didn't exist in India three years ago. "
        "Now there's a queue for it in every city. "
        "Kunafa — a Middle Eastern sweet made of shredded wheat, molten cheese, "
        "and sugar syrup — has a scientifically perfect combination. "
        "Your brain gets hit with fat, sugar, and salt simultaneously. "
        "That triple signal is the same reason you can't stop eating chips. "
        "But Kunafa adds one more weapon — the cheese pull. "
        "Your brain is wired to find stretchy textures deeply satisfying. "
        "It's the same reflex that made pizza go global. "
        "Indians didn't just adopt Kunafa — they mutated it. "
        "Kunafa cheesecake. Kunafa stuffed croissants. Kunafa inside gulab jamun. "
        "Hit that plus sign — because the next Indian food taking over the world "
        "is something you eat every single day."
    ),
    "scenes": [
        {
            "scene_number": 1,
            "narration": (
                "This dessert didn't exist in India three years ago. "
                "Now there's a queue for it in every city."
            ),
            "visual_prompt": "long queue of people outside a dessert shop at night, golden lights, urban India street",
            "duration_estimate": 6,
        },
        {
            "scene_number": 2,
            "narration": (
                "Kunafa — a Middle Eastern sweet made of shredded wheat, molten cheese, "
                "and sugar syrup — has a scientifically perfect combination. "
                "Your brain gets hit with fat, sugar, and salt simultaneously."
            ),
            "visual_prompt": "close up of golden kunafa with melting cheese pull, warm lighting, food photography style",
            "duration_estimate": 10,
        },
        {
            "scene_number": 3,
            "narration": (
                "That triple signal is the same reason you can't stop eating chips. "
                "But Kunafa adds one more weapon — the cheese pull. "
                "Your brain is wired to find stretchy textures deeply satisfying. "
                "It's the same reflex that made pizza go global."
            ),
            "visual_prompt": "brain diagram lighting up with pleasure signals, food reward system, vibrant colors",
            "duration_estimate": 12,
        },
        {
            "scene_number": 4,
            "narration": (
                "Indians didn't just adopt Kunafa — they mutated it. "
                "Kunafa cheesecake. Kunafa stuffed croissants. Kunafa inside gulab jamun. "
                "Hit that plus sign — because the next Indian food taking over the world "
                "is something you eat every single day."
            ),
            "visual_prompt": "fusion Indian kunafa desserts spread on table, colorful plating, mouth watering close up",
            "duration_estimate": 12,
        },
    ],
    "tags": [
        "kunafa", "food trends india", "viral food", "indian dessert",
        "food science", "why kunafa is trending", "street food india",
        "clickbaitnt", "shorts", "viral", "trending food 2026",
    ],
    "category": "food",
}

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    # Enable split-screen brain rot mode
    get_config()["video"]["mode"] = "splitscreen"

    video_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log.info("batch_kunafa.start", video_id=video_id, title=SCRIPT["title"])

    # [1/7] Voice generation
    log.info("batch_kunafa.stage", step="1/7", name="voice_generation")
    raw_audio = TTSEngine().generate(SCRIPT["script_text"], video_id)

    # [2/7] Audio processing (normalise, silence trim, music mix)
    log.info("batch_kunafa.stage", step="2/7", name="audio_processing")
    audio_path = AudioProcessor().process(raw_audio, video_id)

    # [3/7] Whisper word-level alignment for subtitles
    log.info("batch_kunafa.stage", step="3/7", name="whisper_alignment")
    word_segments = WhisperAligner().align(audio_path)

    # [4/7] Image generation (one per scene)
    log.info("batch_kunafa.stage", step="4/7", name="image_generation", scenes=len(SCRIPT["scenes"]))
    image_paths = ImageGenerator().generate_all(SCRIPT["scenes"], video_id)

    # [5/7] Video assembly (motion + overlays + subtitles + audio)
    log.info("batch_kunafa.stage", step="5/7", name="video_assembly")
    video_path = VideoComposer().compose(
        scenes        = SCRIPT["scenes"],
        image_paths   = image_paths,
        audio_path    = audio_path,
        word_segments = word_segments,
        video_id      = video_id,
    )

    # Validate before upload
    result = VideoValidator().validate(video_path)
    if not result.valid:
        raise RuntimeError(f"Video validation failed: {result}")
    log.info("batch_kunafa.video_valid", path=str(video_path))

    # [6/7] YouTube upload
    log.info("batch_kunafa.stage", step="6/7", name="youtube_upload")
    metadata    = MetadataBuilder().build(SCRIPT, video_id)
    youtube_url = YouTubeUploader().upload(video_path, metadata, video_id)
    log.info("batch_kunafa.uploaded", url=youtube_url)

    # [7/7] Tracker
    log.info("batch_kunafa.stage", step="7/7", name="tracker_update")
    record            = VideoRecord.from_script(
        script       = SCRIPT,
        video_id     = video_id,
        trend_source = "manual",
        trend_score  = 100.0,
    )
    record.video_file  = str(video_path)
    record.youtube_url = youtube_url
    record.update_status("uploaded")
    ExcelTracker().append(record)

    log.info(
        "batch_kunafa.done",
        video_id    = video_id,
        youtube_url = youtube_url,
        video_path  = str(video_path),
    )
    print(f"\n=== DONE ===")
    print(f"YouTube URL : {youtube_url}")
    print(f"Video file  : {video_path}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.error("batch_kunafa.failed", error=str(exc), exc_info=True)
        sys.exit(1)
