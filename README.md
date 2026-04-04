# ClickBaitnt-Engine

> **The automation engine behind [@ClickBaitn't](https://www.youtube.com/@ClickBaitnt)** — a fully autonomous AI pipeline that discovers trending topics, writes scripts, generates voice, assembles videos, and uploads directly to YouTube. Zero manual work per video.

---

## What It Does

ClickBaitnt-Engine runs a **12-stage pipeline** end-to-end, fully unattended:

```
Trend Discovery  →  Script Generation  →  Script Validation
       ↓
Voice Synthesis  →  Audio Processing  →  Whisper Alignment
       ↓
Image Generation →  Video Assembly    →  Video Validation
       ↓
YouTube Upload   →  Excel Tracker     →  Cleanup & Archive
```

Scheduled to run 3 videos/day at set intervals — wake up to a channel that posted while you slept.

---

## Features

- **Trend Discovery** — pulls live trends from Google Trends, NewsAPI, and Reddit; scores and filters by niche
- **AI Scriptwriting** — Gemini generates punchy 45-second narrations with hooks, facts, and a CTA
- **Voice Synthesis** — ElevenLabs TTS with Edge-TTS as a free fallback
- **Word-Level Subtitles** — Whisper aligns every word to the audio; animated highlight subtitles burned in
- **Visual Generation** — Stability AI images per scene; Pexels as a free fallback
- **Brain Rot Split-Screen** — optional bottom panel with satisfying clips (parkour, ASMR, sand cutting) for retention
- **Auto Upload** — full YouTube Data API v3 integration with OAuth, title, description, tags, and hashtags
- **Excel Tracker** — every video logged with topic, trend score, YouTube URL, and views
- **Daily Scheduler** — runs at a configured IST hour, posts N videos with configurable intervals

---

## The Channel

All videos produced by this engine are published to:

**[youtube.com/@ClickBaitnt](https://www.youtube.com/@ClickBaitnt)**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Script Generation | Google Gemini (`gemini-2.0-flash`) |
| Voice | ElevenLabs API / Edge-TTS (fallback) |
| Subtitles | OpenAI Whisper (runs locally) |
| Images | Stability AI REST API / Pexels (fallback) |
| Video Assembly | MoviePy 2.x + FFmpeg |
| Trend Sources | Google Trends · NewsAPI · Reddit (PRAW) |
| Upload | YouTube Data API v3 (OAuth 2.0) |
| Tracking | openpyxl (Excel) |
| Scheduler | APScheduler + custom sequential runner |

---

## Requirements

- Python 3.10+
- FFmpeg installed and on PATH
- API keys (see Setup below)

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/KunalBhargava182/ClickBaitnt-Engine.git
cd ClickBaitnt-Engine
pip install -r requirements.txt
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

| Variable | Where to get it |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) |
| `STABILITY_API_KEY` | [platform.stability.ai](https://platform.stability.ai) |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org) |
| `REDDIT_CLIENT_ID` / `SECRET` | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| `YOUTUBE_CLIENT_ID` / `SECRET` | [Google Cloud Console](https://console.cloud.google.com) |

**3. YouTube OAuth**

- Go to [Google Cloud Console](https://console.cloud.google.com) → Create a project → Enable **YouTube Data API v3**
- Create OAuth 2.0 credentials → Download as `client_secrets.json`
- Place it at `data/client_secrets.json`
- On first run the browser will open for auth; a token is saved automatically after that

**4. (Optional) Brain Rot clips**

For split-screen mode, add background clips to `assets/brain_rot_clips/`. The engine fetches these automatically via Pexels on first use if the folder is empty.

---

## Usage

```bash
# Run one video immediately
python main.py --run-now

# Run with a specific topic (skip trend discovery)
python main.py --run-now --topic "The black hole that shouldn't exist"

# Full pipeline test — no upload, prints stage-by-stage report
python main.py --test

# Run today's full batch right now (3 videos, spaced by interval)
python main.py --run-batch

# Start the daily scheduler (runs forever, 3 videos/day at 9am IST)
python main.py --schedule

# Dry run — full pipeline but skip upload and tracker
python main.py --run-now --dry-run

# Enable split-screen brain rot mode for one run
python main.py --run-now --splitscreen
```

---

## Configuration

All behaviour is controlled via `config.yaml` — no code changes needed:

```yaml
scheduler:
  videos_per_day: 3
  post_interval_hours: 5      # 9am / 2pm / 7pm
  daily_start_hour: 9

script:
  target_duration_seconds: 45
  tone: "energetic_casual"

voice:
  provider: "elevenlabs"      # or "edge_tts"

subtitles:
  style: "word_highlight"
  font: "Montserrat-Bold"
  colors:
    active_word: "#FFFF00"
    inactive_word: "#FFFFFF"
```

---

## Batch Scripts

Standalone scripts for specific video formats, runnable independently:

| Script | Format |
|---|---|
| `batch_trending_4.py` | 4-video trending batch |
| `batch_trending_10.py` | 10-video trending batch |
| `batch_brainrot_normal_15.py` | 15-video brain rot batch |
| `batch_viral_11.py` | 11-video viral format |
| `batch_reddit_story_3parts.py` | Reddit story (3 parts) |
| `batch_kunafa_trend.py` | Niche trend batch |
| `single_aphantasia_short.py` | Single aphantasia-style short |

---

## Project Structure

```
ClickBaitnt-Engine/
├── main.py                    # Entry point
├── config.yaml                # All settings
├── requirements.txt
├── .env.example               # API key template
│
├── src/
│   ├── script_engine/         # Gemini scriptwriting + validation
│   ├── trend_discovery/       # Google Trends, NewsAPI, Reddit
│   ├── voice/                 # TTS + audio processing
│   ├── subtitles/             # Whisper alignment + renderer
│   ├── visuals/               # Image generation + motion engine
│   ├── video/                 # Video composer + validator
│   ├── upload/                # YouTube OAuth + uploader
│   ├── tracker/               # Excel tracker
│   └── utils/                 # Config, logger, retry, cleanup
│
├── tests/                     # Unit + integration tests
└── assets/
    ├── fonts/                 # Subtitle fonts
    ├── overlays/              # Overlay graphics
    └── brain_rot_clips/       # Split-screen background clips
```

---

## License

All rights reserved. This codebase is the intellectual property of the author.

---

If you like this project — like, share, and subscribe to **[@ClickBaitn't](https://www.youtube.com/@ClickBaitnt)** on YouTube.
