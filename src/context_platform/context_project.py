"""Request-scoped project id for multi-tenant isolation (MVP)."""

from __future__ import annotations

import contextvars
import os

DEFAULT_PROJECT_ID = "prj_default"

_current_project: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "context_project", default=None
)


def get_project_id() -> str:
    """Prefer request-scoped id (middleware); else CONTEXT_PROJECT_ID env; else default."""
    try:
        v = _current_project.get()
        if v is not None:
            return v[:80]
    except LookupError:
        pass
    env = (os.environ.get("CONTEXT_PROJECT_ID") or "").strip()
    if env:
        return env[:80]
    return DEFAULT_PROJECT_ID


def set_project_token(project_id: str) -> contextvars.Token[str | None]:
    p = (project_id or DEFAULT_PROJECT_ID).strip()[:80] or DEFAULT_PROJECT_ID
    return _current_project.set(p)


def reset_project_token(token: contextvars.Token[str | None]) -> None:
    _current_project.reset(token)
