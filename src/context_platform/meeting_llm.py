"""Optional OpenAI extraction for meeting transcripts (D2). Falls back via caller."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_MAX_TRANSCRIPT_CHARS = 48_000


def try_llm_extract(text: str) -> Optional[dict[str, Any]]:
    """
    If OPENAI_API_KEY is set and openai is installed, return structured extraction.
    Returns None on skip, import failure, or API/parse errors (caller uses stub).
    """

    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed; skipping LLM extraction")
        return None

    model = (os.environ.get("OPENAI_MODEL") or "gpt-4o-mini").strip()
    client = OpenAI(api_key=key)

    system = """You extract structured items from a meeting transcript for software delivery.
Return ONLY valid JSON with exactly this shape:
{"proposed_items": [{"type": "decision"|"action_item"|"requirement"|"note", "text": "string"}]}
Rules:
- decision: commitments, choices, agreed direction
- action_item: tasks; include assignee in text if mentioned
- requirement: functional or non-functional constraints
- note: other important context
- Omit empty items; keep text concise."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text[:_MAX_TRANSCRIPT_CHARS]},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
    except Exception as e:
        logger.warning("LLM extraction failed: %s", e)
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
        "extractor": f"openai:{model}",
        "proposed_items": normalized,
    }
