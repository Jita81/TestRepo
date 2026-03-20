"""Context Engineering Platform — FastAPI application."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
from fastapi.responses import RedirectResponse

from src.context_platform import api as context_platform_api
from src.context_platform.middleware_actor import ActorMiddleware
from src.context_platform.middleware_api_key import ApiKeyMiddleware
from src.context_platform.store import init_store

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

app.add_middleware(ApiKeyMiddleware)
app.add_middleware(ActorMiddleware)

app.include_router(
    context_platform_api.api_router,
    tags=["Context Platform API"],
)
app.include_router(context_platform_api.page_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/context", status_code=302)
