"""Stub manufacturing pipeline (H1) — simulates async job without external systems."""

from __future__ import annotations

import logging
import time

from src.context_platform.schemas import ManufacturingStatus
from src.context_platform.store import get_store

logger = logging.getLogger(__name__)


def run_stub_manufacturing_job(request_id: str) -> None:
    """
    queued → running → awaiting_triage (success) or failed.
    Replace with real codegen / CI integration later.
    """

    store = get_store()
    try:
        store.update_manufacturing_status(
            request_id,
            ManufacturingStatus.running,
            started=True,
        )
        # Simulate work
        time.sleep(1.6)
        m = store.get_manufacturing_row(request_id)
        pid = m["context_package_id"]
        h = (m["package_content_hash"] or "")[:12]
        summary = (
            f"Stub manufacturing finished for context package {pid[:8]}… "
            f"(pinned hash {h}…). No code was generated — adapter placeholder."
        )
        store.update_manufacturing_status(
            request_id,
            ManufacturingStatus.awaiting_triage,
            finished=True,
            output_summary=summary,
        )
    except Exception as e:
        logger.exception("manufacturing_stub_failed")
        try:
            store.update_manufacturing_status(
                request_id,
                ManufacturingStatus.failed,
                finished=True,
                error_message=str(e),
            )
        except Exception:
            pass
