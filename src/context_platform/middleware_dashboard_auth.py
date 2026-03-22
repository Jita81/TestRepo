"""Require dashboard login when CONTEXT_DASHBOARD_PASSWORD is set (after SessionMiddleware)."""

from __future__ import annotations

from urllib.parse import quote

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.context_platform.dashboard_auth import dashboard_password_configured

SESSION_KEY = "dashboard_auth"


class DashboardAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not dashboard_password_configured():
            return await call_next(request)
        path = request.url.path
        if path == "/context/login" or path.startswith("/context/login/"):
            return await call_next(request)
        if not path.startswith("/context"):
            return await call_next(request)
        sess = request.session
        if sess.get(SESSION_KEY):
            return await call_next(request)
        login = "/context/login"
        if request.method in ("GET", "HEAD"):
            nxt = path if path != "/context" else "/context"
            return RedirectResponse(
                url=f"{login}?next={quote(nxt, safe='')}",
                status_code=302,
            )
        return RedirectResponse(url=login, status_code=302)
