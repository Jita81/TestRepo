"""Optional OpenAI extraction for meeting transcripts (D4/D2 pipeline). Falls back via caller."""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.context_platform.llm_client import chat_json, llm_configured

logger = logging.getLogger(__name__)

_MAX_TRANSCRIPT_CHARS = 48_000


def try_llm_extract(text: str) -> Optional[dict[str, Any]]:
    """
    If OPENAI_API_KEY is set and openai is installed, return structured extraction.
    Returns None on skip, import failure, or API/parse errors (caller uses stub).
    Uses the shared :mod:`llm_client` (``CONTEXT_LLM_MODEL`` / ``OPENAI_MODEL``).
    """

    if not llm_configured():
        return None

    system = """You extract structured items from a meeting transcript for software delivery.
Return ONLY valid JSON with exactly this shape:
{"proposed_items": [{"type": "decision"|"action_item"|"requirement"|"note", "text": "string"}]}
Rules:
- decision: commitments, choices, agreed direction
- action_item: tasks; include assignee in text if mentioned
- requirement: functional or non-functional constraints
- note: other important context
- Omit empty items; keep text concise."""

    data, err, model = chat_json(system, text[:_MAX_TRANSCRIPT_CHARS], temperature=0.2)
    if err or data is None:
        if err and err not in ("no_api_key", "openai_not_installed"):
            logger.warning("LLM extraction failed: %s", err)
        return None

    items = data.get("proposed_items")
    if not isinstance(items, list) or not items:
        return None

    normalized: list[dict[str, str]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        t = it.get("text")
        if not t or not str(t).strip():
            continue
        normalized.append(
            {
                "type": str(it.get("type", "note"))[:64],
                "text": str(t).strip()[:4000],
            }
        )

    if not normalized:
        return None

    return {
        "extractor": f"llm:{model}",
        "proposed_items": normalized,
    }
