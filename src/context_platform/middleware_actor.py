"""HTTP middleware: set actor from X-Context-Actor header."""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.context_platform.context_actor import reset_actor_token, set_actor_token


class ActorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw = (
            request.headers.get("x-context-actor")
            or os.environ.get("CONTEXT_ACTOR")
            or "anonymous"
        )
        token = set_actor_token(raw)
        try:
            return await call_next(request)
        finally:
            reset_actor_token(token)
