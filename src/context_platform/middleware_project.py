"""Resolve active project from header, cookie, or env (see context_project.get_project_id)."""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.context_platform.context_project import (
    DEFAULT_PROJECT_ID,
    reset_project_token,
    set_project_token,
)


def _resolve_project_id(request: Request) -> str:
    h = (request.headers.get("x-context-project") or "").strip()
    if h:
        return h[:80]
    c = (request.cookies.get("context_project_id") or "").strip()
    if c:
        return c[:80]
    env = (os.environ.get("CONTEXT_PROJECT_ID") or "").strip()
    if env:
        return env[:80]
    return DEFAULT_PROJECT_ID


class ProjectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pid = _resolve_project_id(request)
        token = set_project_token(pid)
        try:
            return await call_next(request)
        finally:
            reset_project_token(token)
