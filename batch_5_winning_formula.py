# batch_5_winning_formula.py
# 5 Shorts — The Winning Formula (creepy medical / historical / creatures / death)
# Hook in first 3s, no build-up, subscribe CTA targeting 500 subs
# Run: python batch_5_winning_formula.py

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

SCRIPTS = [

    # ── SHORT 1: Creepy Medical Anomaly ──────────────────────────
    {
        "topic": "Tanganyika Laughter Epidemic",
        "title": "1,000 People Couldn't Stop Laughing For 18 Months 😨😂",
        "description": (
            "The Tanganyika Laughter Epidemic of 1962 forced schools to close "
            "as an uncontrollable laughing sickness spread to over 1,000 people. "
            "It was not a joke. It was a mass psychogenic illness. "
            "#ClickBaitnt #MedicalMysteries #CreepyFacts #Psychology "
            "#TrueStory #MindBlown #Shorts #Viral #DidYouKnow #ScienceFacts"
        ),
        "script_text": (
            # HOOK 1 — shocking outcome, first 3 seconds, no build-up
            "In 1962, over a thousand people started laughing "
            "and physically could not stop for eighteen months. "
            # HOOK 2 — raise stakes
            "It was not happiness. "
            "They were crying, screaming, and collapsing from exhaustion — "
            "while still laughing. "
            "And it spread like a virus. "
            # BODY
            "It started with three schoolgirls in a village in Tanzania. "
            "One began laughing. Then the whole class. "
            "Within weeks, 95 students were affected "
            "and the school was forced to shut down. "
            "But closing the school made it worse. "
            "The students went home and infected their families and villages. "
            "It spread to 14 schools and over 1,000 people. "
            "Symptoms lasted anywhere from a few hours to 16 days per person, "
            "and the entire outbreak lasted a year and a half. "
            "Doctors found no virus, no toxin, no drug. "
            "It was a mass psychogenic illness — "
            "stress and fear physically spreading through a population "
            "like a contagious disease. "
            "Your brain can make your body do things "
            "you have absolutely no control over. "
            # SUBSCRIBE CTA
            "We are 50 subscribers away from 500. "
            "Subscribe and comment the word LAUGH "
            "if your brain just glitched."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "In 1962, over a thousand people started laughing and physically could not stop for eighteen months.",
                "visual_prompt": "unsettling vintage 1960s African schoolyard, children with disturbing frozen laughing expressions, eerie sepia horror aesthetic",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "It was not happiness. They were crying, screaming, and collapsing from exhaustion while still laughing. And it spread like a virus.",
                "visual_prompt": "disturbing close up of a face caught between laughing and crying, tears streaming, psychological horror, dark cinematic lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "It started with three schoolgirls. Within weeks 95 students were affected and the school shut down. It spread to 14 schools and over 1,000 people. Doctors found no virus, no toxin. It was mass psychogenic illness — fear spreading like a disease.",
                "visual_prompt": "map of Tanzania with glowing red infection spread lines radiating outward from a village, epidemic visualization, ominous",
                "duration_estimate": 15,
            },
            {
                "scene_number": 4,
                "narration": "Your brain can make your body do things you have absolutely no control over. We are 50 subscribers away from 500. Subscribe and comment LAUGH if your brain just glitched.",
                "visual_prompt": "glowing human brain with chaotic electrical signals overwhelming the body, loss of control visual, dramatic neon aesthetic",
                "duration_estimate": 9,
            },
        ],
        "tags": [
            "tanganyika laughter epidemic", "mass hysteria", "medical mysteries",
            "creepy facts", "psychology", "true story", "mind blown",
            "did you know", "clickbaitnt", "shorts", "viral", "science facts"
        ],
        "category": "education",
    },

    # ── SHORT 2: Historical Mystery / Creepy ─────────────────────
    {
        "topic": "Hinterkaifeck Murders",
        "title": "A Family Was Murdered By Someone Living In Their Attic 🏚️🔪",
        "description": (
            "The Hinterkaifeck murders of 1922 remain unsolved. "
            "For days before they died, the family heard footsteps in the attic. "
            "Someone was living above them. Then they were all killed. "
            "#ClickBaitnt #UnsolvedMysteries #TrueCrime #CreepyFacts "
            "#Hinterkaifeck #MindBlown #Shorts #Viral #DidYouKnow #Horror"
        ),
        "script_text": (
            # HOOK 1
            "For days before this entire family was murdered, "
            "they heard footsteps coming from inside their own attic. "
            # HOOK 2
            "They found newspapers nobody bought. "
            "Keys went missing. "
            "Fresh footprints led to the house but never away from it. "
            "Someone was living above them. "
            "And nobody believed them until it was too late. "
            # BODY
            "In 1922, on a remote farm called Hinterkaifeck in Germany, "
            "the farmer told neighbours he heard footsteps in the attic "
            "and found a strange newspaper he never purchased. "
            "He found an unfamiliar set of keys. "
            "He found fresh footprints in the snow "
            "leading toward the farm — but none leading away. "
            "Days later, all six people on the farm were found dead, "
            "killed one by one with a tool called a mattock. "
            "But here is the part that still terrifies investigators. "
            "After the murders, the killer stayed on the farm. "
            "Neighbours saw smoke from the chimney. "
            "The animals had been fed. "
            "Someone ate meals in that kitchen "
            "for days while six bodies lay in the barn. "
            "The case was never solved. "
            "Over 100 suspects were questioned. "
            "Nobody was ever charged. "
            # SUBSCRIBE CTA
            "We are 50 subscribers from 500. "
            "Subscribe and comment who you think did it."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "For days before this entire family was murdered, they heard footsteps coming from inside their own attic.",
                "visual_prompt": "dark eerie wooden attic with a single shaft of light, ominous footprints in dust, deeply unsettling horror atmosphere",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "They found newspapers nobody bought. Keys went missing. Fresh footprints led to the house but never away from it. Someone was living above them. Nobody believed them until it was too late.",
                "visual_prompt": "fresh footprints in snow leading toward a dark isolated farmhouse at dusk, no footprints leading away, chilling mystery aesthetic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "In 1922 on a remote German farm, six people were found dead, killed one by one. But the killer stayed. Neighbours saw chimney smoke. The animals were fed. Someone ate meals in that kitchen for days while six bodies lay in the barn.",
                "visual_prompt": "isolated snow covered German farmhouse at night with smoke rising from chimney and a single window glowing, deeply ominous",
                "duration_estimate": 15,
            },
            {
                "scene_number": 4,
                "narration": "The case was never solved. Over 100 suspects questioned. Nobody charged. We are 50 subscribers from 500. Subscribe and comment who you think did it.",
                "visual_prompt": "vintage 1922 unsolved case file with crime scene photos blurred out, mystery investigation aesthetic, dramatic shadows",
                "duration_estimate": 8,
            },
        ],
        "tags": [
            "hinterkaifeck", "unsolved mysteries", "true crime", "creepy history",
            "horror history", "cold case", "mind blown", "did you know",
            "clickbaitnt", "shorts", "viral", "mystery"
        ],
        "category": "education",
    },

    # ── SHORT 3: Strange Real Creature ───────────────────────────
    {
        "topic": "Immortal Jellyfish Turritopsis",
        "title": "This Animal Reverses Its Own Death To Become A Baby Again 🪼♾️",
        "description": (
            "The Immortal Jellyfish can reverse its own aging and become "
            "a baby again whenever it is dying. It is biologically immortal. "
            "Scientists are studying it to understand human aging. "
            "#ClickBaitnt #NatureFacts #BiologyFacts #OceanFacts "
            "#Immortal #MindBlown #Shorts #Viral #DidYouKnow #ScienceFacts"
        ),
        "script_text": (
            # HOOK 1
            "There is an animal in the ocean "
            "that cannot die of old age "
            "because it can literally reverse its own death. "
            # HOOK 2
            "When it gets old, injured, or starving, "
            "it does not die. "
            "It turns its entire body back into a baby "
            "and starts its life over again — "
            "and it can do this forever. "
            # BODY
            "It is called Turritopsis dohrnii, the Immortal Jellyfish, "
            "and it is the only known biologically immortal animal on Earth. "
            "Normal animals age in one direction. "
            "This jellyfish can age backwards. "
            "When it is dying, its cells transform "
            "in a process called transdifferentiation — "
            "where adult cells turn back into baby cells. "
            "Its entire body collapses into a blob, "
            "settles on the ocean floor, "
            "and regrows as a brand new young polyp. "
            "The same jellyfish can do this over and over, "
            "potentially living forever "
            "unless it is eaten or killed by disease. "
            "Scientists believe that unlocking how it does this "
            "could one day help us understand "
            "how to stop human aging entirely. "
            "It is the size of your fingernail "
            "and it has solved death. "
            # SUBSCRIBE CTA
            "We are 50 subscribers from 500. "
            "Subscribe and comment if you would want to live forever."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is an animal in the ocean that cannot die of old age because it can literally reverse its own death.",
                "visual_prompt": "ethereal glowing translucent jellyfish floating in dark deep ocean, otherworldly bioluminescent beauty, cinematic",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "When it gets old, injured, or starving, it does not die. It turns its entire body back into a baby and starts its life over again — forever.",
                "visual_prompt": "time reversal visual of a jellyfish transforming from old to young, glowing rewind effect, surreal biological magic",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "Its cells transform in a process called transdifferentiation where adult cells turn back into baby cells. Its body collapses into a blob, settles on the ocean floor, and regrows as a brand new young polyp. Over and over, forever.",
                "visual_prompt": "microscopic view of jellyfish cells glowing and reversing into younger cells, scientific transformation visualization, beautiful and eerie",
                "duration_estimate": 15,
            },
            {
                "scene_number": 4,
                "narration": "It is the size of your fingernail and it has solved death. We are 50 subscribers from 500. Subscribe and comment if you would want to live forever.",
                "visual_prompt": "tiny glowing immortal jellyfish next to a human fingertip for scale, glowing with eternal life energy, awe inspiring",
                "duration_estimate": 9,
            },
        ],
        "tags": [
            "immortal jellyfish", "turritopsis", "ocean facts", "nature facts",
            "biology facts", "immortality", "science facts", "mind blown",
            "did you know", "clickbaitnt", "shorts", "viral"
        ],
        "category": "education",
    },

    # ── SHORT 4: Disturbing Death Story ──────────────────────────
    {
        "topic": "Alexander Bogdanov Blood Transfusion",
        "title": "This Scientist Tried To Become Immortal With Blood And It Killed Him 🩸💀",
        "description": (
            "Alexander Bogdanov believed blood transfusions could make him immortal. "
            "He performed them on himself — until one transfusion killed him. "
            "#ClickBaitnt #TrueStory #ScienceHistory #CreepyFacts "
            "#MedicalHistory #MindBlown #Shorts #Viral #DidYouKnow #Dark"
        ),
        "script_text": (
            # HOOK 1
            "A scientist became convinced "
            "he could live forever by swapping his blood with younger people — "
            "so he tested it on himself eleven times. "
            # HOOK 2
            "The first ten times, he claimed it was working. "
            "He said his eyesight improved and his hair stopped falling out. "
            "The eleventh time killed him. "
            # BODY
            "His name was Alexander Bogdanov, "
            "a Russian physician and revolutionary in the 1920s. "
            "He became obsessed with the idea "
            "that blood held the secret to eternal youth. "
            "He founded the world's first institute "
            "dedicated entirely to blood transfusion. "
            "He began transfusing himself with the blood of younger people, "
            "convinced it was reversing his aging. "
            "After his eleventh transfusion, "
            "he took the blood of a student "
            "who unknowingly had both malaria and tuberculosis. "
            "Blood type matching was barely understood at the time. "
            "His body rejected the blood violently. "
            "He died slowly over the next two weeks "
            "in agonising pain. "
            "Strangely, the student whose blood he took "
            "made a full recovery. "
            "Bogdanov was searching for immortality "
            "and found the exact opposite. "
            # SUBSCRIBE CTA
            "We are 50 subscribers from 500. "
            "Subscribe — tomorrow's story is even darker."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "A scientist became convinced he could live forever by swapping his blood with younger people, so he tested it on himself eleven times.",
                "visual_prompt": "1920s scientist in a dim laboratory with blood transfusion equipment, ominous red glow, vintage medical horror aesthetic",
                "duration_estimate": 6,
            },
            {
                "scene_number": 2,
                "narration": "The first ten times he claimed it was working. His eyesight improved, his hair stopped falling out. The eleventh time killed him.",
                "visual_prompt": "vintage blood transfusion tubes glowing ominously, dramatic close up of blood flowing, dark clinical tension",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "He founded the world's first blood transfusion institute. On his eleventh transfusion he took the blood of a student with malaria and tuberculosis. Blood type matching was barely understood. His body rejected it violently and he died slowly over two weeks.",
                "visual_prompt": "1920s hospital bed with a dying figure, blood bags hanging, eerie sterile lighting, tragic medical scene",
                "duration_estimate": 15,
            },
            {
                "scene_number": 4,
                "narration": "Strangely, the student whose blood he took made a full recovery. Bogdanov was searching for immortality and found the exact opposite. We are 50 subscribers from 500. Subscribe — tomorrow's story is even darker.",
                "visual_prompt": "single empty vintage hospital bed with a blood bag still dripping, haunting irony, dark cinematic atmosphere",
                "duration_estimate": 9,
            },
        ],
        "tags": [
            "alexander bogdanov", "blood transfusion", "science history", "true story",
            "medical history", "creepy facts", "dark history", "mind blown",
            "did you know", "clickbaitnt", "shorts", "viral"
        ],
        "category": "education",
    },

    # ── SHORT 5: Medical Horror ──────────────────────────────────
    {
        "topic": "Fatal Familial Insomnia",
        "title": "This Disease Stops You From Sleeping Until You Die 🛏️💀",
        "description": (
            "Fatal Familial Insomnia is a genetic disease where you slowly "
            "lose the ability to sleep — and there is no cure. "
            "Patients stay awake for months until their body shuts down. "
            "#ClickBaitnt #MedicalMysteries #CreepyFacts #BodyHorror "
            "#TrueStory #MindBlown #Shorts #Viral #DidYouKnow #ScienceFacts"
        ),
        "script_text": (
            # HOOK 1
            "There is a disease that slowly stops you from sleeping — "
            "ever again — until it kills you. "
            # HOOK 2
            "There is no cure. No treatment. "
            "Sleeping pills do nothing. "
            "Once it begins, you will be awake "
            "for the last few months of your life. "
            # BODY
            "It is called Fatal Familial Insomnia, "
            "and it is one of the rarest and most terrifying diseases on Earth. "
            "It is genetic, passed down through families, "
            "caused by a single mutated protein in the brain "
            "called a prion. "
            "The disease attacks the thalamus — "
            "the part of your brain that controls sleep. "
            "It usually begins in your 40s or 50s. "
            "First, you struggle to fall asleep. "
            "Then you cannot sleep at all. "
            "Your body never gets to rest or repair. "
            "You begin to hallucinate, lose weight, "
            "and experience full dementia "
            "while remaining completely awake and aware. "
            "The average patient survives 18 months "
            "from the first symptom. "
            "The most disturbing part — "
            "the patient stays mentally conscious "
            "for almost the entire descent, "
            "fully aware of what is happening to them. "
            # SUBSCRIBE CTA
            "We are 50 subscribers from 500. "
            "Subscribe and comment if you will hug your bed tonight."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a disease that slowly stops you from sleeping ever again until it kills you.",
                "visual_prompt": "person lying in bed at night with wide open exhausted bloodshot eyes unable to sleep, dark room, psychological horror",
                "duration_estimate": 5,
            },
            {
                "scene_number": 2,
                "narration": "There is no cure. No treatment. Sleeping pills do nothing. Once it begins you will be awake for the last few months of your life.",
                "visual_prompt": "clock showing endless passing time over a sleepless figure in bed, surreal exhaustion visual, eerie blue darkness",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "It is genetic, caused by a mutated prion protein. It attacks the thalamus which controls sleep. First you cannot fall asleep, then you cannot sleep at all. You hallucinate, lose weight, and experience full dementia while completely awake and aware.",
                "visual_prompt": "glowing brain diagram with the thalamus region deteriorating and glowing red, medical horror visualization, clinical and disturbing",
                "duration_estimate": 16,
            },
            {
                "scene_number": 4,
                "narration": "The average patient survives 18 months. The most disturbing part — they stay fully conscious and aware of what is happening the entire time. We are 50 subscribers from 500. Subscribe and comment if you will hug your bed tonight.",
                "visual_prompt": "exhausted hollow eyed person staring into darkness fully aware and afraid, deeply human and tragic, cinematic horror lighting",
                "duration_estimate": 10,
            },
        ],
        "tags": [
            "fatal familial insomnia", "medical mysteries", "creepy facts",
            "body horror", "rare disease", "true story", "science facts",
            "mind blown", "did you know", "clickbaitnt", "shorts", "viral"
        ],
        "category": "education",
    },

]

# ============================================================
# PIPELINE — DO NOT CHANGE ANYTHING BELOW THIS LINE
# ============================================================

def main() -> None:
    start_time = time.time()
    get_config()["video"]["mode"] = "splitscreen"

    total = len(SCRIPTS)
    log.info("batch.start", total=total)

    for i, script in enumerate(SCRIPTS, 1):
        video_id = f"vid_winform_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
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
            record = VideoRecord.from_script(
                script       = script,
                video_id     = video_id,
                trend_source = "winning_formula",
                trend_score  = 99.9,
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

    end_time   = time.time()
    total_secs = end_time - start_time
    hours      = int(total_secs // 3600)
    minutes    = int((total_secs % 3600) // 60)
    seconds    = int(total_secs % 60)

    print("\n==================================================")
    print(f"=== BATCH COMPLETE — {hours}h {minutes}m {seconds}s ===")
    print("==================================================\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("batch.fatal", error=str(e), exc_info=True)
        sys.exit(1)