"""Request-scoped actor name for audit, decisions, and artifacts."""

from __future__ import annotations

import contextvars
import os

_current_actor: contextvars.ContextVar[str] = contextvars.ContextVar(
    "context_actor", default="anonymous"
)


def get_actor() -> str:
    env = (os.environ.get("CONTEXT_ACTOR") or "").strip()
    if env:
        return env[:200]
    try:
        v = _current_actor.get()
        return v if v else "anonymous"
    except LookupError:
        return "anonymous"


def set_actor_token(actor: str) -> contextvars.Token[str]:
    a = (actor or "anonymous").strip()[:200] or "anonymous"
    return _current_actor.set(a)


def reset_actor_token(token: contextvars.Token[str]) -> None:
    _current_actor.reset(token)
