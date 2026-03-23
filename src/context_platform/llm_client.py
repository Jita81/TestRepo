"""Shared LLM access for decision agents, meeting extraction, and future tools.

One configuration surface: same API process, model of your choice (OpenAI-compatible).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def llm_configured() -> bool:
    return bool((os.environ.get("OPENAI_API_KEY") or "").strip())


def resolve_llm_model() -> str:
    return (
        (os.environ.get("CONTEXT_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini")
    ).strip()


def resolve_base_url() -> Optional[str]:
    u = (os.environ.get("CONTEXT_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "").strip()
    return u or None


def chat_json(
    system: str,
    user: str,
    *,
    temperature: float = 0.2,
    max_user_chars: int = 96_000,
) -> tuple[Optional[dict[str, Any]], Optional[str], str]:
    """
    Single chat completion with JSON response.

    Returns ``(parsed_dict, error_message, model_id)``.
    ``parsed_dict`` is None on skip, import failure, API error, or invalid JSON.
    """
    if not llm_configured():
        return None, "no_api_key", resolve_llm_model()

    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed; LLM call skipped")
        return None, "openai_not_installed", resolve_llm_model()

    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    model = resolve_llm_model()
    kwargs: dict[str, Any] = {"api_key": key}
    base = resolve_base_url()
    if base:
        kwargs["base_url"] = base
    client = OpenAI(**kwargs)

    payload = user if len(user) <= max_user_chars else user[:max_user_chars]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": payload},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None, "response_not_object", model
        return data, None, model
    except Exception as e:
        logger.warning("llm_chat_json_failed: %s", e)
        return None, str(e)[:500], model
