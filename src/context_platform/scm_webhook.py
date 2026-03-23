"""SCM webhook helpers (Phase 5) — GitHub-compatible HMAC + push payload summary."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def scm_webhook_secret() -> Optional[str]:
    s = (os.environ.get("CONTEXT_SCM_WEBHOOK_SECRET") or "").strip()
    return s if s else None


def verify_scm_signature(body: bytes, signature_header: Optional[str]) -> bool:
    secret = scm_webhook_secret()
    if not secret:
        return True
    if not signature_header:
        return False
    sig = signature_header.strip()
    if sig.lower().startswith("sha256="):
        sig = sig[7:].strip()
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(mac, sig)
    except TypeError:
        return False


def is_github_hook_ping(data: dict[str, Any]) -> bool:
    return "zen" in data and "hook_id" in data


def summarize_github_push(data: dict[str, Any]) -> dict[str, Any]:
    repo = data.get("repository")
    full_name = ""
    html_url = ""
    if isinstance(repo, dict):
        full_name = str(repo.get("full_name") or repo.get("name") or "")
        html_url = str(repo.get("html_url") or "")
    ref = str(data.get("ref") or "")
    head = data.get("head_commit")
    head_sha: Optional[str] = None
    if isinstance(head, dict):
        head_sha = head.get("id")
        if isinstance(head_sha, str):
            head_sha = head_sha[:40]
    if not head_sha:
        after = data.get("after")
        if isinstance(after, str) and after and after != "0" * 40:
            head_sha = after[:40]
    commits = data.get("commits")
    n_commits = len(commits) if isinstance(commits, list) else 0
    pusher = data.get("pusher")
    pusher_name = ""
    if isinstance(pusher, dict):
        pusher_name = str(pusher.get("name") or pusher.get("login") or "")
    compare = str(data.get("compare") or "")
    return {
        "source": "github_push",
        "repository_full_name": full_name,
        "repository_url": html_url,
        "ref": ref,
        "head_sha": head_sha,
        "commits_count": n_commits,
        "pusher": pusher_name,
        "compare_url": compare,
    }
