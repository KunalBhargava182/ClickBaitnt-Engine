"""
Phase 12: First-time setup script for auto-shorts-engine.

Run once before first use:
    python setup.py

What it does:
  1. Checks Python version (3.10+ required)
  2. Verifies all pip packages from requirements.txt are installed
  3. Creates required directory structure
  4. Writes a .env template if no .env exists
  5. Prints a quick-start checklist
"""

import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows (avoids UnicodeEncodeError in cp1252 consoles)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── constants ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
ENV_FILE     = PROJECT_ROOT / ".env"
ENV_EXAMPLE  = PROJECT_ROOT / ".env.example"

REQUIRED_DIRS = [
    "output/images",
    "output/audio",
    "output/scripts",
    "output/videos",
    "output/archive",
    "assets/fonts",
    "assets/music",
    "assets/overlays",
    "data",
    "logs",
]

ENV_TEMPLATE = """\
# ============================================================
# AUTO-SHORTS-ENGINE — Environment Variables
# Copy this file to .env and fill in the values.
# ============================================================

# ── Stability AI (image generation) ──────────────────────────
STABILITY_API_KEY=your_stability_api_key_here

# ── ElevenLabs (TTS — optional, edge-tts is the free fallback) ──
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# ── NewsAPI (trend discovery — optional) ─────────────────────
NEWSAPI_KEY=your_newsapi_key_here

# ── YouTube OAuth (download client_secrets.json from Google Cloud Console
#    and place it at data/client_secrets.json, OR set these env vars) ──
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here

# ── Reddit API (optional — pending API approval) ─────────────
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=auto-shorts-engine/1.0

# ── Gemini (free tier: 1500 RPD, no key needed for public API) ──
# GEMINI_API_KEY=your_gemini_api_key_here   # only if using paid tier
"""

# ─── helpers ─────────────────────────────────────────────────────────────────

OK   = "\033[92m[OK]\033[0m"
WARN = "\033[93m[WARN]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"


def _print(tag: str, msg: str) -> None:
    print(f"  {tag}  {msg}")


def _check_python() -> bool:
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 10):
        _print(FAIL, f"Python 3.10+ required — found {major}.{minor}")
        return False
    _print(OK, f"Python {major}.{minor}.{sys.version_info.micro}")
    return True


def _check_packages() -> bool:
    """
    Check installed distributions by their PyPI name using importlib.metadata.
    This avoids false negatives from packages that fail to import at runtime
    (e.g. pydub on Python 3.13+ where audioop was removed).
    """
    from importlib.metadata import distribution, PackageNotFoundError

    if not REQUIREMENTS.exists():
        _print(WARN, "requirements.txt not found — skipping package check")
        return True

    missing = []
    with open(REQUIREMENTS) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Extract distribution name (before ==, >=, <=, ~=)
            dist_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            # Strip inline comments
            dist_name = dist_name.split("#")[0].strip()
            if not dist_name:
                continue
            try:
                distribution(dist_name)
            except PackageNotFoundError:
                missing.append(dist_name)

    if missing:
        _print(WARN, f"Missing packages: {', '.join(missing)}")
        print()
        try:
            answer = input("      Install missing packages now? [Y/n] ").strip().lower()
        except EOFError:
            answer = "n"
        if answer in ("", "y", "yes"):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
            )
            _print(OK, "Packages installed")
        else:
            _print(WARN, "Skipped — run:  pip install -r requirements.txt")
        return False
    _print(OK, "All packages installed")
    return True


def _create_dirs() -> None:
    created = 0
    for rel in REQUIRED_DIRS:
        path = PROJECT_ROOT / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created += 1
    if created:
        _print(OK, f"Created {created} director{'ies' if created != 1 else 'y'}")
    else:
        _print(OK, "All directories already exist")


def _write_env_template() -> None:
    # Always write/update the example file
    ENV_EXAMPLE.write_text(ENV_TEMPLATE, encoding="utf-8")
    _print(OK, f".env.example written -> {ENV_EXAMPLE.name}")

    if ENV_FILE.exists():
        _print(INFO, ".env already exists — not overwritten")
    else:
        ENV_FILE.write_text(ENV_TEMPLATE, encoding="utf-8")
        _print(OK, ".env created — fill in your API keys before running")


def _check_oauth_secrets() -> None:
    secrets_path = PROJECT_ROOT / "data" / "client_secrets.json"
    token_path   = PROJECT_ROOT / "data" / "youtube_token.json"

    if secrets_path.exists():
        _print(OK, "data/client_secrets.json found")
    else:
        _print(WARN, "data/client_secrets.json missing")
        _print(INFO, "  Download from: Google Cloud Console -> APIs & Services -> Credentials")
        _print(INFO, "  OR set YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET in .env")

    if token_path.exists():
        _print(OK, "YouTube OAuth token cached (data/youtube_token.json)")
    else:
        _print(INFO, "YouTube OAuth token not yet generated — first run will open browser")


def _print_quickstart() -> None:
    print()
    print("─" * 60)
    print("  QUICK-START CHECKLIST")
    print("─" * 60)
    steps = [
        ("1", "Fill in .env with your API keys"),
        ("2", "Add data/client_secrets.json for YouTube OAuth"),
        ("3", "Run a dry-run to verify the pipeline end-to-end:"),
        ("  ", "    python -m src.main --run-now --dry-run"),
        ("4", "Schedule 3 videos/day (09:00, 14:00, 19:00 IST):"),
        ("  ", "    python -m src.main --schedule"),
        ("5", "Run the full test suite:"),
        ("  ", "    python -m pytest tests/ -v"),
    ]
    for num, text in steps:
        print(f"  {num}. {text}" if num.strip().isdigit() else f"  {text}")
    print()
    print("  Docs: see README.md for detailed instructions")
    print("─" * 60)


# ─── main ────────────────────────────────────────────────────────────────────

def main() -> int:
    print()
    print("=" * 60)
    print("  AUTO-SHORTS-ENGINE — Setup")
    print("=" * 60)
    print()

    ok = True

    print("  Checking Python version…")
    ok = _check_python() and ok

    print()
    print("  Checking Python packages…")
    _check_packages()

    print()
    print("  Creating directory structure…")
    _create_dirs()

    print()
    print("  Writing .env template…")
    _write_env_template()

    print()
    print("  Checking YouTube credentials…")
    _check_oauth_secrets()

    _print_quickstart()
    return 0


if __name__ == "__main__":
    sys.exit(main())
