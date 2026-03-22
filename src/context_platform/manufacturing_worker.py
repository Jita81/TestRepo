"""Manufacturing pipeline (H1 / Phase 3) — stub or git+command adapter."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

from src.context_platform.schemas import ManufacturingStatus
from src.context_platform.store import get_store

logger = logging.getLogger(__name__)

_MAX_LOG_CHARS = 24_000


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


def _truncate(s: str, limit: int = _MAX_LOG_CHARS) -> str:
    if len(s) <= limit:
        return s
    return s[: limit - 80] + f"\n\n… truncated ({len(s)} chars total)\n"


def _package_one_line_summary(store, package_id: str) -> str:
    try:
        pkg = store.get_context_package(package_id)
    except KeyError:
        return "(package not found)"
    biz = pkg.business_context
    if isinstance(biz, dict) and biz.get("summary"):
        return str(biz["summary"])[:500]
    return f"story_id={pkg.story_id}, version v{pkg.version}, readiness {pkg.readiness_score}%"


def _timeout_sec() -> int:
    try:
        return max(30, int(os.environ.get("MANUFACTURING_TIMEOUT_SEC", "600")))
    except ValueError:
        return 600


def _git_depth() -> int:
    try:
        return max(1, int(os.environ.get("MANUFACTURING_GIT_DEPTH", "1")))
    except ValueError:
        return 1


def _git_adapter_enabled() -> bool:
    return bool((os.environ.get("MANUFACTURING_GIT_URL") or "").strip())


def _run_git_pipeline(
    request_id: str,
    pid: str,
    h: str | None,
    summary_line: str,
    snap_note: str,
) -> tuple[str, str, str | None]:
    """
    Clone MANUFACTURING_GIT_URL into output dir, optionally MANUFACTURING_RUN_CMD.
    Returns (markdown_body, short_summary, error_message or None).
    """
    url = (os.environ.get("MANUFACTURING_GIT_URL") or "").strip()
    ref = (os.environ.get("MANUFACTURING_GIT_REF") or "").strip()
    run_cmd = (os.environ.get("MANUFACTURING_RUN_CMD") or "").strip()
    timeout = _timeout_sec()
    depth = _git_depth()
    root = _output_root() / request_id
    root.mkdir(parents=True, exist_ok=True)
    work = root / "repo"
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)

    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    if ref:
        clone = [
            "git",
            "clone",
            "--depth",
            str(depth),
            "--branch",
            ref,
            url,
            str(work),
        ]
    else:
        clone = ["git", "clone", "--depth", str(depth), url, str(work)]

    logger.info("manufacturing_git_clone: request=%s url=%s", request_id, url[:80])
    try:
        r = subprocess.run(
            clone,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return "", "", f"git clone timed out after {timeout}s"
    except FileNotFoundError:
        return "", "", "git executable not found (install git in the image/host)"

    clone_log = (r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or "")
    if r.returncode != 0:
        body = f"""# Manufacturing run (git adapter — clone failed)

| Field | Value |
|-------|-------|
| request_id | `{request_id}` |
| context_package_id | `{pid}` |
| package_content_hash | `{h or "n/a"}` |
| git_url | `{url[:200]}` |
| ref | `{ref or "(default branch)"}` |

## Clone output

```
{_truncate(clone_log)}
```
"""
        return body, "Git clone failed", clone_log[-2000:]

    patch_log = ""
    patch_file = (os.environ.get("MANUFACTURING_PATCH_FILE") or "").strip()
    if patch_file:
        p = Path(patch_file).expanduser()
        if not p.is_file():
            return (
                "",
                "",
                f"MANUFACTURING_PATCH_FILE not found or not a file: {patch_file}",
            )
        logger.info("manufacturing_git_apply: request=%s path=%s", request_id, p)
        try:
            rp = subprocess.run(
                ["git", "apply", "--verbose", str(p.resolve())],
                cwd=str(work),
                capture_output=True,
                text=True,
                timeout=min(timeout, 300),
                env=env,
            )
        except subprocess.TimeoutExpired:
            return "", "", "git apply timed out"
        patch_log = (rp.stdout or "") + "\n--- stderr ---\n" + (rp.stderr or "")
        if rp.returncode != 0:
            body = f"""# Manufacturing run (git adapter — patch failed)

| Field | Value |
|-------|-------|
| request_id | `{request_id}` |
| context_package_id | `{pid}` |
| patch_file | `{str(p)[:200]}` |

## Clone output

```
{_truncate(clone_log)}
```

## git apply

```
{_truncate(patch_log)}
```
"""
            return body, "Git apply failed", patch_log[-2000:]

    run_exit = 0
    run_log = ""
    if run_cmd:
        logger.info("manufacturing_run_cmd: request=%s", request_id)
        try:
            r2 = subprocess.run(
                ["/bin/sh", "-c", run_cmd],
                cwd=str(work),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ,
            )
            run_exit = r2.returncode
            run_log = (r2.stdout or "") + "\n--- stderr ---\n" + (r2.stderr or "")
        except subprocess.TimeoutExpired:
            run_exit = -1
            run_log = f"MANUFACTURING_RUN_CMD timed out after {timeout}s"
        except Exception as e:
            run_exit = -1
            run_log = str(e)
    else:
        run_log = "*(no `MANUFACTURING_RUN_CMD` — clone only)*\n"

    status_word = "success" if run_exit == 0 else "failed"
    body = f"""# Manufacturing run (git adapter)

