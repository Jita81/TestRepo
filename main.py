"""Context Engineering Platform — FastAPI application."""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

load_dotenv()
from fastapi.responses import JSONResponse, RedirectResponse
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
from src.context_platform.store import get_store, init_store

validate_dashboard_auth_env()

logger = logging.getLogger("context_platform")


def _configure_logging() -> None:
    """Console logging for operators (Docker / uvicorn stdout)."""

    raw = (os.environ.get("CONTEXT_LOG_LEVEL") or "INFO").strip().upper()
    level = getattr(logging, raw, logging.INFO)
    if not logging.root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    logging.getLogger("context_platform").setLevel(level)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)


_configure_logging()


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


@app.middleware("http")
async def request_context_logging_middleware(request: Request, call_next):
    """Attach request_id; log failures and slow/error responses."""

    rid = str(uuid.uuid4())[:12]
    request.state.request_id = rid
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_unhandled_exception request_id=%s %s %s",
            rid,
            request.method,
            request.url.path,
        )
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    sc = getattr(response, "status_code", 0)
    if sc >= 500:
        logger.error(
            "request_response request_id=%s %s %s -> %s in %.1fms",
            rid,
            request.method,
            request.url.path,
            sc,
            elapsed_ms,
        )
    elif sc >= 400:
        logger.warning(
            "request_response request_id=%s %s %s -> %s in %.1fms",
            rid,
            request.method,
            request.url.path,
            sc,
            elapsed_ms,
        )
    elif os.environ.get("CONTEXT_ACCESS_LOG", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        logger.info(
            "request_response request_id=%s %s %s -> %s in %.1fms",
            rid,
            request.method,
            request.url.path,
            sc,
            elapsed_ms,
        )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    rid = getattr(request.state, "request_id", None)
    logger.warning(
        "validation_error request_id=%s path=%s body=%s",
        rid,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log full traceback for anything FastAPI did not already handle."""

    if isinstance(exc, HTTPException):
        detail = exc.detail
        content: dict | list = detail if isinstance(detail, dict) else {"detail": detail}
        return JSONResponse(status_code=exc.status_code, content=content)
    rid = getattr(request.state, "request_id", None)
    err_id = str(uuid.uuid4())[:10]
    logger.exception(
        "unhandled_exception error_id=%s request_id=%s %s %s",
        err_id,
        rid,
        request.method,
        request.url.path,
    )
    debug = os.environ.get("CONTEXT_DEBUG_ERRORS", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    payload: dict = {
        "detail": "Internal server error",
        "error_id": err_id,
    }
    if rid:
        payload["request_id"] = rid
    if debug:
        payload["exception_type"] = type(exc).__name__
        payload["message"] = str(exc)[:800]
    return JSONResponse(status_code=500, content=payload)


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


@app.get("/health")
def health():
    """Liveness — process is up (Phase 6)."""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness — SQLite store responds (Phase 6)."""
    try:
        get_store().ping()
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "detail": str(e)[:300]},
        )
    return {"status": "ready", "db": "ok"}
