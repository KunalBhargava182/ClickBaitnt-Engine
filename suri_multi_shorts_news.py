# batch_5_crazy_random.py
# Structure: Double-hook format for maximum retention
# Count: 5 Brand New Shorts (Zero Repeats, Highly Bizarre Viral Topics)
# Feature: CRAZY VISUAL PROMPTS to force surreal, comment-bait images.
# Feature: Tracks and outputs total upload time at the end.
# Run: python batch_5_crazy_random.py

import sys
import os
from datetime import datetime
import time

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

# ============================================================
# DOUBLE-HOOK SCRIPT TEMPLATE (5 SHORTS)
# ============================================================

SCRIPTS = [

    # ── SHORT 1: Extreme Survival / Ocean Terror ────────────────
    {
        "topic": "Harrison Okene Deep Sea Survival",
        "title": "He Survived 3 Days Trapped At The Bottom Of The Ocean 🚢🌊",
        "description": (
            "Harrison Okene survived inside a sunken ship for 60 hours in absolute pitch-black, freezing water. "
            "#ClickBaitnt #SurvivalFacts #OceanMysteries #DeepSea "
            "#CreepyFacts #ScienceFacts #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            "Imagine being trapped inside a sunken ship at the pitch-black bottom of the ocean for three entire days, listening to sharks eat your crewmates. "
            "This isn't a movie. It is the unbelievable true story of Harrison Okene. "
            "In 2013, a tugboat capsized and sank 100 feet to the freezing ocean floor off the coast of Nigeria. "
            "Harrison, the ship's cook, managed to find a tiny, four-foot pocket of trapped air inside a bathroom. "
            "For 60 agonizing hours, he sat in freezing water in absolute, terrifying darkness, slowly running out of oxygen. "
            "When deep-sea salvage divers finally arrived to recover dead bodies, they swam into the ship and saw a pale human hand reach out and grab them. "
            "The divers practically had a heart attack. "
            "Harrison had miraculously survived off a single can of Coke and a mathematically impossible air pocket. "
            "Hit that plus sign — tomorrow we look at the terrifying death spiral of army ants."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Imagine being trapped inside a sunken ship at the pitch-black bottom of the ocean for three entire days, listening to sharks eat your crewmates.",
                "visual_prompt": "claustrophobic deep sea nightmare, a terrified man floating in freezing dark water inside a rusted steel cabin, surrounded by pitch black abyss",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "This isn't a movie. It is the unbelievable true story of Harrison Okene.",
                "visual_prompt": "a massive steel ship violently sinking upside down into a terrifying, glowing blue ocean trench",
                "duration_estimate": 5,
            },
            {
                "scene_number": 3,
                "narration": "He found a 4-foot air pocket. For 60 hours he sat in freezing darkness. When salvage divers came for bodies, a pale hand reached out and grabbed them. They practically had a heart attack.",
                "visual_prompt": "a glowing diver's flashlight cutting through murky water, illuminating a ghostly, pale human hand reaching out from the shadows",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "Harrison survived on a single can of Coke. Hit that plus sign — tomorrow we look at the terrifying death spiral of army ants.",
                "visual_prompt": "millions of glowing red ants marching in a massive, hypnotic, swirling vortex of death on the jungle floor",
                "duration_estimate": 8,
            },
        ],
        "tags": ["harrison okene", "ocean mysteries", "deep sea", "survival stories", "scary facts", "weird history", "did you know", "clickbaitnt", "shorts", "viral", "mind blown"],
        "category": "science",
    },

    # ── SHORT 2: Biology / Nature Glitch ────────────────────────
    {
        "topic": "The Ant Mill (Death Spiral)",
        "title": "Millions Of Ants Will March In A Circle Until They Die 🐜🌀",
        "description": (
            "The Ant Death Spiral is a terrifying biological glitch where army ants get trapped in an infinite loop. "
            "#ClickBaitnt #BiologyFacts #NatureFacts #Insects "
            "#CreepyNature #ScienceFacts #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            "Millions of army ants will suddenly form a perfect, massive swirling vortex of death, marching in a circle until every single one of them dies of exhaustion. "
            "It looks like a dark demonic ritual, but it is actually a terrifying biological glitch. "
            "Scientists call it the Ant Mill, or the Death Spiral. "
            "Army ants are completely blind. To navigate the jungle, they rely entirely on smelling the pheromone chemical trails left by the ant walking directly in front of them. "
            "But if the lead foraging ant gets confused and accidentally loops back onto its own trail, a catastrophic error occurs. "
            "The ants start following each other in a closed circle. "
            "Because they blindly follow the scent, the circle gets larger and faster, trapping millions of ants in a hypnotic, infinite loop. "
            "They will literally march themselves to death. "
            "Hit that plus sign — tomorrow we investigate the man who flew into an airport from a country that does not exist."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Millions of army ants will suddenly form a perfect, massive swirling vortex of death, marching in a circle until every single one of them dies of exhaustion.",
                "visual_prompt": "hyper-detailed macabre shot of millions of dark ants locked in a massive, spinning, hypnotic spiral of death, glowing with a faint toxic red aura",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "It looks like a dark demonic ritual, but it is actually a terrifying biological glitch. Scientists call it the Ant Mill.",
                "visual_prompt": "glowing digital DNA glitching over a horde of blind ants, showing neon blue chemical scent trails forming an endless circle",
                "duration_estimate": 6,
            },
            {
                "scene_number": 3,
                "narration": "Army ants are blind and follow pheromone trails. If the leader accidentally loops back, a catastrophic error occurs. They follow the scent in an infinite loop.",
                "visual_prompt": "extreme close up of a blind ant's antennae glowing as it sniffs a bright neon purple chemical trail that loops back onto itself",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "They march themselves to death. Hit that plus sign — tomorrow we investigate the man who flew into an airport from a country that does not exist.",
                "visual_prompt": "a 1950s businessman in a suit handing a glowing, heavily stamped passport to a confused airport guard, noir mystery aesthetic",
                "duration_estimate": 7,
            },
        ],
        "tags": ["ant death spiral", "ant mill", "biology facts", "nature facts", "creepy nature", "insects", "science facts", "clickbaitnt", "shorts", "viral", "did you know"],
        "category": "science",
    },

    # ── SHORT 3: Matrix Glitch / Unsolved Mystery ───────────────
    {
        "topic": "The Man from Taured",
        "title": "The Man From A Country That Doesn't Exist 🛂🌌",
        "description": (
            "In 1954, a man landed at a Tokyo airport claiming to be from Taured, a country that has never existed. "
            "#ClickBaitnt #MatrixGlitch #UnsolvedMysteries #ParallelUniverse "
            "#WeirdHistory #CreepyFacts #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            "In 1954, a businessman landed at a Tokyo airport, handed the guards his passport, and sparked the greatest parallel universe mystery in human history. "
            "When Japanese customs officers looked at his official passport, they were completely baffled. "
            "The passport was authentic, covered in real international stamps, but it was issued by a country called 'Taured'. "
            "The problem? The country of Taured does not exist on Planet Earth. "
            "When officers brought out a world map, the man confidently pointed to the tiny European nation of Andorra. "
            "He became furious, claiming his country had existed for 1,000 years and he had never heard of Andorra. "
            "The police locked him in a high-security hotel room with armed guards at the only door. "
            "When they opened the door the next morning, the man—and all of his luggage—had completely vanished into thin air. "
            "Hit that plus sign — tomorrow we explore the terrifying village where people randomly fall asleep for days."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "In 1954, a businessman landed at a Tokyo airport, handed the guards his passport, and sparked the greatest parallel universe mystery in human history.",
                "visual_prompt": "vintage 1950s airport customs desk, a mysterious man in a trench coat hands over a passport glowing with a strange, otherworldly neon green aura",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "The passport was authentic, covered in real stamps, but it was issued by a country called 'Taured'. The country of Taured does not exist.",
                "visual_prompt": "macro shot of an official, leather-bound passport stamped with the bold gold letters 'TAURED', looking completely authentic but absurd",
                "duration_estimate": 5,
            },
            {
                "scene_number": 3,
                "narration": "He pointed to Andorra on a map and became furious, claiming his country existed for 1,000 years. Police locked him in a high-security hotel room. By morning, he had completely vanished into thin air.",
                "visual_prompt": "a heavily guarded hotel door opening to reveal a completely empty room, the man's silhouette glitching away like a digital matrix error",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "Hit that plus sign — tomorrow we explore the terrifying village where people randomly fall asleep for days.",
                "visual_prompt": "a deserted, foggy village street where dozens of people are inexplicably collapsed and sleeping on the concrete, eerie surrealism",
                "duration_estimate": 8,
            },
        ],
        "tags": ["man from taured", "parallel universe", "matrix glitch", "unsolved mysteries", "creepy history", "weird history", "conspiracy", "clickbaitnt", "shorts", "viral", "did you know"],
        "category": "education",
    },

    # ── SHORT 4: Medical Mystery / Earth Anomaly ────────────────
    {
        "topic": "Kalachi Sleep Epidemic",
        "title": "The Village Where People Randomly Fall Asleep For Days 💤☣️",
        "description": (
            "The Kalachi sleep epidemic caused a quarter of the town to collapse into comas. "
            "#ClickBaitnt #MedicalMysteries #EarthMysteries #ScienceFacts "
            "#WeirdHistory #CreepyFacts #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            "There is a village where people randomly collapse in the middle of the street and fall into a deep, unshakeable sleep for six days straight. "
            "When they finally wake up, they suffer from terrifying hallucinations and intense memory loss. "
            "This is the bizarre medical mystery of the Kalachi Sleep Epidemic. "
            "Starting in 2013, over a quarter of the residents in this small Kazakhstan village were struck by the illness. "
            "Children fell asleep at their school desks, and adults passed out while riding motorcycles. "
            "Doctors tested for viruses, contaminated water, and mass hysteria, but found absolutely nothing wrong with them. "
            "After years of panic, geologists finally uncovered the silent killer. "
            "An abandoned Soviet-era uranium mine near the town was secretly leaking massive, invisible clouds of carbon monoxide. "
            "The gas was silently starving the villagers' brains of oxygen, forcing them into a literal toxic coma. "
            "Hit that plus sign — tomorrow we expose the terrifying Amazonian monster that attacks you when you pee."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a village where people randomly collapse in the middle of the street and fall into a deep, unshakeable sleep for six days straight.",
                "visual_prompt": "a dark, eerie Eastern European village street, a person slumping forward and collapsing into a deep sleep on the pavement, cinematic fog",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "When they finally wake up, they suffer from terrifying hallucinations and intense memory loss. This is the Kalachi Sleep Epidemic.",
                "visual_prompt": "a person waking up with wide, terrified eyes, their vision warped with neon purple hallucinogenic colors and swirling shadows",
                "duration_estimate": 6,
            },
            {
                "scene_number": 3,
                "narration": "Children fell asleep at desks. Doctors found nothing. Finally, geologists found an abandoned Soviet uranium mine leaking massive, invisible clouds of carbon monoxide, forcing toxic comas.",
                "visual_prompt": "a dark, rusted mine shaft emitting a terrifying, glowing yellow invisible gas that slowly creeps over the sleeping town like a blanket",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "Hit that plus sign — tomorrow we expose the terrifying Amazonian monster that attacks you when you pee.",
                "visual_prompt": "a terrifying, translucent, needle-like fish glowing under dark green river water, biological nightmare aesthetic",
                "duration_estimate": 7,
            },
        ],
        "tags": ["kalachi sleep epidemic", "medical mysteries", "science facts", "earth mysteries", "creepy facts", "soviet secrets", "weird history", "clickbaitnt", "shorts", "viral"],
        "category": "science",
    },

    # ── SHORT 5: Extreme Biology / Nightmare Fuel ───────────────
    {
        "topic": "Candiru Fish",
        "title": "Do NOT Pee In The Amazon River 🐟🚽",
        "description": (
            "The Candiru is a terrifying parasitic fish that allegedly swims up human urine streams to embed itself inside you. "
            "#ClickBaitnt #BiologyFacts #AmazonRiver #CreepyNature "
            "#ScienceFacts #MedicalMysteries #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            "If you ever go swimming in the Amazon River, whatever you do, absolutely do not pee in the water. "
            "Because there is a tiny, translucent monster that will literally swim up the stream of urine and embed itself inside your body. "
            "Meet the Candiru, the Vampire Fish of the Amazon. "
            "It is a tiny, parasitic catfish that is nearly invisible in the muddy water. "
            "Normally, it hunts by swimming into the gills of larger fish to drink their blood. "
            "To find its prey, it tracks the scent of urea and ammonia that fish expel from their gills. "
            "But human urine contains the exact same chemicals. "
            "If a human pees in the river, the Candiru mistakes the scent for a fish gill. It aggressively swims straight up the urine stream, entering the human body. "
            "Once inside, it deploys razor-sharp backwards-facing spines like an umbrella, making it physically impossible to pull out without surgery. "
            "Hit that plus sign — and stay curious."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "If you ever go swimming in the Amazon River, whatever you do, absolutely do not pee in the water.",
                "visual_prompt": "dark, muddy Amazon river water viewed from below, a highly ominous and terrifying underwater atmosphere, danger aesthetic",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "Because there is a tiny, translucent monster that will literally swim up the stream of urine and embed itself inside your body.",
                "visual_prompt": "a creepy, glowing translucent worm-like fish with terrifying tiny fangs swimming rapidly through dark green water",
                "duration_estimate": 6,
            },
            {
                "scene_number": 3,
                "narration": "This is the Candiru. It tracks ammonia to find fish gills. Human urine has the same scent. It swims up the stream, enters the body, and deploys backward-facing spines like an umbrella.",
                "visual_prompt": "biological xray diagram showing a horrifying tiny fish deploying sharp, glowing red jagged spikes to lock itself permanently in place",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "It requires surgery to remove. Hit that plus sign — and stay curious.",
                "visual_prompt": "the ClickBaitn't channel logo glowing brilliantly on a dark screen with an animated neon plus sign pulsing like a heartbeat",
                "duration_estimate": 7,
            },
        ],
        "tags": ["candiru fish", "vampire fish", "amazon river", "creepy nature", "biology facts", "medical horror", "dangerous animals", "clickbaitnt", "shorts", "viral", "did you know"],
        "category": "science",
    },

]

