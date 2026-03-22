"""Optional dashboard login (Phase 2) — env-driven password + signed sessions."""

from __future__ import annotations

import os


def dashboard_password_configured() -> bool:
    return bool((os.environ.get("CONTEXT_DASHBOARD_PASSWORD") or "").strip())


def dashboard_session_secret() -> str | None:
    s = (os.environ.get("CONTEXT_SESSION_SECRET") or "").strip()
    return s if len(s) >= 32 else None


def dashboard_username() -> str:
    return (os.environ.get("CONTEXT_DASHBOARD_USER") or "admin").strip() or "admin"


def verify_dashboard_credentials(username: str, password: str) -> bool:
    if not dashboard_password_configured():
        return True
    expected_user = dashboard_username()
    expected_pw = (os.environ.get("CONTEXT_DASHBOARD_PASSWORD") or "").strip()
    if not expected_pw:
        return True
    return (
        (username or "").strip() == expected_user
        and (password or "") == expected_pw
    )


def validate_dashboard_auth_env() -> None:
    """Call at startup: if password set, require a strong session secret."""
    if not dashboard_password_configured():
        return
    if dashboard_session_secret() is None:
        raise RuntimeError(
            "CONTEXT_DASHBOARD_PASSWORD is set but CONTEXT_SESSION_SECRET is missing or "
            "shorter than 32 characters. Set a long random secret for cookie signing "
            "(e.g. openssl rand -hex 32)."
        )
