"""
batch_viral_11.py — 11 Trend-Optimized Shorts, zero Gemini calls.

Same pipeline as previous batches:
  TTS -> Audio -> Whisper -> Images -> Video -> Upload -> Tracker

Run:
  python batch_viral_11.py
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

# ── 11 hardcoded scripts ──────────────────────────────────────────────────────

SCRIPTS = [

    # VIDEO 1 — Tech Myth (Incognito Mode)
    {
        "topic":    "Incognito Mode Myth",
        "category": "tech",
        "title":    "Incognito Mode Does Not Hide Your Search History #Shorts",
        "description": (
            "If you use private browsing to hide what you look at online, you are "
            "being completely lied to by your browser.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #TechMyths #CyberSecurity #Privacy #Hacker "
            "#Technology #Smartphones #DidYouKnow #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "If you use Incognito Mode to hide your search history, you are being lied to. "
            "Millions of people open private browsing tabs thinking it makes them completely "
            "invisible on the internet. It absolutely does not. Incognito mode only stops "
            "your local device from saving the history to your browser. Your Wi-Fi provider, "
            "your cellular network, your boss at work, and your school can still see the "
            "exact websites you are visiting in real time. Even worse, the websites you visit "
            "are still tracking your IP address and collecting your data. The only way to "
            "actually hide your digital footprint is by using a secure VPN. What is the "
            "weirdest thing currently in your search history? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "If you use Incognito Mode to hide your search history, you are being lied to. Millions of people open private browsing tabs thinking it makes them completely invisible.",
                "visual_prompt": "glowing incognito mode spy icon on a computer screen shattering like glass, revealing glowing red eyes behind it, cybersecurity myth concept, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "It absolutely does not. Incognito mode only stops your local device from saving the history to your browser. Your Wi-Fi provider, your boss, and your school...",
                "visual_prompt": "shadowy figures of a boss and a hacker standing behind a person typing on a laptop, watching a glowing stream of their data, creepy tech reality",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "...can still see the exact websites you are visiting in real time. Even worse, the websites you visit are still tracking your IP address and collecting your data.",
                "visual_prompt": "abstract visualization of a glowing IP address tag sticking to a person's back as they walk through a digital neon grid, tracking concept, cinematic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "The only way to actually hide your digital footprint is by using a secure VPN. What is the weirdest thing currently in your search history? Comment below.",
                "visual_prompt": "person sweating nervously while looking at their phone screen, funny awkward internet moment, dramatic lighting, highly detailed",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#TechMyths", "#IncognitoMode", "#Privacy", "#CyberSecurity", "#Technology"
        ],
        "tags": [
            "shorts", "incognito mode", "tech myths", "cyber security", "privacy", 
            "vpn", "hacker", "internet history", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 2 — Ocean/Space Anomaly (Point Nemo)
    {
        "topic":    "Point Nemo - The Spacecraft Graveyard",
        "category": "science",
        "title":    "The Loneliest Place On Planet Earth #Shorts",
        "description": (
            "There is a place in the ocean where the closest human beings to you are "
            "literally floating in outer space.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #PointNemo #Ocean #Space #Astronomy #DeepSea "
            "#CreepyFacts #Science #Viral #Trending #FYP #Geography"
        ),
        "script_text": (
            "There is a place on Earth where the closest humans to you are literally in outer space. "
            "It is called Point Nemo, the oceanic pole of inaccessibility. Located in the absolute "
            "middle of the Pacific Ocean, it is so incredibly far from any landmass that if you "
            "were floating there in a boat, the nearest humans wouldn't be on Earth. They would "
            "be the astronauts on the International Space Station, orbiting two hundred and fifty "
            "miles above your head. Because it is so dead and isolated, global space agencies "
            "use Point Nemo as a massive underwater spacecraft graveyard. Hundreds of decommissioned "
            "satellites and space stations have been crashed into this exact spot. Would you spend "
            "a night at Point Nemo for a million dollars? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a place on Earth where the closest humans to you are literally in outer space. It is called Point Nemo, the oceanic pole of inaccessibility.",
                "visual_prompt": "tiny lonely boat floating in a massive dark empty ocean, extremely isolating atmosphere, thalassophobia concept, cinematic moody lighting, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Located in the absolute middle of the Pacific Ocean, it is so incredibly far from any landmass that the nearest humans wouldn't be on Earth.",
                "visual_prompt": "camera looking straight up from the dark ocean water into the starry night sky, seeing the glowing International Space Station zooming past, breathtaking contrast",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "They would be the astronauts on the International Space Station. Because it is so isolated, global space agencies use Point Nemo as a massive underwater spacecraft graveyard.",
                "visual_prompt": "flaming satellite crashing down from space into the dark ocean waves, epic sci-fi realism, dramatic cinematic lighting, highly detailed",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Hundreds of decommissioned satellites and space stations have been crashed into this exact spot. Would you spend a night at Point Nemo for a million dollars? Comment below.",
                "visual_prompt": "creepy underwater shot of massive rusted spaceships and satellites resting on the dark ocean floor, deep sea mystery, eerie 8k photography",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#PointNemo", "#Ocean", "#Space", "#DeepSea", "#Astronomy"
        ],
        "tags": [
            "shorts", "point nemo", "ocean", "space station", "graveyard", "geography",
            "creepy facts", "science", "thalassophobia", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 3 — Biology/Horror (Rabies)
    {
        "topic":    "The Rabies Virus",
        "category": "science",
        "title":    "The Virus That Makes You Terrified Of Water #Shorts",
        "description": (
            "Rabies is the most terrifying disease on Earth. Once you show a single symptom, "
            "your survival rate drops to absolute zero.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Biology #Rabies #MedicalFacts #Science #Scary "
            "#HumanBody #Virus #MindBlown #Viral #Trending #FYP"
        ),
        "script_text": (
            "There is a virus that literally rewrites your brain to make you terrified of drinking water. "
            "Rabies is the most terrifying disease on planet Earth. If you get bitten by an infected "
            "animal, the virus slowly crawls up your nervous system into your brain. But here is the "
            "scary part. It can hide in your body for months with absolutely no signs. The moment "
            "you finally show your first symptom, like a headache or fever, it is too late. Your "
            "survival rate drops to zero percent. To help it spread, the virus causes violent, "
            "agonizing throat spasms whenever you try to swallow water, forcing the infectious "
            "saliva to build up in your mouth. What disease terrifies you the most? Comment below "
            "and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a virus that literally rewrites your brain to make you terrified of drinking water. Rabies is the most terrifying disease on planet Earth.",
                "visual_prompt": "person staring in absolute terror at a simple glass of pure water, psychological horror concept, dark cinematic medical lighting, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "If you get bitten by an infected animal, the virus slowly crawls up your nervous system into your brain. But here is the scary part.",
                "visual_prompt": "abstract medical visualization of a glowing toxic red virus slowly creeping up the blue electrical nerves of a human spine into the brain, deadly infection",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "It can hide for months. But the moment you finally show your first symptom, it is too late. Your survival rate drops to zero percent.",
                "visual_prompt": "glowing digital heart monitor flatlining, turning from bright green to blood red, terrifying medical reality, dramatic shadows",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "To help it spread, the virus causes agonizing throat spasms whenever you try to swallow water. What disease terrifies you the most? Comment below.",
                "visual_prompt": "sick person holding their throat in extreme pain while a glass of water spills on the floor, scary biological facts, intense cinematic lighting",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#Rabies", "#Biology", "#MedicalFacts", "#ScaryFacts", "#Virus"
        ],
        "tags": [
            "shorts", "rabies", "virus", "biology", "human body", "scary facts",
            "science", "disease", "hydrophobia", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 4 — Current Trend/Future Tech (Artificial Wombs)
    {
        "topic":    "EctoLife / Artificial Wombs",
        "category": "tech",
        "title":    "Babies Will Soon Be Grown In Giant Plastic Pods #Shorts",
        "description": (
            "Scientists are actively developing Artificial Womb facilities to grow "
            "thousands of humans in labs to combat global population collapse.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #FutureTech #ArtificialWomb #Science #Matrix "
            "#Technology #News #MindBlown #Viral #Trending #FYP #Dystopian"
        ),
        "script_text": (
            "In the next ten years, human babies will be grown in giant plastic pods. "
            "Welcome to the era of Artificial Wombs. Because global birth rates are "
            "collapsing, scientists are actively developing massive incubation facilities "
            "to grow humans outside of the human body. Concept projects like EctoLife "
            "have designed facilities capable of growing thirty thousand babies a year "
            "in transparent, liquid-filled pods. Parents would track their baby's growth, "
            "heart rate, and oxygen levels through an app on their smartphone. You could "
            "even play music directly into the pod. While it could save millions of lives "
            "and eliminate pregnancy complications, critics call it a dystopian nightmare "
            "straight out of The Matrix. Would you want your child to be grown in a science "
            "lab? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "In the next ten years, human babies will be grown in giant plastic pods. Welcome to the era of Artificial Wombs.",
                "visual_prompt": "massive futuristic laboratory filled with glowing pink liquid pods containing growing babies, sci-fi dystopian matrix aesthetic, highly detailed 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Because global birth rates are collapsing, scientists are actively developing massive incubation facilities to grow humans outside of the human body.",
                "visual_prompt": "scientist in a white lab coat monitoring a glowing high-tech incubation pod, cyberpunk medical technology, cinematic dramatic lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "Parents would track their baby's growth, heart rate, and oxygen levels through an app on their smartphone. You could even play music directly into the pod.",
                "visual_prompt": "person holding a smartphone displaying a glowing 3D ultrasound of a baby, controlling a massive physical pod behind them via bluetooth, futuristic app",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "While it could eliminate pregnancy complications, critics call it a nightmare straight out of The Matrix. Would you want your child to be grown in a science lab? Comment below.",
                "visual_prompt": "creepy matrix-style power plant but for humans, endless rows of glowing pods fading into the dark distance, terrifying sci-fi reality, 8k",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#ArtificialWomb", "#FutureTech", "#Science", "#Matrix", "#Dystopian"
        ],
        "tags": [
            "shorts", "artificial womb", "ectolife", "future tech", "science", "matrix",
            "dystopian", "babies", "population", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 5 — Psychology Paradox (Jamais Vu)
    {
        "topic":    "Jamais Vu (Opposite of Deja Vu)",
        "category": "psychology",
        "title":    "The Glitch Where Your Brain Forgets Everything #Shorts",
        "description": (
            "Have you ever stared at a normal word so long it completely lost its meaning? "
            "This is a psychological glitch called Jamais Vu.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Psychology #JamaisVu #BrainFacts #MentalHealth "
            "#Science #Neuroscience #Glitch #Viral #Trending #FYP #DeepThoughts"
        ),
        "script_text": (
            "Have you ever stared at a perfectly normal word until it suddenly looked "
            "spelled wrong and lost all of its meaning? This is the opposite of Deja Vu. "
            "It is a psychological glitch called Jamais Vu. Deja Vu is when a completely "
            "new situation feels oddly familiar. But Jamais Vu is when something you know "
            "perfectly well suddenly feels entirely alien. You might walk into your own "
            "bedroom and feel like you have never been there before. Or look at your "
            "best friend's face and feel like you are looking at a stranger. It happens "
            "when your brain gets neurologically fatigued and temporarily disconnects your "
            "perception from your memory. What simple word always looks spelled wrong to you? "
            "Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Have you ever stared at a perfectly normal word until it suddenly looked spelled wrong and lost all of its meaning? This is the opposite of Deja Vu.",
                "visual_prompt": "extreme close up of an eye staring at a piece of paper, the words on the paper are floating off the page and turning into glowing abstract nonsense symbols, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "It is a psychological glitch called Jamais Vu. Deja Vu is when a new situation feels familiar. But Jamais Vu is when something you know perfectly well suddenly feels entirely alien.",
                "visual_prompt": "person standing in a completely normal modern bedroom, but everything around them is glitching and looks terrifyingly unfamiliar, psychological thriller lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "You might look at your best friend's face and feel like you are looking at a stranger. It happens when your brain gets neurologically fatigued...",
                "visual_prompt": "person looking at their friend, but the friend's face is completely blurred out like a faceless mannequin, creepy brain glitch concept, cinematic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "...and temporarily disconnects your perception from your memory. What simple word always looks spelled wrong to you? Comment below and follow ClickBaitnt.",
                "visual_prompt": "glowing blue neural pathways in a human brain suddenly snapping and disconnecting like broken wires, losing memory connection, 8k macro",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Psychology", "#JamaisVu", "#BrainFacts", "#Glitch", "#Neuroscience"
        ],
        "tags": [
            "shorts", "jamais vu", "deja vu", "psychology", "brain facts", "memory",
            "glitch", "neuroscience", "human mind", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 6 — Geopolitics/Secret Ops (The Ghost Army)
    {
        "topic":    "The Ghost Army of WW2",
        "category": "history",
        "title":    "The US Army Won A War Using Inflatable Balloons #Shorts",
        "description": (
            "During WW2, the US deployed a top-secret unit of actors and artists to "
            "trick the Nazis using inflatable tanks and massive speakers.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #History #WW2 #GhostArmy #SecretOps #Military "
            "#Geopolitics #DidYouKnow #MindBlown #Viral #Trending #FYP #USA"
        ),
        "script_text": (
            "The US military won a major World War Two battle using inflatable balloons. "
            "They were a top-secret unit called The Ghost Army. Instead of drafting soldiers "
            "and snipers, the government drafted over a thousand actors, artists, and audio "
            "engineers. Their mission was to completely terrify the Nazi army into retreating "
            "by faking a massive military presence. They built hundreds of life-sized, "
            "inflatable rubber tanks and airplanes and set them up in empty fields. They "
            "mounted massive 500-pound speakers to trucks, blasting the recorded sounds of "
            "marching troops and tank treads so loudly it could be heard fifteen miles away. "
            "The Germans were so intimidated by this massive fake army that they retreated "
            "without firing a single shot. What is the smartest military trick in history? "
            "Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "The US military won a major World War Two battle using inflatable balloons. They were a top-secret unit called The Ghost Army.",
                "visual_prompt": "vintage 1940s military field, soldiers holding up a life-sized green army tank that is completely hollow and made of rubber, historical deception, 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 2,
                "narration": "Instead of drafting soldiers, the government drafted actors, artists, and audio engineers. Their mission was to completely terrify the Nazi army into retreating.",
                "visual_prompt": "men in WW2 uniforms painting fake insignia on an inflatable rubber airplane, cinematic documentary style lighting, historical war secret",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "They built hundreds of inflatable rubber tanks. They mounted massive speakers to trucks, blasting recorded sounds of marching troops that could be heard fifteen miles away.",
                "visual_prompt": "massive vintage loudspeakers mounted on the back of a military jeep in a foggy forest, blasting sound waves, epic historical warfare concept",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "The Germans were so intimidated by this massive fake army that they retreated without firing a single shot. What is the smartest military trick in history? Comment below.",
                "visual_prompt": "Nazi generals looking through binoculars from a dark trench, looking terrified at what they think is a massive army, dramatic cinematic shadows, 8k",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#History", "#GhostArmy", "#WW2", "#SecretOps", "#Military"
        ],
        "tags": [
            "shorts", "ww2", "ghost army", "history", "secret ops", "military strategy",
            "usa", "inflatable tanks", "deception", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 7 — Everyday Body Myth (Phantom Vibration Syndrome)
    {
        "topic":    "Phantom Vibration Syndrome",
        "category": "psychology",
        "title":    "You Are Hallucinating Your Phone Vibrating #Shorts",
        "description": (
            "Over 80% of people feel their phone vibrate in their pocket when it didn't. "
            "Your brain is rewiring itself to be addicted to notifications.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Psychology #Smartphones #BrainFacts #TechAddiction "
            "#MentalHealth #Science #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "You are actively hallucinating your phone vibrating in your pocket. Have you "
            "ever felt a distinct buzz on your leg, pulled out your phone, and realized "
            "you had zero notifications? You are suffering from Phantom Vibration Syndrome. "
            "Because we are so chronically addicted to our devices, our brains have completely "
            "re-wired our nervous system to be hyper-vigilant for alerts. Your brain is now "
            "so desperate for a hit of dopamine that it misinterprets the simple friction of "
            "your clothing rubbing against your leg, or the spasm of a muscle, as a text "
            "message vibration. Over eighty percent of smartphone users experience this glitch "
            "weekly. Our phones are literally altering human biology. How many times has your "
            "phone tricked you today? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "You are actively hallucinating your phone vibrating in your pocket. Have you ever felt a distinct buzz on your leg, pulled out your phone, and realized you had zero notifications?",
                "visual_prompt": "person pulling their smartphone out of their jeans pocket, looking incredibly confused at a blank dark screen, tech hallucination concept, 8k cinematic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "You are suffering from Phantom Vibration Syndrome. Because we are so chronically addicted to our devices, our brains have completely re-wired our nervous system to be hyper-vigilant.",
                "visual_prompt": "abstract x-ray view of a human leg where the nerves are glowing blue and violently vibrating like a phone, neuroscience tech addiction, highly detailed",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "Your brain is so desperate for dopamine that it misinterprets the simple friction of your clothing rubbing against your leg as a text message.",
                "visual_prompt": "glowing digital text message icon hovering near a person's pocket, but it shatters into pieces showing it was just an illusion, psychological glitch",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Over eighty percent of smartphone users experience this glitch. Our phones are literally altering human biology. How many times has your phone tricked you today? Comment below.",
                "visual_prompt": "zombie-like person staring blankly into the bright glowing light of their phone screen, representing global screen addiction, moody dramatic lighting",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Psychology", "#Smartphones", "#TechAddiction", "#BrainFacts", "#Science"
        ],
        "tags": [
            "shorts", "phantom vibration", "smartphones", "psychology", "brain facts",
            "tech addiction", "dopamine", "mental health", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 8 — Space/Tech Disaster (Kessler Syndrome)
    {
        "topic":    "Kessler Syndrome - Space Junk",
        "category": "space",
        "title":    "We Might Be Permanently Trapped On Earth #Shorts",
        "description": (
            "Millions of pieces of space junk are orbiting Earth at 17,000 MPH. One bad "
            "crash could trigger Kessler Syndrome, trapping humanity forever.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Space #Astronomy #TechNews #KesslerSyndrome "
            "#Science #NASA #SpaceX #MindBlown #Viral #Trending #FYP"
        ),
        "script_text": (
            "Humanity might soon be permanently trapped on Earth, and it is entirely our "
            "own fault. It is called Kessler Syndrome. Since the space race began, we have "
            "launched thousands of rockets, leaving over one hundred million pieces of metal "
            "space junk orbiting our planet. These metal fragments are flying around Earth "
            "at seventeen thousand miles per hour. At that speed, a piece of metal the size "
            "of a tiny screw hits with the explosive force of a hand grenade. Scientists are "
            "terrified that if two large dead satellites crash, they will explode into a million "
            "shrapnel bullets. This would trigger an unstoppable chain reaction, destroying every "
            "satellite we have. We would lose the internet, GPS, and be blocked from ever launching "
            "a rocket again. Do you think we will ever leave our solar system? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Humanity might soon be permanently trapped on Earth, and it is entirely our own fault. It is called Kessler Syndrome.",
                "visual_prompt": "massive glowing blue Earth seen from space, but it is completely surrounded by a dense, terrifying cage of rusted metal space junk and satellite debris, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "We have left over one hundred million pieces of metal space junk orbiting our planet. These metal fragments are flying around Earth at seventeen thousand miles per hour.",
                "visual_prompt": "extreme slow motion shot of a tiny jagged metal screw flying through space incredibly fast, glowing red hot with kinetic energy, deadly space debris",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "At that speed, a screw hits with the explosive force of a hand grenade. Scientists are terrified that if two satellites crash, they will trigger an unstoppable chain reaction...",
                "visual_prompt": "massive fiery explosion in outer space as two satellites violently collide, sending millions of deadly shrapnel pieces flying toward the camera, cinematic disaster",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "...destroying every satellite we have. We would lose the internet, GPS, and be blocked from ever launching a rocket again. Do you think we will ever leave our solar system? Comment below.",
                "visual_prompt": "a futuristic rocket ship trying to launch from Earth but crashing into a thick shield of space junk, trapping it inside the atmosphere, dystopian sci-fi",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#KesslerSyndrome", "#Space", "#Astronomy", "#Science", "#TechNews"
        ],
        "tags": [
            "shorts", "kessler syndrome", "space junk", "nasa", "spacex", "space",
            "astronomy", "science", "end of the world", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 9 — Ancient History (The Silphium Plant Extinction)
    {
        "topic":    "The Silphium Plant - Roman Extinction",
        "category": "history",
        "title":    "The Romans Loved This Plant So Much They Destroyed It #Shorts",
        "description": (
            "Ancient Romans loved the Silphium plant so much they literally ate it "
            "into extinction. It was worth more than solid gold.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #History #AncientRome #Botany #Facts #Mystery "
            "#DidYouKnow #FoodHistory #Viral #Trending #FYP #Education"
        ),
        "script_text": (
            "The ancient Romans loved a plant so much they literally ate it into extinction. "
            "It was called Silphium. Thousands of years ago, this mysterious yellow flower "
            "only grew in one specific coastal strip of North Africa. It was the ultimate "
            "miracle plant. The Romans used it as a delicious food seasoning, a luxury "
            "perfume, a medical cure-all, and most famously, as an incredibly effective "
            "ancient form of birth control. It was in such high demand that Julius Caesar "
            "stored it in the imperial treasury alongside solid gold. Its seeds were perfectly "
            "heart-shaped, which is why historians believe we use that shape to represent love "
            "today. Because they refused to farm it properly, they harvested every last stalk "
            "on Earth. What modern food would you eat to extinction? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "The ancient Romans loved a plant so much they literally ate it into extinction. It was called Silphium. Thousands of years ago, this mysterious yellow flower...",
                "visual_prompt": "beautiful cinematic painting of an ancient glowing yellow plant with thick stalks growing on a sunny Mediterranean cliffside, botanical historical art, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "...only grew in one specific strip of North Africa. The Romans used it as a delicious seasoning, a luxury perfume, and an incredibly effective ancient birth control.",
                "visual_prompt": "ancient Roman royalty sniffing a luxurious ornate glass perfume bottle glowing with golden liquid, opulent Roman banquet background, dramatic lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "It was in such high demand that Julius Caesar stored it in the imperial treasury alongside solid gold. Its seeds were perfectly heart-shaped...",
                "visual_prompt": "massive stone vault filled with glowing gold coins and piles of dried yellow plants, Julius Caesar looking over the wealth, epic historical scale",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "...which is why we use that shape for love today. Because they refused to farm it properly, they harvested every last stalk. What modern food would you eat to extinction? Comment below.",
                "visual_prompt": "close up of a perfect glowing heart-shaped seed resting in the palm of an ancient Roman hand, origin of the heart symbol concept, 8k macro photography",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#History", "#AncientRome", "#Botany", "#FoodHistory", "#Mystery"
        ],
        "tags": [
            "shorts", "history", "ancient rome", "silphium", "extinct", "plants",
            "botany", "julius caesar", "heart shape", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 10 — Psychology/Trend (The Tetris Effect)
    {
        "topic":    "The Tetris Effect - Brain Rewiring",
        "category": "psychology",
        "title":    "Video Games Are Literally Rewriting Your Brain #Shorts",
        "description": (
            "Playing repetitive games like Tetris or Minecraft physically alters your "
            "brain's neural pathways, invading your thoughts and dreams.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Psychology #Gaming #TetrisEffect #BrainFacts "
            "#Neuroscience #MentalHealth #Science #Viral #Trending #FYP"
        ),
        "script_text": (
            "Playing video games can literally rewrite your brain's hard drive. It is a "
            "psychological phenomenon known as the Tetris Effect. If you have ever played "
            "Minecraft, Candy Crush, or Tetris for way too many hours, you know exactly "
            "what this is. When you dedicate extreme focus to a repetitive visual task, "
            "your brain physically alters its neural pathways to become hyper-efficient at "
            "that game. The scary part? It bleeds into reality. You start looking at "
            "buildings on the street and imagining how the bricks fit together. You close "
            "your eyes to sleep, and you literally see glowing digital blocks falling "
            "behind your eyelids. Your brain is running the software in the background "
            "against your will. What video game has infected your dreams? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Playing video games can literally rewrite your brain's hard drive. It is a psychological phenomenon known as the Tetris Effect.",
                "visual_prompt": "human brain made entirely of glowing colorful neon tetris blocks locking into place, cyberpunk psychology visualization, 8k cinematic lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "If you have ever played Minecraft, Candy Crush, or Tetris for way too many hours, you know exactly what this is. When you dedicate extreme focus...",
                "visual_prompt": "person staring intensely at a glowing computer screen in a dark room, the reflection of the game code shining in their eyes, gaming addiction",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "...your brain physically alters its neural pathways. The scary part? It bleeds into reality. You start looking at buildings and imagining how the bricks fit together.",
                "visual_prompt": "POV shot walking down a normal city street, but the skyscrapers are glitching and turning into floating video game blocks, augmented reality hallucination",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "You close your eyes, and you literally see glowing digital blocks falling behind your eyelids. Your brain is running the software against your will. What video game has infected your dreams? Comment below.",
                "visual_prompt": "person trying to sleep in bed, but glowing neon puzzle blocks are cascading down the dark wall behind them, tetris effect dream, moody lighting",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#Psychology", "#Gaming", "#TetrisEffect", "#BrainFacts", "#Neuroscience"
        ],
        "tags": [
            "shorts", "tetris effect", "gaming", "psychology", "brain facts", "minecraft",
            "neuroscience", "dreams", "addiction", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 11 — Earth/Mystery (The Door to Hell)
    {
        "topic":    "Darvaza Gas Crater - The Door to Hell",
        "category": "earth",
        "title":    "The Giant Hole On Earth That Has Been Burning For 50 Years #Shorts",
        "description": (
            "In 1971, scientists accidentally lit a massive underground gas crater on fire. "
            "They thought it would burn out in a week. It never stopped.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Earth #Mystery #Geology #Nature #Science "
            "#History #ScaryFacts #DidYouKnow #Viral #Trending #FYP"
        ),
        "script_text": (
            "There is a massive hole in the Earth that has been violently burning on fire "
            "for over fifty years. Welcome to the Door to Hell. Located in the deserts of "
            "Turkmenistan, this crater wasn't made by a volcano. It was a massive human "
            "mistake. In 1971, Soviet engineers were drilling for oil when the ground "
            "suddenly collapsed, swallowing their massive rig and opening a sinkhole two "
            "hundred and thirty feet wide. Toxic methane gas started pouring out into the "
            "atmosphere. To stop the deadly gas from spreading to nearby towns, the scientists "
            "decided to just throw a match in and burn it off. They calculated the fire would "
            "last three days. It has been fifty-five years, and the raging inferno has never "
            "stopped. Would you roast marshmallows over the Door to Hell? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a massive hole in the Earth that has been violently burning on fire for over fifty years. Welcome to the Door to Hell.",
                "visual_prompt": "massive terrifying crater in the middle of a dark desert night, glowing with violent orange and red flames pouring out of the earth, epic drone shot, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Located in Turkmenistan, this crater wasn't made by a volcano. It was a massive human mistake. In 1971, Soviet engineers were drilling for oil...",
                "visual_prompt": "vintage 1970s soviet industrial oil drilling rig violently collapsing and sinking into a massive dusty sinkhole, historical disaster concept, cinematic action",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "...when the ground collapsed, opening a sinkhole two hundred feet wide. Toxic methane gas started pouring out. To stop it, scientists decided to just throw a match in.",
                "visual_prompt": "silhouette of a scientist in a hazmat suit throwing a single burning flare into a massive dark abyss, igniting a massive wave of fire, dramatic lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "They calculated the fire would last three days. It has been fifty-five years, and the inferno has never stopped. Would you roast marshmallows over the Door to Hell? Comment below.",
                "visual_prompt": "person standing way too close to the edge of a massive flaming lava pit holding a tiny marshmallow on a stick, funny dark humor concept, epic scale 8k",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#EarthMystery", "#Geology", "#ScienceFacts", "#History", "#DoorToHell"
        ],
        "tags": [
            "shorts", "door to hell", "darvaza gas crater", "geology", "earth facts",
            "mystery", "science", "ussr", "fire", "clickbaitnt", "viral", "trending"
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
            trend_source = "batch_viral_11",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"batch_viral_11.py — {script['topic']}"
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
    print("  AUTO-SHORTS-ENGINE — Trend Optimized Batch (11 Shorts)")
    print(f"  Uploading {len(SCRIPTS)} videos as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_viral{idx}"

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