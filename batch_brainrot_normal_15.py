"""
batch_brainrot_normal_15.py — 15 Normal-Length Viral Shorts.

Same pipeline as previous batches:
  TTS -> Audio -> Whisper -> Images -> Video -> Upload -> Tracker

Run:
  python batch_brainrot_normal_15.py
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

# ── 15 hardcoded scripts (Normal Length / 4 Scenes) ──────────────────────────

SCRIPTS = [
    # 1. Mandela Effect - Yellow Sun
    {
        "topic": "Yellow Sun Mandela Effect",
        "category": "mystery",
        "title": "We Shifted Into A New Timeline #Shorts",
        "description": "Do you remember the sun being yellow? It's white now. The Mandela Effect is real.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #MandelaEffect #Glitch #Simulation",
        "script_text": "You are living in a different timeline, and the proof is literally in the sky. Do you remember the sun being a warm, bright yellow when you were a kid? Think about how you used to draw it in school. Look outside today. The sun is a harsh, blinding, LED white. Millions of people vividly remember a yellow sun, but scientists claim it has always been white. Did our universe shift into a parallel dimension, or is this a glitch in the simulation? Do you remember the yellow sun? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "You are living in a different timeline, and the proof is literally in the sky. Do you remember the sun being a warm, bright yellow when you were a kid?", "visual_prompt": "nostalgic 90s childhood memory looking up at a bright warm yellow sun in a blue sky, vintage polaroid aesthetic, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "Think about how you used to draw it in school. Look outside today. The sun is a harsh, blinding, LED white.", "visual_prompt": "split screen, left is a happy child's drawing of a yellow sun, right is a harsh blinding white LED-like sun in a real sky, reality glitching, cinematic", "duration_estimate": 8},
            {"scene_number": 3, "narration": "Millions of people vividly remember a yellow sun, but scientists claim it has always been white. Did our universe shift into a parallel dimension, or is this a glitch in the simulation?", "visual_prompt": "glowing sun glitching and morphing between warm yellow and harsh white, matrix simulation effect, deep space aesthetic", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Do you remember the yellow sun? Comment below and follow ClickBaitnt.", "visual_prompt": "glowing neon question mark hovering in a dark starry sky, surreal internet mystery aesthetic", "duration_estimate": 6}
        ],
        "tags": ["shorts", "mandela effect", "yellow sun", "glitch", "simulation", "creepy", "clickbaitnt", "viral"]
    },

    # 2. Mirror Glitch (Troxler Effect)
    {
        "topic": "Troxler Effect",
        "category": "psychology",
        "title": "Never Stare Into A Mirror In The Dark #Shorts",
        "description": "Your brain will hallucinate a monster if you stare in a mirror.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Scary #Psychology",
        "script_text": "Never stare into a mirror in the dark. It is the easiest way to accidentally traumatize yourself. If you sit in a dimly lit room and stare directly at your own reflection for ten minutes, your brain will physically glitch. Because your eyes lack stimulation, your brain starts deleting your face and replacing it with terrifying hallucinations. Your face will literally morph into a twisted, distorted monster right in front of your eyes. It is a psychological glitch called the Troxler Effect. Have you ever hallucinated in the dark? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Never stare into a mirror in the dark. It is the easiest way to accidentally traumatize yourself.", "visual_prompt": "person staring blankly into a dark bathroom mirror illuminated only by a faint glowing light, terrifying psychological thriller aesthetic, 8k", "duration_estimate": 7},
            {"scene_number": 2, "narration": "If you sit in a dimly lit room and stare directly at your own reflection for ten minutes, your brain will physically glitch. Because your eyes lack stimulation...", "visual_prompt": "close up of an eye staring intensely in the dark, digital static and glitching effects surrounding the pupil, brain overload", "duration_estimate": 8},
            {"scene_number": 3, "narration": "...your brain starts deleting your face and replacing it with terrifying hallucinations. Your face will literally morph into a twisted, distorted monster right in front of your eyes.", "visual_prompt": "reflection in the mirror melting and shifting into a dark shadowy demonic figure with hollow eyes, scary horror concept", "duration_estimate": 8},
            {"scene_number": 4, "narration": "It is a psychological glitch called the Troxler Effect. Have you ever hallucinated in the dark? Comment below and follow ClickBaitnt.", "visual_prompt": "mirror shattering into a million glowing pieces, dark cinematic shadows, psychological thriller vibes", "duration_estimate": 6}
        ],
        "tags": ["shorts", "scary", "mirror", "troxler effect", "psychology", "hallucination", "creepy", "clickbaitnt", "viral"]
    },

    # 3. You've never touched anything
    {
        "topic": "Atomic Repulsion",
        "category": "science",
        "title": "You Have Never Touched Anything In Your Life #Shorts",
        "description": "Atomic repulsion means you literally hover above chairs.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Science #Physics #MindBlown",
        "script_text": "You have never actually touched anything in your entire life. Not your phone, not your bed, not even another human being. Because of the laws of quantum physics, the electrons in your body violently repel the electrons in other objects. When you sit on a chair, you are actually hovering a microscopic fraction of a millimeter above it, suspended by a repulsive electromagnetic forcefield. The feeling of touch is just your brain interpreting that forcefield pushing back against your skin. You are literally floating through life. Does this break your brain? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "You have never actually touched anything in your entire life. Not your phone, not your bed, not even another human being.", "visual_prompt": "extreme macro view of a human finger about to touch a surface, but a glowing blue forcefield of electrons violently pushes them apart, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "Because of the laws of quantum physics, the electrons in your body violently repel the electrons in other objects. When you sit on a chair...", "visual_prompt": "abstract visualization of glowing blue and red atoms violently bouncing off each other like magnets, quantum physics concept, cinematic", "duration_estimate": 8},
            {"scene_number": 3, "narration": "...you are actually hovering a microscopic fraction of a millimeter above it, suspended by a repulsive electromagnetic forcefield. The feeling of touch is just your brain interpreting that forcefield.", "visual_prompt": "person hovering a fraction of an inch above a glowing neon chair, physics reality glitch concept, dramatic lighting", "duration_estimate": 8},
            {"scene_number": 4, "narration": "You are literally floating through life. Does this break your brain? Comment below and follow ClickBaitnt.", "visual_prompt": "glowing green computer code shattering like glass, hacking the simulation aesthetic", "duration_estimate": 6}
        ],
        "tags": ["shorts", "physics", "science", "matrix", "mind blown", "simulation", "clickbaitnt", "viral"]
    },

    # 4. Eyelash Mites
    {
        "topic": "Demodex Mites",
        "category": "biology",
        "title": "There Are Bugs Living On Your Face Right Now #Shorts",
        "description": "Demodex mites live in your eyelashes and eat dead skin.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Gross #Biology #Facts",
        "script_text": "There are microscopic bugs mating on your face right now, and you cannot wash them off. They are called Demodex mites, and they live deep inside your eyelash hair follicles and facial pores. During the day, they sleep face-down inside your skin. But when you go to sleep, they crawl out, walk across your face to eat your dead skin, and lay eggs. The craziest part? They don't have an anus, so they just explode when they die on your face. Is your face suddenly feeling incredibly itchy right now? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "There are microscopic bugs mating on your face right now, and you cannot wash them off. They are called Demodex mites...", "visual_prompt": "extreme terrifying microscopic view of alien-like mites crawling inside a human eyelash follicle, highly detailed biological horror, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "...and they live deep inside your eyelash hair follicles and facial pores. During the day, they sleep face-down inside your skin.", "visual_prompt": "cross section of human skin showing creepy glowing bugs sleeping deep inside the pores, biological realism, moody lighting", "duration_estimate": 8},
            {"scene_number": 3, "narration": "But when you go to sleep, they crawl out, walk across your face to eat your dead skin, and lay eggs. The craziest part? They don't have an anus...", "visual_prompt": "glowing neon green bugs crawling over a dark moon-like landscape of human skin pores under a microscope, disgusting biology facts", "duration_estimate": 8},
            {"scene_number": 4, "narration": "...so they just explode when they die on your face. Is your face suddenly feeling incredibly itchy right now? Comment below and follow ClickBaitnt.", "visual_prompt": "person aggressively scratching their face looking paranoid, funny but gross medical aesthetic, dramatic lighting", "duration_estimate": 7}
        ],
        "tags": ["shorts", "gross", "mites", "biology", "human body", "scary facts", "clickbaitnt", "viral"]
    },

    # 5. Reading in Dreams
    {
        "topic": "Reading in Dreams",
        "category": "psychology",
        "title": "You Cannot Read Inside A Dream #Shorts",
        "description": "Your brain shuts down language processing when you sleep.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Dreams #Psychology #Glitch",
        "script_text": "You are physically incapable of reading inside a dream. The next time you are dreaming, try to look at a clock, a sign, or a book. It will be completely impossible. The part of your brain that processes language and logic, called the Wernicke's area, completely shuts down when you enter REM sleep. If you try to read, the words will constantly shift, blur, and turn into unreadable alien gibberish. This is the ultimate reality check to test if you are trapped in a dream. Have you ever tried to read while dreaming? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "You are physically incapable of reading inside a dream. The next time you are dreaming, try to look at a clock, a sign, or a book. It will be completely impossible.", "visual_prompt": "person sleeping peacefully, with a glowing x-ray view showing the language center of their brain powering down to pitch black, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "The part of your brain that processes language and logic, called the Wernicke's area, completely shuts down when you enter REM sleep.", "visual_prompt": "abstract medical visualization of a brain where one specific glowing quadrant suddenly loses power and goes dark, neuroscience concept", "duration_estimate": 8},
            {"scene_number": 3, "narration": "If you try to read, the words will constantly shift, blur, and turn into unreadable alien gibberish. This is the ultimate reality check to test if you are trapped in a dream.", "visual_prompt": "POV looking at a digital clock and an open book in a dark room, but the numbers and letters are swirling alien symbols that make no sense, dream glitch reality", "duration_estimate": 9},
            {"scene_number": 4, "narration": "Have you ever tried to read while dreaming? Comment below and follow ClickBaitnt.", "visual_prompt": "glowing brain shattering into a thousand digital glitching pixels, cinematic cyber aesthetic", "duration_estimate": 6}
        ],
        "tags": ["shorts", "dreams", "lucid dreaming", "psychology", "brain facts", "glitch", "clickbaitnt", "viral"]
    },

    # 6. Solipsism
    {
        "topic": "Solipsism",
        "category": "philosophy",
        "title": "What If Everyone Else Is Fake? #Shorts",
        "description": "The terrifying theory that you are the only conscious human.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #DeepThoughts #Simulation",
        "script_text": "What if you are the only real person on Earth, and everyone else is just a fake simulation? This is a terrifying philosophical concept called Solipsism. It suggests that your own mind is the only thing that actually exists. Your friends, your family, and even this video could just be incredibly advanced NPCs generated by your brain to keep you entertained in a lonely void. You have absolutely no way to prove that anyone around you is actually conscious. I might just be code in your simulation. Prove you are real in the comments and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "What if you are the only real person on Earth, and everyone else is just a fake simulation? This is a terrifying philosophical concept called Solipsism.", "visual_prompt": "lone person standing in a crowded city, but everyone else has a glowing green hollow wireframe body like a video game NPC, simulation concept, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "It suggests that your own mind is the only thing that actually exists. Your friends, your family, and even this video could just be incredibly advanced NPCs...", "visual_prompt": "person looking at their friends, but their friends' faces briefly glitch into digital computer code, cyberpunk simulation aesthetic", "duration_estimate": 8},
            {"scene_number": 3, "narration": "...generated by your brain to keep you entertained in a lonely void. You have absolutely no way to prove that anyone around you is actually conscious.", "visual_prompt": "person floating completely alone in a dark, infinite, empty cosmic void, representing the terrifying loneliness of solipsism, 8k cinematic", "duration_estimate": 8},
            {"scene_number": 4, "narration": "I might just be code in your simulation. Prove you are real in the comments and follow ClickBaitnt.", "visual_prompt": "smartphone screen playing a video, but the video slowly dissolves into cascading green matrix code, deep existential crisis aesthetic", "duration_estimate": 7}
        ],
        "tags": ["shorts", "solipsism", "philosophy", "npc", "simulation", "matrix", "deep thoughts", "clickbaitnt", "viral"]
    },

    # 7. Octopuses are aliens
    {
        "topic": "Octopus Panspermia",
        "category": "science",
        "title": "Octopuses Are Literally Aliens From Space #Shorts",
        "description": "Scientists believe octopus eggs came from meteors.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Aliens #Ocean #Science",
        "script_text": "Octopuses are literally aliens from outer space, and scientists actually have proof. Their DNA is so incredibly complex and entirely different from any other animal on Earth that evolutionary biologists are completely baffled. A massive group of scientists published a paper suggesting that frozen octopus eggs crashed into our oceans on an icy meteor millions of years ago. Think about it. They have three hearts, blue blood, can completely rewrite their own RNA, and can perfectly camouflage into anything. They are not from this planet. Do you believe in aliens? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Octopuses are literally aliens from outer space, and scientists actually have proof. Their DNA is so incredibly complex and entirely different from any other animal on Earth...", "visual_prompt": "massive glowing purple octopus floating through the starry void of outer space, surreal cosmic biology concept art, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "...that evolutionary biologists are completely baffled. A massive group of scientists published a paper suggesting that frozen octopus eggs crashed into our oceans on an icy meteor millions of years ago.", "visual_prompt": "flaming meteor crashing into the ancient ocean, cracking open underwater to reveal glowing alien octopus eggs, epic science realism", "duration_estimate": 8},
            {"scene_number": 3, "narration": "Think about it. They have three hearts, blue blood, can completely rewrite their own RNA, and can perfectly camouflage into anything. They are not from this planet.", "visual_prompt": "abstract x-ray view of a glowing octopus showing three beating hearts pumping neon blue blood, stunning biological visualization, cinematic", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Do you believe in aliens? Comment below and follow ClickBaitnt.", "visual_prompt": "alien UFO hovering over the dark ocean, beaming down a beam of light, cinematic sci-fi lighting", "duration_estimate": 6}
        ],
        "tags": ["shorts", "aliens", "octopus", "ocean", "panspermia", "science", "biology", "clickbaitnt", "viral"]
    },

    # 8. Hypnic Jerk
    {
        "topic": "Hypnic Jerk",
        "category": "science",
        "title": "Why You Feel Like You're Falling In Your Sleep #Shorts",
        "description": "Your brain thinks you are dying when you fall asleep too fast.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Sleep #BrainFacts #Psychology",
        "script_text": "Have you ever felt like you were falling right as you drifted off to sleep, causing you to violently twitch awake? Your brain actually thought you were dying. It is a biological glitch called a Hypnic Jerk. Sometimes, when you fall asleep too fast, your heart rate drops incredibly rapidly. Your primitive lizard brain panics, thinking your body is shutting down and you are literally dying. To save your life, it sends a massive electric shock down your spine to jump-start your organs and wake you up. How often does this happen to you? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Have you ever felt like you were falling right as you drifted off to sleep, causing you to violently twitch awake? Your brain actually thought you were dying.", "visual_prompt": "person sleeping peacefully in bed, but an ethereal glowing spirit version of them is endlessly falling into a dark abyss, dream concept, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "It is a biological glitch called a Hypnic Jerk. Sometimes, when you fall asleep too fast, your heart rate drops incredibly rapidly.", "visual_prompt": "glowing digital heart monitor screen rapidly dropping its heart rate, panic medical aesthetic, dramatic red lighting", "duration_estimate": 7},
            {"scene_number": 3, "narration": "Your primitive lizard brain panics, thinking your body is shutting down and you are literally dying. To save your life, it sends a massive electric shock down your spine...", "visual_prompt": "abstract medical visualization of a glowing brain sending a violent jagged bolt of blue lightning down a human spine, shocking the body awake, cinematic", "duration_estimate": 9},
            {"scene_number": 4, "narration": "...to jump-start your organs and wake you up. How often does this happen to you? Comment below and follow ClickBaitnt.", "visual_prompt": "person gasping awake in a dark bedroom covered in sweat, holding their chest, dramatic thriller lighting", "duration_estimate": 7}
        ],
        "tags": ["shorts", "sleep", "hypnic jerk", "falling in sleep", "brain facts", "psychology", "clickbaitnt", "viral"]
    },

    # 9. Cute Aggression
    {
        "topic": "Cute Aggression",
        "category": "psychology",
        "title": "Why You Want To Squeeze Cute Things #Shorts",
        "description": "Your brain uses anger to balance out intense cuteness.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Psychology #BrainFacts #Cute",
        "script_text": "Why do you suddenly want to violently squeeze or bite incredibly cute things? It is a bizarre brain glitch called Cute Aggression. When you see a fluffy kitten or a cute baby, your brain gets so overwhelmed by intense positive emotion that it literally cannot handle the energy. To stop your brain from short-circuiting, it forcefully injects anger and aggression into your system to balance you out. You don't actually want to hurt the animal; your brain is just trying to calm you down using fake rage. What is the cutest animal on earth? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Why do you suddenly want to violently squeeze or bite incredibly cute things? It is a bizarre brain glitch called Cute Aggression.", "visual_prompt": "person aggressively gritting their teeth while tightly squeezing an impossibly cute fluffy kitten, funny psychological reaction, 8k cinematic", "duration_estimate": 8},
            {"scene_number": 2, "narration": "When you see a fluffy kitten or a cute baby, your brain gets so overwhelmed by intense positive emotion that it literally cannot handle the energy.", "visual_prompt": "glowing human brain exploding with bright pink hearts and rainbow sparkles, cuteness overload visualization, vibrant colors", "duration_estimate": 8},
            {"scene_number": 3, "narration": "To stop your brain from short-circuiting, it forcefully injects anger and aggression into your system to balance you out. You don't actually want to hurt the animal...", "visual_prompt": "glowing brain split in half, one side radiating warm pink love hearts, the other side burning with fiery red anger, balancing scale concept", "duration_estimate": 8},
            {"scene_number": 4, "narration": "...your brain is just trying to calm you down using fake rage. What is the cutest animal on earth? Comment below and follow ClickBaitnt.", "visual_prompt": "adorable fluffy puppy looking up with giant shiny eyes, extreme cuteness overload, warm cinematic lighting", "duration_estimate": 7}
        ],
        "tags": ["shorts", "cute aggression", "psychology", "brain facts", "animals", "cute", "clickbaitnt", "viral"]
    },

    # 10. Phone IR Scanner
    {
        "topic": "Smartphone Face ID Scanners",
        "category": "tech",
        "title": "Your Phone Camera Is Watching You Sleep #Shorts",
        "description": "Infrared cameras on your phone map your face in the dark.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Creepy #CyberSecurity #Tech",
        "script_text": "Your smartphone camera is watching you sleep, and you can easily prove it. The Face ID scanners on modern phones don't just work when you unlock them. They constantly shoot out thousands of invisible infrared lasers to map your face, even in pitch-black darkness, just to check if you are paying attention to the screen. If you point a night-vision camera at your phone in the dark, you will see a terrifying flashing strobe light constantly scanning your room. You are never truly alone in your bedroom. Are you covering your camera right now? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Your smartphone camera is watching you sleep, and you can easily prove it. The Face ID scanners on modern phones don't just work when you unlock them.", "visual_prompt": "view through an infrared night vision camera looking at a person sleeping in bed, thousands of glowing laser dots mapping their face, creepy tech 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "They constantly shoot out thousands of invisible infrared lasers to map your face, even in pitch-black darkness, just to check if you are paying attention to the screen.", "visual_prompt": "dark bedroom where a smartphone on a nightstand is glowing with an evil looking red laser beam scanning the room, cyber stalker concept", "duration_estimate": 8},
            {"scene_number": 3, "narration": "If you point a night-vision camera at your phone in the dark, you will see a terrifying flashing strobe light constantly scanning your room.", "visual_prompt": "smartphone camera lens glowing with a bright intense infrared strobe light in the pitch black, surveillance tech aesthetic, cinematic", "duration_estimate": 8},
            {"scene_number": 4, "narration": "You are never truly alone in your bedroom. Are you covering your camera right now? Comment below and follow ClickBaitnt.", "visual_prompt": "finger slapping a black piece of tape over a smartphone camera lens, privacy concept, dramatic cinematic lighting", "duration_estimate": 7}
        ],
        "tags": ["shorts", "creepy", "smartphone", "privacy", "cyber security", "tech facts", "camera", "clickbaitnt", "viral"]
    },

    # 11. Universe is a Brain
    {
        "topic": "Cosmic Web / Neural Network",
        "category": "space",
        "title": "The Universe Is Actually A Giant Brain #Shorts",
        "description": "Galaxies and brain cells look exactly identical under a microscope.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Space #Simulation #MindBlown",
        "script_text": "The universe is actually a giant brain, and the scientific images prove it. When astrophysicists took a massive mapping scan of the cosmic web of galaxies and laid it next to a microscopic scan of human brain neurons, they were terrified. They looked exactly identical. The structure of the universe mimics the structure of a brain perfectly. Some quantum physicists now theorize that the entire universe might literally be a massive living, thinking organism, and we are just microscopic cells living inside of it. Are we inside a giant? Comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "The universe is actually a giant brain, and the scientific images prove it. When astrophysicists took a massive mapping scan of the cosmic web of galaxies...", "visual_prompt": "split screen, left side is a massive glowing cosmic web of purple galaxies, right side is a microscopic scan of glowing blue human brain neurons, looking identical, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "...and laid it next to a microscopic scan of human brain neurons, they were terrified. They looked exactly identical. The structure of the universe mimics the structure of a brain perfectly.", "visual_prompt": "the entire starry universe contained inside the silhouette of a massive glowing human head, epic cosmic horror, beautiful cinematic lighting", "duration_estimate": 9},
            {"scene_number": 3, "narration": "Some quantum physicists now theorize that the entire universe might literally be a massive living, thinking organism, and we are just microscopic cells living inside of it.", "visual_prompt": "earth floating like a tiny microscopic cell inside a massive glowing blood stream of a cosmic giant, surreal scale concept, highly detailed", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Are we inside a giant? Comment below and follow ClickBaitnt.", "visual_prompt": "glowing eye of a giant opening up in the middle of a starry nebula, mind blowing space mystery, 8k resolution", "duration_estimate": 6}
        ],
        "tags": ["shorts", "space", "universe", "brain", "simulation", "science", "astronomy", "clickbaitnt", "viral"]
    },

    # 12. Time Speeding Up
    {
        "topic": "Time Perception",
        "category": "psychology",
        "title": "Time Is Literally Speeding Up As You Age #Shorts",
        "description": "Why a year feels so much shorter when you are older.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Psychology #DeepThoughts #Time",
        "script_text": "Time is literally speeding up as you get older, and you are not crazy for feeling it. Remember when summer break felt like it lasted a lifetime when you were ten? Now, entire years vanish in a blink. It is because of how your brain processes memory. When you are a kid, everything is new, so your brain records dense, heavy memories. When you are an adult, your routine is exactly the same every day. Your brain stops recording new data, making the outside world feel like it is playing on fast forward. Subscribe to slow down time.",
        "scenes": [
            {"scene_number": 1, "narration": "Time is literally speeding up as you get older, and you are not crazy for feeling it. Remember when summer break felt like it lasted a lifetime when you were ten?", "visual_prompt": "analog clock spinning out of control, blurring into a circle of light, time speeding up concept, cinematic dramatic lighting, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "Now, entire years vanish in a blink. It is because of how your brain processes memory. When you are a kid, everything is new, so your brain records dense, heavy memories.", "visual_prompt": "child looking in awe at a glowing floating butterfly, bright warm lighting, representing heavy dense childhood memories, highly detailed", "duration_estimate": 8},
            {"scene_number": 3, "narration": "When you are an adult, your routine is exactly the same every day. Your brain stops recording new data, making the outside world feel like it is playing on fast forward.", "visual_prompt": "split screen of an adult rushing through a blurry fast-motion city street, time perception visual, fast forward reality concept", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Subscribe to slow down time.", "visual_prompt": "person holding an hourglass that is shattered, floating sand frozen in mid-air, surreal aesthetic", "duration_estimate": 6}
        ],
        "tags": ["shorts", "time", "psychology", "aging", "brain facts", "deep thoughts", "clickbaitnt", "viral"]
    },

    # 13. Ghosts / Phantoms (Infrasound)
    {
        "topic": "Infrasound and Ghosts",
        "category": "science",
        "title": "Why You Feel Someone Watching You In The Dark #Shorts",
        "description": "Your brain detects low frequencies that make you feel pure dread.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Scary #Ghosts #Science",
        "script_text": "There is a scientific reason why you feel someone watching you in an empty room in the dark. Your brain is a highly sensitive antenna. Sometimes, old buildings, heavy wind, or household appliances emit a sound frequency so low that human ears cannot hear it. It is called Infrasound. But even though you can't hear it, your brain feels it. This specific frequency vibrates your eyeballs, causing you to hallucinate ghosts, and triggers a feeling of absolute, pure dread in your nervous system. There is no ghost, just a sound wave. Are you scared of the dark? Comment below.",
        "scenes": [
            {"scene_number": 1, "narration": "There is a scientific reason why you feel someone watching you in an empty room in the dark. Your brain is a highly sensitive antenna.", "visual_prompt": "person standing alone in a dark empty room, glowing faint red electromagnetic ripples emitting from their head into the darkness, scary concept, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "Sometimes, old buildings, heavy wind, or household appliances emit a sound frequency so low that human ears cannot hear it. It is called Infrasound. But even though you can't hear it, your brain feels it.", "visual_prompt": "invisible glowing sound waves bouncing off the walls of a creepy old house, hitting a person's head, auditory science visual, moody lighting", "duration_estimate": 9},
            {"scene_number": 3, "narration": "This specific frequency vibrates your eyeballs, causing you to hallucinate ghosts, and triggers a feeling of absolute, pure dread in your nervous system. There is no ghost, just a sound wave.", "visual_prompt": "dark shadowy figure forming out of static TV noise in the corner of a dark bedroom, psychological horror, cinematic thriller lighting", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Are you scared of the dark? Comment below.", "visual_prompt": "person pulling blanket over their head with glowing terrified eyes peeking out in pitch black darkness", "duration_estimate": 6}
        ],
        "tags": ["shorts", "scary", "ghosts", "science", "parallel dimensions", "creepy", "clickbaitnt", "viral"]
    },

    # 14. Dopamine Loop
    {
        "topic": "Short Form Content Addiction",
        "category": "psychology",
        "title": "You Are Trapped In A Matrix Loop Right Now #Shorts",
        "description": "Scrolling short videos is exactly like pulling a slot machine.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #Addiction #Psychology #Brainrot",
        "script_text": "You are actively trapped in a psychological Matrix loop right now. Short form videos are mathematically engineered by psychologists to hijack your brain. The algorithm acts exactly like a casino slot machine. Every time you swipe, the unpredictable content gives you a massive, addictive hit of dopamine. Your attention span is literally being harvested by billionaires for profit, and your brain is being trained to lose focus on real life. The only way to win the game is to break the loop. Close the app. But before you escape the matrix, comment below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "You are actively trapped in a psychological Matrix loop right now. Short form videos are mathematically engineered by psychologists to hijack your brain.", "visual_prompt": "person staring zombie-like into a glowing smartphone screen, their eyes reflecting glowing casino slot machine reels spinning, addiction concept, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "The algorithm acts exactly like a casino slot machine. Every time you swipe, the unpredictable content gives you a massive, addictive hit of dopamine.", "visual_prompt": "glowing digital brain trapped inside a glass hourglass, digital coins falling out of it, corporate harvesting attention aesthetic, cyberpunk lighting", "duration_estimate": 8},
            {"scene_number": 3, "narration": "Your attention span is literally being harvested by billionaires for profit, and your brain is being trained to lose focus on real life. The only way to win the game is to break the loop.", "visual_prompt": "puppet strings made of glowing neon code attached to a person's hands as they scroll a phone, matrix control concept, dark background", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Close the app. But before you escape the matrix, comment below and follow ClickBaitnt.", "visual_prompt": "finger aggressively pressing a red glowing exit button, breaking digital glass, escaping the matrix concept", "duration_estimate": 7}
        ],
        "tags": ["shorts", "dopamine", "addiction", "brainrot", "psychology", "matrix", "social media", "clickbaitnt", "viral"]
    },

    # 15. Dead Internet Theory
    {
        "topic": "Dead Internet Theory",
        "category": "tech",
        "title": "Everyone In The Comments Is A Fake AI Bot #Shorts",
        "description": "The internet is mostly just bots talking to other bots.\n\nSubscribe to @ClickBaitn't!\n#Shorts #ClickBaitnt #DeadInternet #AI #Creepy",
        "script_text": "Half the comments on this video are entirely fake. The Dead Internet Theory is a terrifying concept that suggests humans abandoned the internet years ago. Now, bots have completely taken over. Most of the viral posts, angry arguments, and funny memes you see online are just advanced AI programs talking to other AI programs to manipulate the algorithm and keep you scrolling. You are likely arguing with computer code every single day. The internet is a ghost town. Prove you are a real human being in the comments below and follow ClickBaitnt.",
        "scenes": [
            {"scene_number": 1, "narration": "Half the comments on this video are entirely fake. The Dead Internet Theory is a terrifying concept that suggests humans abandoned the internet years ago.", "visual_prompt": "social media comment section visualization where all the profile pictures dissolve into identical glowing robotic skulls, creepy internet concept, 8k", "duration_estimate": 8},
            {"scene_number": 2, "narration": "Now, bots have completely taken over. Most of the viral posts, angry arguments, and funny memes you see online are just advanced AI programs...", "visual_prompt": "two high-tech AI robots furiously typing on keyboards arguing with each other in a dark server room, dead internet reality, cinematic", "duration_estimate": 8},
            {"scene_number": 3, "narration": "...talking to other AI programs to manipulate the algorithm and keep you scrolling. You are likely arguing with computer code every single day. The internet is a ghost town.", "visual_prompt": "vast empty glowing digital neon landscape, a digital ghost town with wind blowing through empty server racks, cyberpunk mystery, 8k", "duration_estimate": 8},
            {"scene_number": 4, "narration": "Prove you are a real human being in the comments below and follow ClickBaitnt.", "visual_prompt": "glowing neon CAPTCHA box that says 'I AM HUMAN' hovering over a dark keyboard, hacker aesthetic", "duration_estimate": 6}
        ],
        "tags": ["shorts", "dead internet theory", "ai bots", "tech trend", "creepy", "cyber security", "clickbaitnt", "viral"]
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
            trend_source = "batch_brainrot_normal_15",
            trend_score  = 100.0,
        )
        record.video_file  = str(video_path)
        record.youtube_url = youtube_url
        record.status      = "Posted & Live"
        record.notes       = f"batch_brainrot_normal_15.py — {script['topic']}"
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
    print("  AUTO-SHORTS-ENGINE — Full Length Brainrot Batch (15 Shorts)")
    print(f"  Uploading {len(SCRIPTS)} videos as PUBLIC")
    print("=" * W)

    results = []

    for idx, script in enumerate(SCRIPTS, start=1):
        short_title = script["title"][:55] + ("..." if len(script["title"]) > 55 else "")
        video_id    = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_rot_full{idx}"

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

        # 45-second delay between uploads (skip on the last one)
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