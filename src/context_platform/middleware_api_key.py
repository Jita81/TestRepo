"""Optional API key gate for /api/* when CONTEXT_API_KEY is set."""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """
    If env CONTEXT_API_KEY is non-empty, require it for requests whose path
    starts with /api/ (matches ``X-Context-API-Key`` or ``Authorization: Bearer``).
    HTML dashboard under /context is not gated — use a reverse proxy for that.
    """

    async def dispatch(self, request: Request, call_next):
        key = os.environ.get("CONTEXT_API_KEY", "").strip()
        if not key:
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)
        provided = (request.headers.get("x-context-api-key") or "").strip()
        auth = request.headers.get("authorization") or ""
        if auth.lower().startswith("bearer "):
            provided = auth[7:].strip()
        if provided != key:
            return JSONResponse(
                {"detail": "Invalid or missing API key (X-Context-API-Key or Authorization: Bearer)"},
                status_code=401,
            )
        return await call_next(request)
