# Deploy runbook (Phase 6)

Single-process FastAPI + **SQLite** (default). Use this for production-ish installs until a multi-writer database is introduced.

## 1. Preconditions

- Python **3.12+** (or the Docker image).
- Writable directory for **`CONTEXT_DB_PATH`** (default `data/context_platform.db`).
- **TLS** terminated at a reverse proxy or platform load balancer for anything exposed to the internet.

## 2. Configuration (minimum)

| Variable | Purpose |
|----------|---------|
| `CONTEXT_DB_PATH` | SQLite file path |
| `CONTEXT_API_KEY` | Protects `/api/*` (webhooks under `/api/context/webhooks/` use HMAC instead) |
| `CONTEXT_DASHBOARD_PASSWORD` + `CONTEXT_SESSION_SECRET` | Dashboard login (≥32 char secret) |
| `CONTEXT_SCM_WEBHOOK_SECRET` | GitHub webhook HMAC |

See [README.md](../README.md) for the full table.

## 3. Health checks

After the process starts (`init_store` runs in lifespan):

```bash
curl -sSf http://127.0.0.1:8000/health   # {"status":"ok"}
curl -sSf http://127.0.0.1:8000/ready    # {"status":"ready","db":"ok"}
```

- **`/health`** — process liveness.
- **`/ready`** — SQLite `SELECT 1` via the store (503 if DB unavailable).

Orchestrators should use **`/ready`** for dependency checks; use **`/health`** only if you must not touch the DB during probes.

## 3b. Logging & troubleshooting

The app logs to **stderr / stdout** (visible in `docker logs`, systemd, or the terminal running `python3 run.py`).

| Variable | Purpose |
|----------|---------|
| `CONTEXT_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` — app loggers + uvicorn (`run.py`). Default `INFO`. |
| `CONTEXT_ACCESS_LOG` | Set `1` / `true` to log **every** request (method, path, status, duration). Default: only 4xx/5xx. |
| `CONTEXT_DEBUG_ERRORS` | Set `1` / `true` to include `exception_type` and `message` in **500** JSON responses (dev only; do not enable in production facing untrusted clients). |

Unhandled exceptions log a full **traceback** with `error_id` and `request_id` (correlate with the JSON body on 500 responses).  
Generic browser messages such as “something went wrong” usually come from **GitHub, Cursor, or a proxy**, not this repo — check that product’s status or network tab for the failing request, then server logs for the same time window.

## 4. Migrations

There is **no separate Alembic graph** in this MVP. Schema changes are applied **idempotently** on startup (`ContextStore._ensure_extensions` and related helpers), matching what happens when the API boots.

Validate migrations without running the server:

```bash
CONTEXT_DB_PATH=/path/to/context_platform.db python -m src.context_platform.cli migrate
```

## 5. Reference dataset

One **idempotent** demo graph (project `prj_reference`, cycle → story → draft package → gap):

```bash
CONTEXT_DB_PATH=/path/to/context_platform.db python -m src.context_platform.cli seed
```

Re-running prints `seed: skipped` if that project already has roadmap data.

## 6. Backups (SQLite)

**File copy** (simplest; stop writes or accept a crash-consistent copy on quiet traffic):

```bash
python -m src.context_platform.cli backup
# or
cp data/context_platform.db "data/backups/manual-$(date -u +%Y%m%dT%H%M%SZ).db"
```

**Online backup** (SQLite 3.27+):

```bash
sqlite3 data/context_platform.db ".backup 'data/backups/snapshot.db'"
```

**Restore:** stop the app, replace `CONTEXT_DB_PATH` with the backup file, restart.

**Retention:** keep multiple dated copies; test a restore quarterly.

## 7. Docker

```bash
docker compose up --build
```

Mount a volume on `/app/data` so the DB survives restarts (see `docker-compose.yml`). The Compose service and the **Dockerfile** both define a **`HEALTHCHECK`** that hits **`GET /ready`** (uses `PORT` inside the container, default 8000). Use **`docker compose ps`** to confirm `healthy`.

## 8. PostgreSQL

The application **does not** connect to PostgreSQL today; persistence is **SQLite only**. For analytics or HA, see [postgres-notes.md](postgres-notes.md).