| Field | Value |
|-------|-------|
| request_id | `{request_id}` |
| context_package_id | `{pid}` |
| package_content_hash | `{h or "n/a"}` |
| git_url | `{url[:200]}` |
| branch/ref | `{ref or "(default branch)"}` |
| run_cmd | `{"set" if run_cmd else "(none)"}` |
| patch_file | `{patch_file or "(none)"}` |
| run_exit_code | `{run_exit}` |

## Business summary (from live package view)

{summary_line}
{snap_note}

## Git clone

```
{_truncate(clone_log)}
```
"""
    if patch_file:
        body = body.rstrip() + f"""

## Patch (`MANUFACTURING_PATCH_FILE`)

```
{_truncate(patch_log)}
```
"""
    body = body + f"""

## Command (`MANUFACTURING_RUN_CMD`)

```
{_truncate(run_log)}
```

## Accountability

This artifact is the **manufacturing anchor** for triage (D10). Configure via env:
`MANUFACTURING_GIT_URL`, optional `MANUFACTURING_GIT_REF`, `MANUFACTURING_PATCH_FILE`,
`MANUFACTURING_RUN_CMD`, `MANUFACTURING_GIT_DEPTH`, `MANUFACTURING_TIMEOUT_SEC`.
"""
    summ = (
        f"Git manufacturing {status_word} (exit {run_exit}). "
        f"Workspace `{work}` · package `{pid[:8]}…`"
    )
    err = None if run_exit == 0 else (run_log[-1500:] or f"non-zero exit {run_exit}")
    return body, summ, err


def _stub_pipeline(
    request_id: str,
    pid: str,
    h: str | None,
    summary_line: str,
    snap_note: str,
) -> tuple[str, str, None]:
    body = f"""# Manufacturing run (stub adapter)

| Field | Value |
|-------|-------|
| request_id | `{request_id}` |
| context_package_id | `{pid}` |
| package_content_hash | `{h or "n/a"}` |

## Business summary (from live package view)

{summary_line}
{snap_note}

## Adapter mode

**Stub** — set **`MANUFACTURING_GIT_URL`** to enable the **Phase 3 git adapter**
(clone + optional `MANUFACTURING_PATCH_FILE` + optional `MANUFACTURING_RUN_CMD`).
See README *Manufacturing v2*.

## Next steps

Wire codegen, tests, or CI into `MANUFACTURING_RUN_CMD`, or replace this module with your org’s pipeline.
"""
    out_summary = (
        f"Stub manufacturing finished. Package {pid[:8]}… hash {(h or '')[:12]}…"
    )
    return body, out_summary, None


def run_manufacturing_job(request_id: str) -> None:
    """
    queued → running → awaiting_triage (success) or failed.
    Writes `MANUFACTURING_OUTPUT_DIR/<request_id>/MANUFACTURING.md`.

    **Phase 3:** when `MANUFACTURING_GIT_URL` is set, runs `git clone`, optional
    `git apply` from `MANUFACTURING_PATCH_FILE`, then optional `MANUFACTURING_RUN_CMD`
    in the repo directory. Otherwise uses the lightweight stub.
    """

    store = get_store()
    old_proj = os.environ.get("CONTEXT_PROJECT_ID")
    try:
        store.update_manufacturing_status(
            request_id,
            ManufacturingStatus.running,
            started=True,
        )
        if not _git_adapter_enabled():
            time.sleep(1.0)
        row = store.get_manufacturing_row(request_id)
        pid = row["context_package_id"]
        try:
            os.environ["CONTEXT_PROJECT_ID"] = store.get_project_id_for_package(pid)
        except KeyError:
            pass
        h = row["package_content_hash"]
        summary_line = _package_one_line_summary(store, pid)

        snap_note = ""
        try:
            pkg = store.get_context_package(pid)
            if pkg.status.value == "approved" and pkg.content_hash:
                snap_note = f"\nApproved package hash: `{pkg.content_hash}`\n"
        except KeyError:
            pass

        if _git_adapter_enabled():
            body, out_summary, err = _run_git_pipeline(
                request_id, pid, h, summary_line, snap_note
            )
        else:
            body, out_summary, err = _stub_pipeline(
                request_id, pid, h, summary_line, snap_note
            )

        out_path = _write_artifact(request_id, pid, h, body)
        out_summary = f"{out_summary} Artifact: `{out_path}`."

        if err:
            store.update_manufacturing_status(
                request_id,
                ManufacturingStatus.failed,
                finished=True,
                output_summary=out_summary,
                error_message=err[:4000],
            )
        else:
            store.update_manufacturing_status(
                request_id,
                ManufacturingStatus.awaiting_triage,
                finished=True,
                output_summary=out_summary,
            )
    except Exception as e:
        logger.exception("manufacturing_job_failed")
        try:
            store.update_manufacturing_status(
                request_id,
                ManufacturingStatus.failed,
                finished=True,
                error_message=str(e),
            )
        except Exception:
            pass
    finally:
        if old_proj is None:
            os.environ.pop("CONTEXT_PROJECT_ID", None)
        else:
            os.environ["CONTEXT_PROJECT_ID"] = old_proj


# Backward-compatible name for api.py
run_stub_manufacturing_job = run_manufacturing_job
