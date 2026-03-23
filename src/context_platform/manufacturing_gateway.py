"""
Phase 10 — Manufacturing gateway: structured prompt bundle for codegen / LLM / CI.

Produces a stable JSON-shaped document plus canonical Markdown for embedding in
`MANUFACTURING.md` or external tools. Includes an optional **triage queue** heuristic
for prediction vs actual D10 outcomes (see `predict_triage_queue_heuristic`).
"""

from __future__ import annotations

import json
from typing import Any, Optional

from src.context_platform.schemas import ContextPackageRead

GATEWAY_BUNDLE_VERSION = "1.0"


def predict_triage_queue_heuristic(pkg: ContextPackageRead) -> Optional[str]:
    """
    Lightweight guess for D10 queue (not ML). Used when
    ``CONTEXT_MANUFACTURING_AUTO_PREDICT_TRIAGE`` is set or for analytics.

    - Structural **gaps** present → ``Q2`` (context gaps to address)
    - Readiness **< 55** → ``Q3`` (likely deeper issue)
    - Readiness **≥ 75** and no structural gaps → ``Q1`` (ship / minor notes)
    - Otherwise → ``None`` (no prediction)
    """

    ga = pkg.gap_analysis if isinstance(pkg.gap_analysis, dict) else {}
    gaps = ga.get("gaps")
    if isinstance(gaps, list) and len(gaps) > 0:
        return "Q2"
    try:
        r = float(pkg.readiness_score)
    except (TypeError, ValueError):
        r = 0.0
    if r < 55.0:
        return "Q3"
    if r >= 75.0:
        return "Q1"
    return None


def build_manufacturing_prompt_bundle(
    pkg: ContextPackageRead,
    *,
    story_title: str = "",
    manufacturing_request_id: str = "",
) -> dict[str, Any]:
    """Structured snapshot for manufacturing consumers (deterministic JSON)."""

    return {
        "gateway_version": GATEWAY_BUNDLE_VERSION,
        "context_package_id": pkg.id,
        "story_id": pkg.story_id,
        "story_title": (story_title or "").strip(),
        "package_version": pkg.version,
        "package_status": pkg.status.value,
        "readiness_score": float(pkg.readiness_score),
        "package_content_hash": pkg.content_hash,
        "package_schema_version": pkg.package_schema_version,
        "business_context": pkg.business_context,
        "technical_approach": pkg.technical_approach,
        "testing_contract": pkg.testing_contract,
        "success_patterns": pkg.success_patterns,
        "risks_and_dependencies": pkg.risks_and_dependencies,
        "section_provenance": pkg.section_provenance,
        "gap_analysis": pkg.gap_analysis,
        "predicted_triage_queue_hint": predict_triage_queue_heuristic(pkg),
        "manufacturing_request_id": manufacturing_request_id or None,
    }


def format_manufacturing_prompt_markdown(bundle: dict[str, Any]) -> str:
    """
    Canonical Markdown layout for tests and for embedding in manufacturing artifacts.
    Uses sorted keys only inside JSON blocks where noted for stability.
    """

    def _json_block(obj: Any) -> str:
        return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)

    lines = [
        "# Manufacturing gateway (Phase 10)",
        "",
        f"Bundle version: `{bundle.get('gateway_version', '?')}`",
        "",
        "## Package metadata",
        "",
        f"- **context_package_id:** `{bundle.get('context_package_id', '')}`",
        f"- **story_id:** `{bundle.get('story_id', '')}`",
        f"- **story_title:** {bundle.get('story_title') or '*(none)*'}",
        f"- **package_version:** {bundle.get('package_version', '')}",
        f"- **package_status:** `{bundle.get('package_status', '')}`",
        f"- **readiness_score:** {bundle.get('readiness_score', '')}",
        f"- **package_content_hash:** `{bundle.get('package_content_hash') or 'n/a'}`",
        f"- **predicted_triage_queue_hint:** `{bundle.get('predicted_triage_queue_hint') or 'n/a'}`",
        "",
        "## business_context",
        "",
        "```json",
        _json_block(bundle.get("business_context") or {}),
        "```",
        "",
        "## technical_approach",
        "",
        "```json",
        _json_block(bundle.get("technical_approach") or {}),
        "```",
        "",
        "## testing_contract",
        "",
        "```json",
        _json_block(bundle.get("testing_contract") or {}),
        "```",
        "",
        "## success_patterns",
        "",
        "```json",
        _json_block(bundle.get("success_patterns") or {}),
        "```",
        "",
        "## risks_and_dependencies",
        "",
        "```json",
        _json_block(bundle.get("risks_and_dependencies") or {}),
        "```",
        "",
        "## section_provenance",
        "",
        "```json",
        _json_block(bundle.get("section_provenance") or {}),
        "```",
        "",
        "## gap_analysis",
        "",
        "```json",
        _json_block(bundle.get("gap_analysis") or {}),
        "```",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
