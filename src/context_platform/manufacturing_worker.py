"""Manufacturing pipeline stub (H1) — simulates work and writes a local artifact."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from src.context_platform.schemas import ManufacturingStatus
from src.context_platform.store import get_store

logger = logging.getLogger(__name__)


def _output_root() -> Path:
    return Path(
        os.environ.get("MANUFACTURING_OUTPUT_DIR", "data/manufacturing_outputs")
    )


def _write_artifact(
    request_id: str,
    package_id: str,
    content_hash: str | None,
    body_md: str,
) -> str:
    root = _output_root() / request_id
    root.mkdir(parents=True, exist_ok=True)
    path = root / "MANUFACTURING.md"
    path.write_text(body_md, encoding="utf-8")
    return str(path.resolve())


def _package_one_line_summary(store, package_id: str) -> str:
    try:
        pkg = store.get_context_package(package_id)
    except KeyError:
        return "(package not found)"
    biz = pkg.business_context
    if isinstance(biz, dict) and biz.get("summary"):
        return str(biz["summary"])[:500]
    return f"story_id={pkg.story_id}, version v{pkg.version}, readiness {pkg.readiness_score}%"


def run_stub_manufacturing_job(request_id: str) -> None:
    """
    queued → running → awaiting_triage (success) or failed.
    Writes `MANUFACTURING_OUTPUT_DIR/<request_id>/MANUFACTURING.md`.
    """

    store = get_store()
    try:
        store.update_manufacturing_status(
            request_id,
            ManufacturingStatus.running,
            started=True,
        )
        time.sleep(1.2)
        row = store.get_manufacturing_row(request_id)
        pid = row["context_package_id"]
        h = row["package_content_hash"]
        summary_line = _package_one_line_summary(store, pid)

        snap_note = ""
        try:
            pkg = store.get_context_package(pid)
            if pkg.status.value == "approved" and pkg.content_hash:
                snap_note = f"\nApproved package hash: `{pkg.content_hash}`\n"
        except KeyError:
            pass

        body = f"""# Manufacturing run (stub adapter)

| Field | Value |
|-------|-------|
| request_id | `{request_id}` |
| context_package_id | `{pid}` |
| package_content_hash | `{h or "n/a"}` |

## Business summary (from live package view)

{summary_line}
{snap_note}
## Next steps

Replace `run_stub_manufacturing_job` with your codegen / CI adapter. This file is the **accountability anchor** for what was submitted to manufacturing.
"""
        out_path = _write_artifact(request_id, pid, h, body)
        out_summary = (
            f"Stub manufacturing finished. Artifact: `{out_path}`. "
            f"Package {pid[:8]}… hash {(h or '')[:12]}…"
        )
        store.update_manufacturing_status(
            request_id,
            ManufacturingStatus.awaiting_triage,
            finished=True,
            output_summary=out_summary,
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
