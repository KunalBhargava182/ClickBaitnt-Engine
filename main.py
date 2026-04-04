"""
Root-level entry point for auto-shorts-engine.

Allows running from the project directory without the -m flag:
    python main.py --test
    python main.py --run-now --dry-run
    python main.py --schedule
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src` resolves correctly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
