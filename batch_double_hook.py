# batch_double_hook.py
# Structure: Double-hook format for maximum retention
# Week: [FILL IN WEEK]
# Run: python batch_double_hook.py

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
# DOUBLE-HOOK SCRIPT TEMPLATE
# ------------------------------------------------------------
# STRUCTURE PER SHORT:
#   topic        : internal label (not shown to viewer)
#   title        : YouTube title — must contain the curiosity gap
#   description  : YouTube description + hashtags
#   script_text  : Full narration broken into 3 beats:
#                  HOOK 1 (0-2s)  — shocking statement
#                  HOOK 2 (2-5s)  — raise the stakes / twist
#                  BODY   (5-40s) — deliver the proof
#                  CTA    (last 3s) — "Hit that plus sign + tease next video"
#   scenes       : 4 scenes, one per visual beat
#                  scene 1 → HOOK visual
#                  scene 2 → TWIST visual
#                  scene 3 → PROOF visual
#                  scene 4 → PAYOFF + CTA visual
#   tags         : 12-15 tags, mix of topic + niche + viral
# ============================================================

SCRIPTS = [

    # ── SHORT 1 ─────────────────────────────────────────────
    {
        "topic": "Liver Regeneration",
        "title": "Your Liver Can Regrow Itself — But Only Once",
        "description": (
            "Your liver is the only organ that can fully regenerate itself. "
            "But there's a catch nobody tells you about. "
            "#ClickBaitnt #BrainFacts #BodyFacts #ScienceFacts #DidYouKnow "
            "#HumanBody #Biology #Shorts #Viral #MindBlown"
        ),
        "script_text": (
            # HOOK 1 — shocking statement (0-2s)
            "Your liver can completely regrow itself after being cut in half. "
            # HOOK 2 — raise the stakes (2-5s)
            "But here's what doctors don't tell you — it only works once, "
            "and most people have already used up that chance without knowing it. "
            # BODY — deliver the proof (5-38s)
            "The human liver is the only internal organ capable of full regeneration. "
            "Remove 70 percent of it, and within 8 weeks it grows back to full size. "
            "This is why liver donation is possible between living people. "
            "But every time you damage it — alcohol, junk food, medication overuse — "
            "it regenerates with scar tissue instead of healthy cells. "
            "Enough scars and the regeneration stops permanently. "
            "That condition is called cirrhosis, and it's irreversible. "
            # CTA (last 3s)
            "Hit that plus sign — tomorrow we reveal the one drink "
            "that repairs liver cells while you sleep."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Your liver can completely regrow itself after being cut in half.",
                "visual_prompt": "glowing human liver split in half regenerating, medical illustration, dramatic dark background",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "But here's what doctors don't tell you — it only works once, and most people have already used up that chance without knowing it.",
                "visual_prompt": "doctor looking serious at xray scan, hospital lighting, tension atmosphere",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "Remove 70 percent of it and within 8 weeks it grows back to full size. But every time you damage it, it regenerates with scar tissue instead. Enough scars and regeneration stops permanently.",
                "visual_prompt": "split comparison of healthy glowing liver vs scarred damaged liver, clinical infographic style",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "That condition is called cirrhosis and it is irreversible. Hit that plus sign — tomorrow we reveal the one drink that repairs liver cells while you sleep.",
                "visual_prompt": "dramatic close up of a single glass of liquid glowing on a dark table, mysterious lighting",
                "duration_estimate": 8,
            },
        ],
        "tags": [
            "liver regeneration", "human body facts", "biology facts",
            "did you know", "body mysteries", "science facts",
            "health facts", "mind blown", "clickbaitnt",
            "shorts", "viral", "amazing facts"
        ],
        "category": "education",
    },

    # ── SHORT 2 ─────────────────────────────────────────────
    {
        "topic": "Void of Bootes",
        "title": "There Is A Hole In Space So Big It Should Not Exist",
        "description": (
            "The Boötes Void is 330 million light years wide and almost completely empty. "
            "Scientists still cannot explain it. "
            "#ClickBaitnt #Space #Universe #SpaceFacts #Cosmos "
            "#ScienceFacts #MindBlown #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            # HOOK 1
            "There is a hole in space so large that our entire galaxy "
            "would be invisible inside it. "
            # HOOK 2
            "And the terrifying part — it is completely, perfectly empty. "
            "No stars. No galaxies. No dark matter. Just nothing. "
            # BODY
            "It is called the Boötes Void, and it stretches 330 million light years across. "
            "In that entire region, astronomers have found only 60 galaxies. "
            "A normal region that size should contain over 10,000. "
            "When it was first discovered in 1981, scientists assumed it was a mistake. "
            "They rechecked the data three times. "
            "It was not a mistake. "
            "The universe is 13.8 billion years old. "
            "Physicists calculated that a void this size cannot form naturally "
            "in that amount of time. "
            "It should not exist. "
            # CTA
            "Hit that plus sign — because the theory scientists whisper about "
            "in private is deeply unsettling."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a hole in space so large that our entire galaxy would be invisible inside it.",
                "visual_prompt": "massive black void in space surrounded by glowing galaxies, cosmic scale, cinematic",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "And the terrifying part — it is completely, perfectly empty. No stars. No galaxies. No dark matter. Just nothing.",
                "visual_prompt": "deep black empty space with zero stars, eerie silence visual, slight blue edge glow",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "It stretches 330 million light years across. A normal region that size should contain over 10,000 galaxies. They found only 60. Scientists rechecked the data three times. It was not a mistake.",
                "visual_prompt": "astronomer looking shocked at data screen, universe map showing giant empty patch, dramatic lighting",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "The universe is 13.8 billion years old. This void cannot form naturally in that time. It should not exist. Hit that plus sign — because the theory scientists whisper about is deeply unsettling.",
                "visual_prompt": "scientists gathered around a table in dark room, universe projection showing the void, tense atmosphere",
                "duration_estimate": 10,
            },
        ],
        "tags": [
            "bootes void", "space facts", "universe mysteries", "space horror",
            "astronomy", "cosmos", "science facts", "mind blown",
            "clickbaitnt", "shorts", "viral", "space shorts"
        ],
        "category": "education",
    },

    # ── SHORT 3 ─────────────────────────────────────────────
    {
        "topic": "Nocebo Effect",
        "title": "Doctors Can Make You Sick Just By Telling You Something",
        "description": (
            "The Nocebo Effect is the opposite of placebo — and it kills people. "
            "Your brain is more dangerous than any disease. "
            "#ClickBaitnt #Psychology #BrainFacts #MindOverMatter #Nocebo "
            "#ScienceFacts #MindBlown #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            # HOOK 1
            "A doctor can make you physically sick just by telling you "
            "that you are going to get sick. "
            # HOOK 2
            "This is not a theory. People have died from it. "
            "And it happens in hospitals every single day. "
            # BODY
            "You already know about the placebo effect — "
            "believing you are being healed can actually heal you. "
            "The nocebo effect is the exact opposite. "
            "Believing you will get worse makes you get worse. "
            "In one study, patients told their chemotherapy would cause hair loss "
            "lost hair — even when given a sugar pill with zero chemicals. "
            "Their brain generated the physical symptom from belief alone. "
            "Doctors have recorded cases where patients told they had "
            "three months to live died in exactly three months — "
            "with no medical reason for the timing. "
            "Your brain does not know the difference between a real threat "
            "and one you were told about. "
            # CTA
            "Hit that plus sign — tomorrow we show you how to use this in reverse "
            "to actually make yourself heal faster."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "A doctor can make you physically sick just by telling you that you are going to get sick.",
                "visual_prompt": "doctor speaking seriously to patient, hospital room, dramatic shadow lighting",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "This is not a theory. People have died from it. And it happens in hospitals every single day.",
                "visual_prompt": "hospital corridor at night, ominous lighting, empty beds, psychological tension",
                "duration_estimate": 6,
            },
            {
                "scene_number": 3,
                "narration": "In one study, patients told their chemotherapy would cause hair loss — lost hair — even when given a sugar pill. Their brain generated the physical symptom from belief alone.",
                "visual_prompt": "glowing brain sending signals to body, medical scan aesthetic, blue and white tones",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "Your brain does not know the difference between a real threat and one you were told about. Hit that plus sign — tomorrow we show you how to use this in reverse to heal faster.",
                "visual_prompt": "person meditating with glowing healing energy surrounding body, hopeful warm lighting",
                "duration_estimate": 10,
            },
        ],
        "tags": [
            "nocebo effect", "placebo", "psychology", "brain power",
            "mind over matter", "medical facts", "brain facts",
            "mind blown", "clickbaitnt", "shorts", "viral", "science facts"
        ],
        "category": "education",
    },

    # ── SHORT 4 ─────────────────────────────────────────────
    {
        "topic": "Roman Concrete",
        "title": "Ancient Romans Made Concrete That Gets Stronger Every Year",
        "description": (
            "Roman concrete has survived 2,000 years underwater and is still getting stronger. "
            "Modern concrete crumbles in 50. Here is why. "
            "#ClickBaitnt #AncientHistory #RomanEmpire #ScienceFacts #AncientTech "
            "#History #MindBlown #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            # HOOK 1
            "Ancient Romans made concrete 2,000 years ago "
            "that is literally stronger today than the day it was built. "
            # HOOK 2
            "Modern concrete — the kind holding up your building right now — "
            "starts crumbling after 50 years. "
            "We have been building it wrong for two centuries. "
            # BODY
            "Roman concrete, called opus caementicium, was mixed with seawater "
            "and a volcanic ash called pozzolana. "
            "Scientists assumed the seawater would weaken it. "
            "It did the exact opposite. "
            "When seawater enters the concrete, it reacts with the ash "
            "and grows new crystals inside the structure — "
            "making it denser and stronger over time. "
            "Roman harbour walls built in 37 BC are still intact underwater today. "
            "When researchers analysed the formula and tried to replicate it, "
            "they couldn't perfectly reproduce it for 15 years. "
            # CTA
            "Hit that plus sign — tomorrow we reveal the Roman building "
            "that modern engineers say is physically impossible to construct today."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Ancient Romans made concrete 2,000 years ago that is literally stronger today than the day it was built.",
                "visual_prompt": "ancient Roman harbour wall underwater still perfectly intact, dramatic ocean lighting, cinematic",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "Modern concrete starts crumbling after 50 years. We have been building it wrong for two centuries.",
                "visual_prompt": "split screen of crumbling modern concrete vs pristine ancient Roman structure, dramatic comparison",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "Roman concrete was mixed with seawater and volcanic ash. The seawater grows new crystals inside the structure making it denser and stronger over time.",
                "visual_prompt": "microscopic view of crystals growing inside ancient concrete, scientific visualization, glowing blue",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "Roman harbour walls built in 37 BC are still intact underwater today. Hit that plus sign — tomorrow we reveal the Roman building that modern engineers say is physically impossible to construct today.",
                "visual_prompt": "ancient Roman colosseum at sunset, grand scale, mysterious atmosphere, warm golden tones",
                "duration_estimate": 9,
            },
        ],
        "tags": [
            "roman concrete", "ancient rome", "ancient technology", "history facts",
            "ancient mysteries", "science facts", "mind blown", "ancient tech",
            "clickbaitnt", "shorts", "viral", "did you know"
        ],
        "category": "education",
    },

    # ── SHORT 5 ─────────────────────────────────────────────
    {
        "topic": "Cold Water Shock",
        "title": "Jumping Into Cold Water Can Stop Your Heart In 60 Seconds",
        "description": (
            "Cold water shock kills more swimmers than drowning does. "
            "And it happens in the first 60 seconds before you even start to struggle. "
            "#ClickBaitnt #BodyFacts #ScienceFacts #Swimming #ColdWater "
            "#HumanBody #MindBlown #Shorts #Viral #DidYouKnow"
        ),
        "script_text": (
            # HOOK 1
            "If you jump into cold water, your heart can stop "
            "before you even have time to panic. "
            # HOOK 2
            "Most people who drown in cold water never drown. "
            "They die in the first 60 seconds from something else entirely — "
            "and almost nobody knows this. "
            # BODY
            "When your body hits cold water below 15 degrees Celsius, "
            "it triggers a reflex called cold water shock. "
            "Your blood vessels slam shut simultaneously. "
            "Your heart rate spikes to over 180 beats per minute. "
            "You involuntarily gasp and inhale water. "
            "All of this happens in under 3 seconds. "
            "In healthy adults with no heart conditions, "
            "this reflex alone can cause cardiac arrest. "
            "This is why people are found floating face down "
            "in shallow water with no signs of struggle. "
            "They were dead before they could fight. "
            "The survival window is exactly 60 seconds — "
            "if you can control your breathing in that window, "
            "your chances of survival increase by 85 percent. "
            # CTA
            "Hit that plus sign — tomorrow we show the exact breathing technique "
            "that keeps you alive in cold water."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "If you jump into cold water, your heart can stop before you even have time to panic.",
                "visual_prompt": "person jumping into dark cold water, dramatic slow motion, icy blue tones, tension",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "Most people who drown in cold water never actually drown. They die in the first 60 seconds from something else entirely.",
                "visual_prompt": "60 second countdown timer over dark icy water, urgent red tones, dramatic lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "Cold water shock slams your blood vessels shut, spikes your heart rate to 180 beats per minute, and makes you involuntarily gasp and inhale water — all in under 3 seconds.",
                "visual_prompt": "human body diagram showing cardiovascular system reacting, medical visualization, blue and red contrast",
                "duration_estimate": 14,
            },
            {
                "scene_number": 4,
                "narration": "This is why people are found floating face down in shallow water with no signs of struggle. Hit that plus sign — tomorrow we show the exact breathing technique that keeps you alive.",
                "visual_prompt": "calm person floating on back in icy water, controlled breathing, survival focus, cinematic blue tones",
                "duration_estimate": 10,
            },
        ],
        "tags": [
            "cold water shock", "swimming safety", "body facts", "survival facts",
            "human body", "science facts", "mind blown", "did you know",
            "clickbaitnt", "shorts", "viral", "health facts"
        ],
        "category": "education",
    },

]

# ============================================================
# PIPELINE — DO NOT CHANGE ANYTHING BELOW THIS LINE
# ============================================================

def main() -> None:
    get_config()["video"]["mode"] = "splitscreen"

    total = len(SCRIPTS)
    log.info("batch.start", total=total)

    for i, script in enumerate(SCRIPTS, 1):
        video_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
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
                trend_source = "manual_batch",
                trend_score  = 95.0,
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

    print("\n=== BATCH COMPLETE ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("batch.fatal", error=str(e), exc_info=True)
        sys.exit(1)