# ============================================================
# PIPELINE — DO NOT CHANGE ANYTHING BELOW THIS LINE
# ============================================================

def main() -> None:
    # Track the exact start time to calculate total batch duration
    start_time = time.time()
    
    get_config()["video"]["mode"] = "splitscreen"

    total = len(SCRIPTS)
    log.info("batch.start", total=total)

    for i, script in enumerate(SCRIPTS, 1):
        video_id = f"vid_5batch_crazy_random_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
        log.info("batch.processing", index=i, total=total, title=script["title"])

        try:
            log.info("stage", step="1/7", name="voice")
            raw_audio = TTSEngine().generate(script["script_text"], video_id)

            log.info("stage", step="2/7", name="audio")
            audio_path = AudioProcessor().process(raw_audio, video_id)

            log.info("stage", step="3/7", name="whisper")
            word_segments = WhisperAligner().align(audio_path)

            log.info("stage", step="4/7", name="images")
            image_paths = ImageGenerator().generate_all(script["scenes"], video_id)

            log.info("stage", step="5/7", name="video")
            video_path = VideoComposer().compose(
                scenes        = script["scenes"],
                image_paths   = image_paths,
                audio_path    = audio_path,
                word_segments = word_segments,
                video_id      = video_id,
            )

            result = VideoValidator().validate(video_path)
            if not result.valid:
                raise RuntimeError(f"Validation failed: {result}")

            log.info("stage", step="6/7", name="upload")
            metadata    = MetadataBuilder().build(script, video_id)
            youtube_url = YouTubeUploader().upload(video_path, metadata, video_id)

            log.info("stage", step="7/7", name="tracker")
            record            = VideoRecord.from_script(
                script       = script,
                video_id     = video_id,
                trend_source = "clickbaitnt_viral_logic",
                trend_score  = 99.8,
            )
            record.video_file  = str(video_path)
            record.youtube_url = youtube_url
            record.update_status("uploaded")
            ExcelTracker().append(record)

            print(f"\n✅ {i}/{total} DONE")
            print(f"   Title : {script['title']}")
            print(f"   URL   : {youtube_url}\n")

            time.sleep(5)

        except Exception as e:
            log.error("batch.failed", index=i, error=str(e), exc_info=True)
            print(f"\n❌ {i}/{total} FAILED — moving to next\n")
            continue

    # --------------------------------------------------------
    # FINAL TIMING OUTPUT
    # --------------------------------------------------------
    end_time = time.time()
    total_seconds = end_time - start_time
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    print("\n==================================================")
    print("=== BATCH COMPLETE ===")
    print(f"Total time taken to generate and upload {total} shorts:")
    if hours > 0:
        print(f"{hours} hours, {minutes} minutes, and {seconds} seconds.")
    else:
        print(f"{minutes} minutes and {seconds} seconds.")
    print("==================================================\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("batch.fatal", error=str(e), exc_info=True)
        sys.exit(1)