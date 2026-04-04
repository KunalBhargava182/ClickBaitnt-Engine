"""
Central config loader.
Reads config.yaml + loads .env into os.environ.
Returns a nested dict accessible via dot-notation (AppConfig).
"""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


# Project root = directory containing this file's grandparent (src/utils/../../)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_env(env_path: Path | None = None) -> None:
    """Load .env into os.environ. Safe to call multiple times."""
    if env_path is None:
        env_path = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path=env_path, override=False)


def _load_yaml(config_path: Path | None = None) -> dict[str, Any]:
    """Read config.yaml and return as dict."""
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class _DotDict(dict):
    """Dict subclass that allows attribute access: cfg.scheduler.timezone."""

    def __getattr__(self, name: str) -> Any:
        try:
            val = self[name]
        except KeyError:
            raise AttributeError(f"Config key '{name}' not found") from None
        if isinstance(val, dict):
            return _DotDict(val)
        return val

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class AppConfig(_DotDict):
    """
    Top-level config object.

    Usage:
        from src.utils.config_loader import get_config
        cfg = get_config()
        print(cfg.scheduler.timezone)        # "Asia/Kolkata"
        print(cfg.trends.min_trend_score)    # 60
    """


_config_cache: AppConfig | None = None


def get_config(reload: bool = False) -> AppConfig:
    """
    Return the singleton AppConfig.

    Args:
        reload: Force re-read from disk (useful in tests).

    Returns:
        AppConfig instance populated from config.yaml.
    """
    global _config_cache
    if _config_cache is None or reload:
        _load_env()
        raw = _load_yaml()
        _config_cache = AppConfig(raw)
    return _config_cache


def get_project_root() -> Path:
    """Return the project root directory as a Path."""
    return PROJECT_ROOT
