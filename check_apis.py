"""
API Health Check — tests every configured API with a minimal live call.
Run: python check_apis.py
"""

import os
import sys
import json
import time

# Force UTF-8 output so emoji don't crash Windows terminal
sys.stdout.reconfigure(encoding="utf-8")

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

results = {}


def check(name, fn):
    try:
        msg = fn()
        results[name] = (PASS, msg)
        print(f"{PASS}  {name}: {msg}")
    except Exception as e:
        results[name] = (FAIL, str(e)[:120])
        print(f"{FAIL}  {name}: {str(e)[:120]}")


# ── 1. Gemini ────────────────────────────────────────────────────────────────
def test_gemini():
    import requests
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    # Use REST endpoint to avoid the deprecated google.generativeai package
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    models = [m["name"] for m in r.json().get("models", [])]
    return f"key valid, {len(models)} models accessible"

# ── 2. Pexels ────────────────────────────────────────────────────────────────
def test_pexels():
    import requests
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        raise ValueError("PEXELS_API_KEY not set")
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": key},
        params={"query": "nature", "per_page": 1},
        timeout=10,
    )
    r.raise_for_status()
    total = r.json().get("total_results", 0)
    return f"total_results={total}"

# ── 3. NewsAPI ───────────────────────────────────────────────────────────────
def test_newsapi():
    import requests
    key = os.environ.get("NEWSAPI_KEY", "")
    if not key:
        raise ValueError("NEWSAPI_KEY not set")
    r = requests.get(
        "https://newsapi.org/v2/top-headlines",
        params={"apiKey": key, "country": "us", "pageSize": 1},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "ok":
        raise ValueError(data.get("message", "unknown error"))
    return f"status=ok articles={data.get('totalResults', 0)}"

# ── 4. Stability AI ──────────────────────────────────────────────────────────
def test_stability():
    import requests
    key = os.environ.get("STABILITY_API_KEY", "")
    if not key or key.startswith("sk-xx"):
        raise ValueError("STABILITY_API_KEY not set")
    r = requests.get(
        "https://api.stability.ai/v1/user/account",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    credits = data.get("credits", "?")
    return f"account ok, credits={credits}"

# ── 5. ElevenLabs ────────────────────────────────────────────────────────────
def test_elevenlabs():
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key or key.startswith("sk_xxx"):
        raise ValueError("ELEVENLABS_API_KEY not set")
    r = requests.get(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": key},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    tier = data.get("subscription", {}).get("tier", "unknown")
    chars = data.get("subscription", {}).get("character_count", "?")
    return f"tier={tier} chars_used={chars}"

# ── 6. Reddit ────────────────────────────────────────────────────────────────
def test_reddit():
    import requests
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "auto-shorts-engine/1.0")
    if "PASTE_YOUR" in client_id or not client_id:
        raise ValueError("Reddit credentials not configured (placeholder values)")
    r = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": user_agent},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise ValueError(data["error"])
    return f"token_type={data.get('token_type')} scope={data.get('scope')}"

# ── 7. OpenAI ────────────────────────────────────────────────────────────────
def test_openai():
    import requests
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key.startswith("sk-proj-xx"):
        raise ValueError("OPENAI_API_KEY not set")
    r = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10,
    )
    r.raise_for_status()
    models = r.json().get("data", [])
    return f"accessible models={len(models)}"

# ── 8. YouTube OAuth token ───────────────────────────────────────────────────
def test_youtube():
    token_path = os.path.join(os.path.dirname(__file__), "data", "youtube_token.json")
    if not os.path.exists(token_path):
        raise FileNotFoundError("data/youtube_token.json not found — run OAuth flow first")
    with open(token_path) as f:
        token = json.load(f)
    import requests
    access_token = token.get("token") or token.get("access_token", "")
    if not access_token:
        raise ValueError("No access_token in youtube_token.json")
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"part": "snippet", "mine": "true"},
        timeout=10,
    )
    if r.status_code == 401:
        raise ValueError("Token expired — will auto-refresh on next upload run")
    r.raise_for_status()
    items = r.json().get("items", [])
    channel = items[0]["snippet"]["title"] if items else "unknown"
    return f"channel='{channel}'"


# ── Run all checks ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  API HEALTH CHECK")
print("="*60 + "\n")

check("Gemini",      test_gemini)
check("Pexels",      test_pexels)
check("NewsAPI",     test_newsapi)
check("Stability AI",test_stability)
check("ElevenLabs",  test_elevenlabs)
check("Reddit",      test_reddit)
check("OpenAI",      test_openai)
check("YouTube",     test_youtube)

print("\n" + "="*60)
working = sum(1 for s, _ in results.values() if s == PASS)
print(f"  {working}/{len(results)} APIs working")
print("="*60 + "\n")
