"""
Shared Google Gemini client using the official google-genai SDK.

Free tier limits:
  - gemini-2.0-flash      : 15 RPM, 1 500 RPD, 1 000 000 tokens/day
  - gemini-2.0-flash-lite : 30 RPM, 1 500 RPD, 1 000 000 tokens/day  (fallback)

Usage:
    from src.utils.gemini_client import call_gemini_json, call_gemini_text
"""

import json
import os
import re
import time
from typing import Any

from google import genai
from google.genai import types

from src.utils.logger import log

# Model names — both free tier
_PRIMARY_MODEL = "gemini-2.0-flash"
_FALLBACK_MODEL = "gemini-2.0-flash-lite"   # lighter model, confirmed available

# Rate-limit guard: free tier = 15 RPM → 4 s minimum between calls
_MIN_CALL_INTERVAL = 4.0
# On 429 RESOURCE_EXHAUSTED, wait this long before one retry
_RATE_LIMIT_WAIT = 65.0

_last_call_ts: float = 0.0
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Return a cached Gemini client, initialised from GEMINI_API_KEY."""
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise ValueError(
                "GEMINI_API_KEY not set. "
                "Get a free key at https://aistudio.google.com/apikey and add it to .env"
            )
        _client = genai.Client(api_key=key)
    return _client


def _rate_limit() -> None:
    """Sleep just enough to respect 15 RPM."""
    global _last_call_ts
    elapsed = time.time() - _last_call_ts
    if elapsed < _MIN_CALL_INTERVAL:
        time.sleep(_MIN_CALL_INTERVAL - elapsed)
    _last_call_ts = time.time()


def _strip_fences(text: str) -> str:
    """Remove markdown code fences that some responses include."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _is_rate_limit(exc: Exception) -> bool:
    """True if the exception indicates a 429 rate-limit response."""
    s = str(exc)
    return "429" in s or "RESOURCE_EXHAUSTED" in s


def _generate(client: genai.Client, model_name: str, cfg: types.GenerateContentConfig, prompt: str) -> str:
    """Single generate_content call, returns response text."""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=cfg,
    )
    return response.text


def call_gemini_json(
    prompt: str,
    temperature: float = 0.85,
    max_tokens: int = 1500,
    model: str = _PRIMARY_MODEL,
) -> dict[str, Any]:
    """
    Send a prompt to Gemini and return the parsed JSON response.

    Strategy:
      - Try primary model.
      - On 429: wait _RATE_LIMIT_WAIT seconds, retry same model once.
      - On other failure: try fallback model.
      - Raise RuntimeError if all attempts fail.

    Args:
        prompt: Combined system + user prompt string.
        temperature: 0.0–1.0.
        max_tokens: Max output tokens.
        model: Primary model name.

    Returns:
        Parsed JSON dict.

    Raises:
        ValueError: Unparseable JSON in response.
        RuntimeError: All models/retries failed.
    """
    client = _get_client()
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    models = [model]
    if _FALLBACK_MODEL != model:
        models.append(_FALLBACK_MODEL)

    for idx, model_name in enumerate(models):
        _rate_limit()
        log.info("gemini_client.call_json", model=model_name)

        try:
            raw = _generate(client, model_name, cfg, prompt)
            return json.loads(_strip_fences(raw))

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini ({model_name}) returned invalid JSON: {exc}"
            ) from exc

        except Exception as exc:
            log.warning("gemini_client.call_json.failed", model=model_name, error=str(exc))

            if _is_rate_limit(exc):
                log.warning("gemini_client.rate_limited", wait_s=_RATE_LIMIT_WAIT)
                time.sleep(_RATE_LIMIT_WAIT)
                # One retry on same model after waiting
                try:
                    _rate_limit()
                    raw = _generate(client, model_name, cfg, prompt)
                    return json.loads(_strip_fences(raw))
                except json.JSONDecodeError as jexc:
                    raise ValueError(f"Gemini invalid JSON after rate-limit retry: {jexc}") from jexc
                except Exception:
                    pass  # Fall through to next model

            if idx == len(models) - 1:
                raise RuntimeError(
                    f"Gemini call_json failed on all models. Last: {exc}"
                ) from exc

    raise RuntimeError("Gemini call_json: exhausted all models")


def call_gemini_text(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 300,
    model: str = _PRIMARY_MODEL,
) -> str:
    """
    Send a prompt to Gemini and return plain-text response.

    Args:
        prompt: Full prompt string.
        temperature: 0.0–1.0.
        max_tokens: Max output tokens.
        model: Primary model name.

    Returns:
        Response text string.

    Raises:
        RuntimeError: All models/retries failed.
    """
    client = _get_client()
    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    models = [model]
    if _FALLBACK_MODEL != model:
        models.append(_FALLBACK_MODEL)

    for idx, model_name in enumerate(models):
        _rate_limit()
        log.info("gemini_client.call_text", model=model_name)

        try:
            return _generate(client, model_name, cfg, prompt).strip()

        except Exception as exc:
            log.warning("gemini_client.call_text.failed", model=model_name, error=str(exc))

            if _is_rate_limit(exc):
                log.warning("gemini_client.rate_limited", wait_s=_RATE_LIMIT_WAIT)
                time.sleep(_RATE_LIMIT_WAIT)
                try:
                    _rate_limit()
                    return _generate(client, model_name, cfg, prompt).strip()
                except Exception:
                    pass

            if idx == len(models) - 1:
                raise RuntimeError(f"Gemini call_text failed on all models. Last: {exc}") from exc

    raise RuntimeError("Gemini call_text: exhausted all models")
