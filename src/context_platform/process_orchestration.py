"""Phase 9 — env-driven process rules (quick-path eligibility, helpers)."""

from __future__ import annotations

import os
from typing import Any, Optional


def env_float_optional(name: str) -> Optional[float]:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def quick_path_min_readiness_threshold() -> Optional[float]:
    """Unset = feature off. Typical: 90–95."""

    return env_float_optional("CONTEXT_PROCESS_QUICK_PATH_MIN_READINESS")


def package_qualifies_quick_path(
    readiness: float, gap_analysis: dict[str, Any] | None
) -> bool:
    th = quick_path_min_readiness_threshold()
    if th is None:
        return False
    ga = gap_analysis if isinstance(gap_analysis, dict) else {}
    gaps = ga.get("gaps")
    if not isinstance(gaps, list):
        gaps = []
    return float(readiness) >= th and len(gaps) == 0
