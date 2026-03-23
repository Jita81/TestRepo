"""Stub meeting extraction (D2 MVP) — no LLM; pattern-based draft from transcript."""

from __future__ import annotations

import re
from typing import Any


def stub_extract_transcript(text: str) -> dict[str, Any]:
    """
    Parse lines like:
      DECISION: We will use OAuth2
      ACTION: Alice to update the diagram
      REQ: Password must be 12+ chars
    """

    items: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    patterns = (
        (re.compile(r"^DECISION:\s*(.+)$", re.I), "decision"),
        (re.compile(r"^ACTION:\s*(.+)$", re.I), "action_item"),
        (re.compile(r"^REQ(?:UIREMENT)?S?:\s*(.+)$", re.I), "requirement"),
    )
    un_patterns = (
        (re.compile(r"^UNRESOLVED:\s*(.+)$", re.I), "open_question"),
        (re.compile(r"^OPEN:\s*(.+)$", re.I), "open_question"),
        (re.compile(r"^\?\?\s*(.+)$"), "ambiguity"),
    )
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        matched = False
        for rx, kind in un_patterns:
            m = rx.match(s)
            if m:
                unresolved.append(
                    {"text": m.group(1).strip(), "kind": kind}
                )
                matched = True
                break
        if matched:
            continue
        for rx, kind in patterns:
            m = rx.match(s)
            if m:
                items.append({"type": kind, "text": m.group(1).strip()})
                matched = True
                break
        if not matched and s.startswith("-"):
            items.append({"type": "note", "text": s.lstrip("- ").strip()})

    if not items:
        items.append(
            {
                "type": "meta",
                "text": "No DECISION:/ACTION:/REQ: lines found. Add those prefixes per line for structured extraction.",
            }
        )

    return {
        "extractor": "stub_v2",
        "proposed_items": items,
        "unresolved": unresolved,
    }


def extract_transcript_auto(text: str) -> dict[str, Any]:
    """Use OpenAI when `OPENAI_API_KEY` + `openai` package; else pattern stub."""

    from src.context_platform.meeting_llm import try_llm_extract

    llm = try_llm_extract(text)
    if llm is not None:
        return llm
    return stub_extract_transcript(text)
