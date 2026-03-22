"""Context Engineering Platform — FastAPI application."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from src.context_platform import api as context_platform_api
from src.context_platform.dashboard_auth import (
    dashboard_password_configured,
    dashboard_session_secret,
    validate_dashboard_auth_env,
)
from src.context_platform.middleware_actor import ActorMiddleware
from src.context_platform.middleware_api_key import ApiKeyMiddleware
from src.context_platform.middleware_dashboard_auth import DashboardAuthMiddleware
from src.context_platform.middleware_project import ProjectMiddleware
from src.context_platform.store import init_store

validate_dashboard_auth_env()


def _session_https_only() -> bool:
    v = os.environ.get("CONTEXT_SESSION_HTTPS_ONLY", "").strip().lower()
    return v in ("1", "true", "yes", "on")

Path("data").mkdir(exist_ok=True)
Path(os.environ.get("MANUFACTURING_OUTPUT_DIR", "data/manufacturing_outputs")).mkdir(
    parents=True, exist_ok=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_store(os.environ.get("CONTEXT_DB_PATH", "data/context_platform.db"))
    yield


app = FastAPI(
    title="Context Engineering Platform",
    description="Work items, context packages, D7 sign-offs, manufacturing, triage (Q1/Q2/Q3).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(ProjectMiddleware)
app.add_middleware(ApiKeyMiddleware)
app.add_middleware(ActorMiddleware)
if dashboard_password_configured():
    sk = dashboard_session_secret()  # set by validate_dashboard_auth_env()
    assert sk is not None
    app.add_middleware(DashboardAuthMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=sk,
        session_cookie="context_session",
        max_age=14 * 24 * 3600,
        same_site="lax",
        https_only=_session_https_only(),
    )

app.include_router(
    context_platform_api.api_router,
    tags=["Context Platform API"],
)
app.include_router(context_platform_api.page_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/context", status_code=302)
