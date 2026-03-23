"""EA Phase 8 — normalized meeting extraction draft (subset schema + helpers)."""

from __future__ import annotations

from typing import Any

EXTRACTION_SCHEMA_VERSION = 2


def normalize_extraction_draft(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Coerce any legacy extractor output into the v2 shape:
    - ``proposed_items``: {type, text}[]
    - ``unresolved``: {text, kind}[]
    - ``extraction_schema_version``: int
    Preserves ``extractor``, ``item_reviews``, ``confirmed_items``, etc.
    """

    out = dict(raw)
    ver = out.get("extraction_schema_version")
    try:
        out["extraction_schema_version"] = int(ver) if ver is not None else EXTRACTION_SCHEMA_VERSION
    except (TypeError, ValueError):
        out["extraction_schema_version"] = EXTRACTION_SCHEMA_VERSION

    items = out.get("proposed_items")
    if not isinstance(items, list):
        items = []
    norm_items: list[dict[str, str]] = []
    for it in items:
        if isinstance(it, dict):
            t = (it.get("text") or "").strip()
            if not t:
                continue
            norm_items.append(
                {
                    "type": str(it.get("type", "note"))[:64],
                    "text": t[:4000],
                }
            )
    out["proposed_items"] = norm_items

    un = out.get("unresolved")
    if not isinstance(un, list):
        un = []
    norm_un: list[dict[str, str]] = []
    for u in un:
        if isinstance(u, str) and u.strip():
            norm_un.append(
                {"text": u.strip()[:4000], "kind": "open_question"}
            )
        elif isinstance(u, dict):
            tx = (u.get("text") or "").strip()
            if not tx:
                continue
            norm_un.append(
                {
                    "text": tx[:4000],
                    "kind": str(u.get("kind", "open_question"))[:64],
                }
            )
    out["unresolved"] = norm_un
    return out


def summarize_meeting_extraction_draft(draft: dict[str, Any]) -> dict[str, Any]:
    """Counts for dashboards and ``pending-extraction-confirmation`` API."""

    items = draft.get("proposed_items") or []
    if not isinstance(items, list):
        items = []
    rev = draft.get("item_reviews") or {}
    if not isinstance(rev, dict):
        rev = {}
    pending = 0
    for i in range(len(items)):
        if rev.get(str(i), "pending") == "pending":
            pending += 1
    un = draft.get("unresolved") or []
    if not isinstance(un, list):
        un = []
    return {
        "extraction_schema_version": draft.get("extraction_schema_version", 1),
        "n_proposed": len(items),
        "n_unresolved": len(un),
        "n_pending_item_reviews": pending,
    }
