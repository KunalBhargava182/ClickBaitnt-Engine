"""
batch_trending_10.py — 10 Current World Trend Shorts, zero Gemini calls.

Same pipeline as previous batches:
  TTS -> Audio -> Whisper -> Images -> Video -> Upload -> Tracker

Run:
  python batch_trending_10.py
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

# ── 10 hardcoded scripts ──────────────────────────────────────────────────────

SCRIPTS = [

    # VIDEO 1 — AI Deepfake Voice Scams (Cybersecurity Trend)
    {
        "topic":    "AI Voice Cloning Scams",
        "category": "tech news",
        "title":    "Do Not Trust Your Own Mother's Voice On The Phone #Shorts",
        "description": (
            "The scariest trend of 2026 is AI voice cloning. Scammers only need 3 seconds "
            "of your voice to perfectly clone it and call your family.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Deepfake #ScamAlert #CyberSecurity #TechNews "
            "#ArtificialIntelligence #Creepy #FutureTech #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "You can no longer trust the voice of your own mother on the phone. "
            "The scariest technological trend right now is AI voice cloning, and it is "
            "causing absolute chaos. Scammers now only need three seconds of audio from "
            "a TikTok or Instagram reel to perfectly map your voice. They then use AI to "
            "call your parents, sounding exactly like you, crying and saying you've been "
            "kidnapped or arrested and need money immediately. The AI even copies your "
            "breathing patterns and stuttering. Millions of dollars are being stolen "
            "every week because the human brain cannot tell the difference between the AI "
            "and the real person. Experts say every family needs a secret safe-word right "
            "now. What would your family's secret safe-word be? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "You can no longer trust the voice of your own mother on the phone. The scariest technological trend right now is AI voice cloning, and it is causing absolute chaos.",
                "visual_prompt": "person holding a glowing smartphone looking terrified, a digital waveform of a voice coming out of the speaker turning into a sinister digital skull, cyber security concept, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Scammers now only need three seconds of audio from a TikTok or Instagram reel to perfectly map your voice. They then use AI to call your parents...",
                "visual_prompt": "hacker in a dark room using a glowing high-tech audio software interface, isolating a 3-second audio clip from a social media video, cinematic thriller lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "...sounding exactly like you, crying and saying you've been kidnapped or arrested and need money immediately. The AI even copies your breathing patterns.",
                "visual_prompt": "split screen of an AI robot speaking into a microphone on one side, and a panicked parent holding a phone on the other side, deepfake concept art",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "Millions of dollars are being stolen every week. Experts say every family needs a secret safe-word right now. What would your family's secret safe-word be? Comment below.",
                "visual_prompt": "glowing neon padlock over a family portrait, digital security concept, modern tech aesthetic, cinematic lighting, 8k resolution",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Deepfake", "#ScamAlert", "#CyberSecurity", "#TechNews", "#AI"
        ],
        "tags": [
            "shorts", "ai voice clone", "deepfake", "scam", "cyber security", "tech trend",
            "artificial intelligence", "warning", "clickbaitnt", "viral", "trending", "india"
        ],
    },

    # VIDEO 2 — Lab-Grown Meat Going Mainstream (Food Tech Trend)
    {
        "topic":    "Lab-Grown Meat in Fast Food",
        "category": "science",
        "title":    "You Probably Ate Fake Meat This Week #Shorts",
        "description": (
            "Lab-grown cultivated meat is officially hitting the mainstream. It's real meat, "
            "but no animal was ever killed to make it. Have you eaten it yet?\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #LabGrownMeat #FutureOfFood #Science #TechTrend "
            "#FoodFacts #MindBlown #DidYouKnow #Viral #Trending #FYP #WTF"
        ),
        "script_text": (
            "You probably ate fake meat this week and didn't even notice. But I don't mean "
            "plant-based vegan burgers. I mean real, biological meat that was grown in a "
            "science laboratory. Cultivated meat is officially taking over the global food "
            "supply. Scientists take a single harmless cell swab from a living chicken or cow, "
            "put it into a giant steel bioreactor, and feed it nutrients until it grows into "
            "real muscle tissue. It has the exact same DNA, taste, and texture as regular meat, "
            "but zero animals actually had to die for it. Fast food chains are quietly starting "
            "to test it in their nuggets and burgers right now because it is becoming cheaper "
            "to produce than farming. Would you eat a burger grown in a science lab? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "You probably ate fake meat this week and didn't even notice. But I don't mean plant-based vegan burgers. I mean real, biological meat that was grown in a science laboratory.",
                "visual_prompt": "juicy realistic hamburger sitting on a clean modern laboratory table next to glowing microscopes and test tubes, future of food concept, 8k photorealistic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Cultivated meat is officially taking over the global food supply. Scientists take a single harmless cell swab from a living cow...",
                "visual_prompt": "giant stainless steel brewery-style bioreactor tanks in a pristine futuristic facility, glowing green and blue lights, high tech food production",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "...and feed it nutrients until it grows into real muscle tissue. It has the exact same DNA, taste, and texture as regular meat, but zero animals actually had to die for it.",
                "visual_prompt": "abstract macro visualization of glowing cells rapidly multiplying and forming into a recognizable piece of meat, biological science magic, cinematic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Fast food chains are quietly starting to test it in their nuggets right now. Would you eat a burger grown in a science lab? Comment below.",
                "visual_prompt": "person holding a fast food burger looking suspicious at it, while digital sci-fi scanning graphics overlay the meat, futuristic consumer concept",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#LabGrownMeat", "#FutureOfFood", "#FoodTech", "#ScienceFacts", "#Innovation"
        ],
        "tags": [
            "shorts", "lab grown meat", "fake meat", "future of food", "science", 
            "technology", "food facts", "burger", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 3 — De-influencing Mega-Trend (Internet Culture)
    {
        "topic":    "The De-Influencing Movement",
        "category": "culture",
        "title":    "Why Famous Influencers Are Going Bankrupt #Shorts",
        "description": (
            "The traditional influencer is dying. The massive 'De-influencing' trend is "
            "destroying brand deals as audiences demand extreme authenticity.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Deinfluencing #TikTokTrend #InternetCulture #SocialMedia "
            "#Exposed #Psychology #Viral #Trending #FYP #CreatorEconomy #India"
        ),
        "script_text": (
            "The most famous influencers on the internet are secretly going bankrupt, "
            "and it is all because of a massive new psychological trend. It is called "
            "De-influencing. For the last ten years, people blindly bought whatever "
            "celebrities told them to buy. But audiences have officially snapped. "
            "People are so exhausted by fake sponsorships and edited lifestyles that "
            "the algorithm has completely flipped. Now, the most viral videos are normal "
            "people brutally reviewing and exposing the terrible products that big "
            "influencers are trying to sell. Authenticity is the new currency. If you "
            "look too perfect or too sponsored, nobody trusts you anymore. Brands are "
            "panicking and pulling their million-dollar deals. Who is an influencer you "
            "used to love but absolutely cannot stand anymore? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "The most famous influencers on the internet are secretly going bankrupt, and it is all because of a massive new psychological trend. It is called De-influencing.",
                "visual_prompt": "glamorous social media influencer holding shopping bags but their digital follower count above their head is rapidly dropping to zero in glowing red numbers, cinematic 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "For the last ten years, people blindly bought whatever celebrities told them to buy. But audiences have officially snapped. People are so exhausted by fake sponsorships...",
                "visual_prompt": "person aggressively swiping their phone screen, looking incredibly bored and annoyed at fake bright social media ads, dark moody lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "...that the algorithm has completely flipped. Now, the most viral videos are normal people brutally reviewing and exposing the terrible products that big influencers sell.",
                "visual_prompt": "normal person in a messy bedroom holding up a broken luxury product with a big red 'X' over it, authentic viral video aesthetic, highly detailed",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "If you look too perfect, nobody trusts you anymore. Brands are pulling their million-dollar deals. Who is an influencer you used to love but absolutely cannot stand anymore? Comment below.",
                "visual_prompt": "burning social media contract with golden coins turning to ash, the death of fake influencer culture, dramatic conceptual photography, 8k",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Deinfluencing", "#InternetCulture", "#CreatorEconomy", "#Exposed", "#SocialMedia"
        ],
        "tags": [
            "shorts", "deinfluencing", "influencer", "tiktok trend", "internet culture", 
            "social media", "exposed", "fake", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 4 — The First Trillionaire (Economy Trend)
    {
        "topic":    "The Race for the First Trillionaire",
        "category": "news",
        "title":    "Someone Is About To Become A Trillionaire #Shorts",
        "description": (
            "The world is about to crown its first Trillionaire. But human brains cannot "
            "actually comprehend how massive one trillion dollars really is.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Trillionaire #Wealth #Economy #MoneyFacts #ElonMusk "
            "#Billionaire #MindBlown #DidYouKnow #Viral #Trending #FYP #WTF"
        ),
        "script_text": (
            "Someone alive right now is about to become the first Trillionaire in human history. "
            "But your brain literally cannot comprehend how much money that is. Let me break "
            "it down for you. One million seconds is twelve days. One billion seconds is "
            "thirty-one years. One trillion seconds is thirty-one thousand years. If you "
            "earned one hundred thousand dollars every single day since the pyramids were "
            "built in Egypt five thousand years ago, you still would not even be close to "
            "having one trillion dollars today. Yet, due to the massive explosion of AI and "
            "tech monopolies, financial experts predict the world's first trillionaire will "
            "be crowned within the next three years. If you had one trillion dollars, what "
            "is the very first stupid thing you would buy? Comment below."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Someone alive right now is about to become the first Trillionaire in human history. But your brain literally cannot comprehend how much money that is.",
                "visual_prompt": "massive towering mountain made entirely of glowing gold coins and glowing green digital money, towering up into the clouds, unimaginable wealth concept, 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 2,
                "narration": "Let me break it down for you. One million seconds is twelve days. One billion seconds is thirty-one years. One trillion seconds is thirty-one thousand years.",
                "visual_prompt": "split screen showing a ticking clock on the left and a rapid time lapse of ancient history turning into a futuristic city on the right, cinematic time scale",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "If you earned one hundred thousand dollars every single day since the pyramids were built, you still would not even be close to having one trillion dollars today.",
                "visual_prompt": "ancient Egyptian pharaoh standing next to a massive pyramid that is slowly filling up with stacks of cash, historical wealth comparison, hyper-realistic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Financial experts predict the world's first trillionaire will be crowned within the next three years. If you had one trillion dollars, what is the very first stupid thing you would buy? Comment below.",
                "visual_prompt": "a shadowy figure in a highly futuristic penthouse looking over a neon cyberpunk city, holding a glowing black credit card, ultimate wealth aesthetic",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Trillionaire", "#Wealth", "#Economy", "#MoneyFacts", "#Billionaire"
        ],
        "tags": [
            "shorts", "trillionaire", "billionaire", "money facts", "economy", 
            "wealth", "rich", "mind blown", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 5 — Cloning the Woolly Mammoth (Science/Cloning Trend)
    {
        "topic":    "De-Extinction / Cloning the Woolly Mammoth",
        "category": "science",
        "title":    "Scientists Just Started Jurassic Park In Real Life #Shorts",
        "description": (
            "Colossal Biosciences is literally cloning the Woolly Mammoth right now. "
            "They plan to release them into the Arctic in 2028.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #WoollyMammoth #Cloning #DeExtinction #ScienceNews "
            "#JurassicPark #Animals #MindBlown #Viral #Trending #FYP #WTF"
        ),
        "script_text": (
            "Scientists are literally building Jurassic Park in real life right now. "
            "A biotech company called Colossal is actively reviving the Woolly Mammoth. "
            "They are taking DNA recovered from frozen mammoth fossils and splicing it "
            "into the DNA of modern Asian elephants. The goal is to create a cold-resistant "
            "hybrid that perfectly resembles the extinct giant. And this isn't some distant "
            "sci-fi dream. They have hundreds of millions in funding and have announced "
            "they expect the first baby mammoth to be born in the year 2028. They plan to "
            "release entire herds of them into the Arctic tundra to help fight climate change "
            "by restoring the ancient ecosystem. What extinct animal do you think they should "
            "bring back next? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Scientists are literally building Jurassic Park in real life right now. A biotech company called Colossal is actively reviving the Woolly Mammoth.",
                "visual_prompt": "massive frozen woolly mammoth trapped in glowing blue ice being scanned by red lasers in a high tech dark laboratory, cinematic sci-fi cloning concept, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "They are taking DNA recovered from frozen mammoth fossils and splicing it into the DNA of modern Asian elephants. The goal is to create a cold-resistant hybrid.",
                "visual_prompt": "abstract medical visualization of glowing double helix DNA chains merging together, half elephant and half ancient icy mammoth DNA, neon scientific lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "And this isn't some distant sci-fi dream. They have announced they expect the first baby mammoth to be born in the year 2028.",
                "visual_prompt": "scientist looking proudly through thick glass at a highly realistic baby woolly mammoth sleeping in a futuristic artificial womb incubator, mind blowing science",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "They plan to release entire herds of them into the Arctic tundra to help fight climate change. What extinct animal do you think they should bring back next? Comment below.",
                "visual_prompt": "epic cinematic wide shot of a herd of massive woolly mammoths walking across a snowy arctic landscape during a beautiful sunset, de-extinction reality, 8k",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#DeExtinction", "#WoollyMammoth", "#ScienceNews", "#Cloning", "#JurassicPark"
        ],
        "tags": [
            "shorts", "woolly mammoth", "cloning", "de-extinction", "science news", 
            "jurassic park", "dna", "biology", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 6 — Brain-Computer Interfaces (BCI / Neuralink trend)
    {
        "topic":    "Brain-Computer Interfaces / Mind Control Gaming",
        "category": "tech",
        "title":    "People Are Now Playing Video Games With Their Minds #Shorts",
        "description": (
            "Brain chips like Neuralink are officially working. Paralyzed patients are "
            "now playing Mario Kart and browsing the internet using only their thoughts.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #Neuralink #BrainChip #Cyberpunk #TechNews #Gaming "
            "#FutureTech #MindBlown #DidYouKnow #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "People are officially playing video games using nothing but their thoughts. "
            "The era of brain-computer interfaces is here. Companies like Neuralink have "
            "successfully implanted chips into human brains, allowing paralyzed patients "
            "to control computers just by thinking about it. No hands, no voice commands. "
            "The chip reads the electrical signals in their brain's motor cortex and translates "
            "it instantly into digital movement. Patients are already playing Mario Kart, "
            "browsing Twitter, and playing chess at superhuman speeds using pure telepathy. "
            "Within our lifetime, keyboards and mice will become entirely obsolete. You will "
            "just look at a screen and think your commands. Would you let a doctor put a "
            "computer chip in your brain? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "People are officially playing video games using nothing but their thoughts. The era of brain-computer interfaces is here.",
                "visual_prompt": "person sitting calmly with their eyes closed while glowing digital gaming UI and code floats in the air around their head, mind control gaming concept, cyberpunk 8k",
                "duration_estimate": 7,
            },
            {
                "scene_number": 2,
                "narration": "Companies like Neuralink have successfully implanted chips into human brains, allowing paralyzed patients to control computers just by thinking about it. No hands, no voice commands.",
                "visual_prompt": "glowing microchip resting on the surface of a highly detailed human brain, connecting with glowing blue neural pathways, advanced medical technology, cinematic lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "The chip reads the electrical signals in their brain's motor cortex and translates it instantly into digital movement. Patients are already playing Mario Kart and chess at superhuman speeds.",
                "visual_prompt": "abstract visualization of lightning-fast electrical brain waves shooting directly into a glowing computer monitor, telepathy tech, neon lighting",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Within our lifetime, keyboards will become obsolete. You will just look at a screen and think your commands. Would you let a doctor put a computer chip in your brain? Comment below.",
                "visual_prompt": "close up of an eye looking at a screen, with digital crosshairs and data reflecting in the pupil, futuristic human upgrade, sci-fi reality, 8k",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#Neuralink", "#BrainChip", "#Cyberpunk", "#TechNews", "#GamingTrend"
        ],
        "tags": [
            "shorts", "neuralink", "brain chip", "mind control", "gaming", "tech news", 
            "cyberpunk", "future tech", "science", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 7 — The AI Virtual Influencer Takeover
    {
        "topic":    "AI Models Replacing Humans",
        "category": "culture",
        "title":    "The Most Famous Model On Instagram Doesn't Exist #Shorts",
        "description": (
            "Human models are losing their jobs to AI. Virtual influencers are making millions "
            "in sponsorships and millions of fans don't know they are fake.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #AIInfluencer #ArtificialIntelligence #TechTrend "
            "#Simulation #Creepy #SocialMedia #MindBlown #Viral #Trending #FYP #WTF"
        ),
        "script_text": (
            "The most beautiful person you follow on Instagram might not actually exist. "
            "Human models are rapidly losing their jobs to artificial intelligence. "
            "Agencies are now generating entirely fake, hyper-realistic virtual influencers "
            "who are making millions of dollars in brand sponsorships. These AI models "
            "never get tired, they never age, and they don't demand a salary. They can do "
            "a photoshoot in Paris and Tokyo on the exact same day with the click of a "
            "button. The craziest part? Millions of people following them and commenting "
            "on their photos have absolutely no idea they are staring at computer code. "
            "We are entering an era where you cannot trust a single photo you see online. "
            "Have you ever been fooled by an AI picture? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "The most beautiful person you follow on Instagram might not actually exist. Human models are rapidly losing their jobs to artificial intelligence.",
                "visual_prompt": "stunningly beautiful instagram model posing for a selfie, but her skin is slightly glitching to reveal glowing green matrix code underneath, AI illusion, 8k cinematic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Agencies are now generating entirely fake, hyper-realistic virtual influencers who are making millions of dollars in brand sponsorships.",
                "visual_prompt": "dark server room where a supercomputer monitor shows a highly realistic 3D model being generated wireframe by wireframe into a human, digital creation concept",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "These AI models never get tired, they never age, and they don't demand a salary. They can do a photoshoot in Paris and Tokyo on the exact same day.",
                "visual_prompt": "split screen of the exact same AI model flawlessly posing in front of the Eiffel Tower and neon Tokyo streets simultaneously, uncanny perfection, vibrant colors",
                "duration_estimate": 8,
            },
            {
                "scene_number": 4,
                "narration": "Millions of people have no idea they are staring at computer code. We are entering an era where you cannot trust a single photo. Have you ever been fooled by an AI picture? Comment below.",
                "visual_prompt": "person holding a glowing smartphone looking completely fooled, heart icons floating up from the screen while dark robotic arms control the device, creepy tech aesthetic",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#AIInfluencer", "#Deepfake", "#ArtificialIntelligence", "#TechTrend", "#Simulation"
        ],
        "tags": [
            "shorts", "ai influencer", "ai model", "artificial intelligence", "simulation", 
            "social media", "creepy", "future", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 8 — The 4-Day Work Week Shift (Society Trend)
    {
        "topic":    "The Global 4-Day Work Week",
        "category": "society",
        "title":    "The 5-Day Work Week Is Officially Dead #Shorts",
        "description": (
            "The biggest corporate shift in 100 years is happening right now. The 4-day "
            "work week is taking over the world because it actually makes companies richer.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #4DayWorkWeek #WorkLifeBalance #Productivity #MentalHealth "
            "#FutureOfWork #Corporate #News #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "The five day work week is officially dying, and billionaires are furious. "
            "The biggest shift in global work culture since the industrial revolution is "
            "happening right now. Dozens of countries and major corporations are permanently "
            "switching to a four-day work week with no cut in pay. And the results are "
            "terrifying to old-school bosses. In the largest global trials, companies found "
            "that when employees worked one day less, they were actually significantly more "
            "productive. Sick days dropped by sixty five percent, revenue went up, and "
            "employee burnout plummeted. It turns out humans are not designed to sit in "
            "a cubicle for forty hours a week. If you had a three day weekend every single "
            "week, what would you do with your extra day off? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "The five day work week is officially dying, and billionaires are furious. The biggest shift in global work culture since the industrial revolution is happening right now.",
                "visual_prompt": "giant heavy stone calendar cracking and breaking apart, specifically destroying the 'Friday' block, end of the work week concept, cinematic dramatic lighting 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "Dozens of countries and major corporations are permanently switching to a four-day work week with no cut in pay. And the results are terrifying to old-school bosses.",
                "visual_prompt": "angry old man in an expensive suit looking at a glowing green stock market chart that is pointing straight up while his employees are leaving the office early, corporate reality",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "In the largest global trials, companies found that when employees worked one day less, they were actually significantly more productive. Sick days dropped and burnout plummeted.",
                "visual_prompt": "abstract visualization of a glowing human battery charging from 50 percent instantly up to 100 percent maximum power, mental health and energy concept, vibrant lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "It turns out humans are not designed to sit in a cubicle for forty hours a week. If you had a three day weekend every single week, what would you do with your extra day off? Comment below.",
                "visual_prompt": "person relaxing happily on a sunny beach, holding a laptop that is closed and covered in sand, ultimate work life balance aesthetic, beautiful lighting",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#4DayWorkWeek", "#WorkLifeBalance", "#Productivity", "#FutureOfWork", "#MentalHealth"
        ],
        "tags": [
            "shorts", "4 day work week", "work life balance", "corporate", "productivity", 
            "mental health", "news", "trend", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 9 — The Drone Delivery Sky Traffic
    {
        "topic":    "Drone Delivery Skyways",
        "category": "tech",
        "title":    "Looking Up At The Sky Will Never Be The Same #Shorts",
        "description": (
            "Companies like Amazon and Walmart are launching massive drone delivery fleets. "
            "The sky above your house is about to become an invisible highway.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #DroneDelivery #TechTrend #FutureCity #Amazon #Logistics "
            "#ScienceFiction #MindBlown #Viral #Trending #FYP #India"
        ),
        "script_text": (
            "Looking up at the sky is about to get incredibly annoying. Welcome to the era "
            "of drone skyways. Massive retail giants like Amazon and Walmart are quietly "
            "mapping out invisible highways in the sky above your city. Very soon, instead "
            "of a delivery truck pulling up to your house, thousands of autonomous drones "
            "will be constantly buzzing overhead, dropping off groceries, medicine, and "
            "packages directly into your backyard in under thirty minutes. The FAA is "
            "currently struggling to regulate the massive 'sky traffic' this will create. "
            "Cities are preparing for noise pollution, drone crashes, and package hijackings. "
            "The quiet suburban sky is gone forever. Would you rather have your packages "
            "delivered by a slow truck, or a noisy flying drone? Comment below and follow ClickBaitnt."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "Looking up at the sky is about to get incredibly annoying. Welcome to the era of drone skyways. Massive retail giants are quietly mapping out invisible highways...",
                "visual_prompt": "view looking up at a blue sky filled with glowing neon grid lines mapping out invisible digital highways, futuristic smart city concept, cinematic 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "...in the sky above your city. Very soon, thousands of autonomous drones will be constantly buzzing overhead, dropping off packages directly into your backyard.",
                "visual_prompt": "hundreds of sleek modern delivery drones swarming in the sky carrying cardboard boxes, futuristic logistics, hyper-detailed sci-fi reality",
                "duration_estimate": 7,
            },
            {
                "scene_number": 3,
                "narration": "The FAA is currently struggling to regulate the massive 'sky traffic' this will create. Cities are preparing for noise pollution, drone crashes, and package hijackings.",
                "visual_prompt": "two delivery drones crashing into each other mid-air dropping a box, chaotic futuristic city problem, dramatic action shot, cinematic lighting",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "The quiet suburban sky is gone forever. Would you rather have your packages delivered by a slow truck, or a noisy flying drone? Comment below and follow ClickBaitnt.",
                "visual_prompt": "split screen of a boring old delivery truck stuck in traffic versus a sleek fast drone flying over the traffic jam, tech debate concept, high quality",
                "duration_estimate": 8,
            },
        ],
        "topic_hashtags": [
            "#DroneDelivery", "#TechTrend", "#FutureCity", "#Logistics", "#TechNews"
        ],
        "tags": [
            "shorts", "drone delivery", "amazon drone", "future tech", "smart city", 
            "tech news", "future", "drones", "clickbaitnt", "viral", "trending"
        ],
    },

    # VIDEO 10 — The Deep Ocean Mining Race
    {
        "topic":    "Deep Sea Mining Resource Rush",
        "category": "environment",
        "title":    "Billionaires Are Destroying The Bottom Of The Ocean #Shorts",
        "description": (
            "A massive new gold rush is happening at the bottom of the ocean. Corporations "
            "are mining the deep sea for battery metals, and it might destroy the ecosystem.\n\n"
            "---\nFollow @ClickBaitn't for daily mind-blowing facts!\n\n"
            "#Shorts #ClickBaitnt #DeepSeaMining #Ocean #Environment #TechNews #ElectricVehicles "
            "#ScaryFacts #DidYouKnow #Viral #Trending #FYP #WTF"
        ),
        "script_text": (
            "There is a secret gold rush happening right now, and it might destroy the planet. "
            "To build enough batteries for all the new electric cars and smartphones, "
            "corporations are running out of metals on land. So, they are going to the "
            "bottom of the ocean. It is called Deep Sea Mining. Massive, remote-controlled "
            "robotic tanks are being lowered thousands of feet into the pitch-black abyss. "
            "They drive across the ocean floor, vacuuming up potato-sized rocks called "
            "polymetallic nodules that are packed with pure cobalt, nickel, and copper. "
            "But marine biologists are terrified. These machines are ripping up ancient, "
            "undiscovered alien-like ecosystems and creating massive toxic dust clouds in "
            "the water. Are electric cars worth destroying the bottom of the ocean? "
            "Comment below and follow ClickBaitnt for more."
        ),
        "scenes": [
            {
                "scene_number": 1,
                "narration": "There is a secret gold rush happening right now, and it might destroy the planet. To build enough batteries for all the new electric cars, corporations are running out of metals on land.",
                "visual_prompt": "massive pile of glowing high-tech electric car batteries sitting next to an empty barren strip mine, resource depletion concept, dark cinematic lighting, 8k",
                "duration_estimate": 8,
            },
            {
                "scene_number": 2,
                "narration": "So, they are going to the bottom of the ocean. It is called Deep Sea Mining. Massive, remote-controlled robotic tanks are being lowered thousands of feet into the pitch-black abyss.",
                "visual_prompt": "giant terrifying robotic mining tank with massive treads and bright spotlights landing on the dark ocean floor, sci-fi industrial underwater aesthetic, photorealistic",
                "duration_estimate": 8,
            },
            {
                "scene_number": 3,
                "narration": "They vacuum up rocks called polymetallic nodules that are packed with pure cobalt and copper. But marine biologists are terrified. These machines are ripping up ancient ecosystems...",
                "visual_prompt": "robotic machine violently vacuuming up glowing rocks from the ocean floor while beautiful alien-like deep sea creatures flee in terror, environmental destruction concept",
                "duration_estimate": 7,
            },
            {
                "scene_number": 4,
                "narration": "...and creating massive toxic dust clouds in the water. Are electric cars worth destroying the bottom of the ocean? Comment below and follow ClickBaitnt for more.",
                "visual_prompt": "split screen of a pristine shiny new electric car driving on a clean road, and a devastated murky destroyed ocean floor below it, dark contrast art, 8k",
                "duration_estimate": 7,
            },
        ],
        "topic_hashtags": [
            "#DeepSeaMining", "#Ocean", "#TechTrend", "#Environment", "#ElectricVehicles"
        ],
        "tags": [
            "shorts", "deep sea mining", "ocean", "environment", "electric cars", 
            "tech news", "future", "scary facts", "clickbaitnt", "viral", "trending"
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
            trend_source = "batch_trending_10",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"batch_trending_10.py — {script['topic']}"
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
    print("  AUTO-SHORTS-ENGINE — Mega Trend Mix (Batch of 10)")
    print(f"  Uploading {len(SCRIPTS)} videos as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_trendmeg{idx}"

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