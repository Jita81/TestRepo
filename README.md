# Context Engineering Platform

Reference implementation for the **Automated Agile — Context Engineering Platform**: a **self-curating context graph** (roadmap → story → **D7** context package → **D8** sprint commitment → **D9** manufacturing → **D10** triage → **D11** improvement backlog) with **meetings (D4 extraction)**, **audit trail**, **decision/artifact records**, and **project-scoped** workspaces.

**Spec:** [docs/context-platform-process-architecture.md](docs/context-platform-process-architecture.md) · **Issue-style backlog:** [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md) · **Deploy / ops:** [docs/deploy-runbook.md](docs/deploy-runbook.md)

---

## Programme goals (what “done” means)

The programme exists so that **the right person has the right context to make the right decision at the right time**—using three primitives everywhere: **Inputs → Decisions → Outputs**, with **decisions D1–D12** and **meetings M1–M7** as first-class process steps.

| Goal | Target outcome |
|------|----------------|
| **Structured context** | Context packages are validated, versioned, and **D7-approved** before manufacturing. |
| **Traceability** | Approvals, triage, extractions, and sprint commitments are **attributed** and **queryable**. |
| **Delivery spine** | Roadmap, sprints, manufacturing, and triage connect **stories → code path → feedback**. |
| **Self-curation** | Gaps, triage (Q2/Q3), and improvement items **feed back** into context quality. |
| **Governance** | Multi-**project** isolation, optional **dashboard login** + **API key**, hooks for future **org/SSO**. |

This repo is an **MVP**: it demonstrates the spine end-to-end with SQLite, a single-process API, and a dashboard—not full enterprise auth, integrations, or real codegen.

---

## Implementation status

| Area | Spec / epic | Status in repo |
|------|-------------|----------------|
| Roadmap hierarchy | A1 | **Done** — cycle → phase → feature → story |
| Structured context package + D7 snapshot | B1, B2 | **Done** — Pydantic v2 sections, hash, frozen snapshot |
| Gap analysis / readiness | B3 | **Partial** — readiness + gap hints from schema; not full blocking UI |
| Decision & artifact records | A2 | **Partial** — `decision_records` + `artifacts`; **D7, D8, D10, D4** wired; not full D1–D12 UI |
| Audit / provenance | A3 | **Partial** — append-only events; **before/after** on key package + gap actions; not full graph diff |
| Manufacturing | H1 / D9 | **Phase 3** — configurable **git clone → optional patch → optional test/cmd**; same status machine; stub when `MANUFACTURING_GIT_URL` unset |
| Triage D10 | C2 | **Partial** — structured Q1/Q2/Q3 + `detail_json` + list API |
| Sprint D8 | C1 | **Partial** — sprints + commitments + D7 gate; light on dates/capacity |
| D11 backlog | C3 | **Partial** — items from Q2/Q3; basic list/resolve |
| Meetings / extraction D4 | D2 | **Partial** — transcript, LLM or stub, per-item review, confirm |
| Meeting agenda D1 | D1 | **Phase 4** — `meeting_agenda_items` + optional `context_gap_id`; **generate from gaps** stub; dashboard + REST |
| Projects / tenancy | I2 | **Partial** — `projects` + `project_id` on core entities **and** audit / decisions / artifacts; **not** org/RBAC |
| Auth | I1 | **Partial** — optional **dashboard** session login (`CONTEXT_DASHBOARD_PASSWORD` + `CONTEXT_SESSION_SECRET`); **API key** for `/api/*`; string actor; no OAuth/RBAC |
| Integrations | F | **Phase 5 (partial)** — GitHub **push/ping** webhook → `audit_events`; optional `story_id` + `context_project` query params; **not** PR events or normalized event table |
| Ops / hardening | I3 / Phase 6 | **Done** — **`GET /health`**, **`GET /ready`**, CLI **`python -m src.context_platform.cli`**, SQLite backup guidance, reference dataset **`prj_reference`**; **Postgres** documented as future ([docs/postgres-notes.md](docs/postgres-notes.md)) |
| Codebase intelligence | G | **Not done** |

---

## What’s left (grouped backlog)

1. **Graph & governance:** Optional **PostgreSQL** for multi-instance deploys; org-level tenancy above `project_id`.
2. **Identity:** OAuth / SSO; roles (PO, CE, dev) beyond shared dashboard password; service accounts for automation.
3. **Delivery depth:** D8 sprint calendar/capacity UI; **D12** release sign-off placeholder; manufacturing **PR automation** / org-specific CI beyond env-driven git adapter.
4. **Meetings:** **D1** item status / ordering rules beyond MVP; **D3** richer gap-driven agenda heuristics; richer M1–M7 registry.
5. **Product / analytics:** Triage trends, improvement metrics, exports; **B4** predicted queue heuristic.
6. **Integrations:** Chat, PM tools; **SCM** beyond push/ping audit (PR events, repo↔story mapping table); see Epic F in [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md).

---

## Agent cycle phases (suggested autonomous work units)

Use these as **sequenced iterations** for coding agents (or human sprints). Each phase has a clear “done” signal without requiring calendar estimates.

| Phase | Focus | Done when |
|-------|--------|-----------|
| **1 — Scope completion** | Attach **project_id** to `audit_events`, `decision_records`, `artifacts`; filter list APIs; backfill | **✅ Done** — columns + `WHERE project_id = ?` on list/get; legacy rows backfilled to `prj_default` |
| **2 — Auth MVP** | Session login for **`/context/*`** when password env set; **`CONTEXT_API_KEY`** unchanged for `/api/*` | **✅ Done** — `/context/login`, signed cookie, `POST`/`GET` dashboard gated |
| **3 — Manufacturing v2** | **git clone + optional `git apply` + optional shell command** (tests/build); status machine unchanged | **✅ Done** — env-driven adapter + Docker `git` + README path |
| **4 — Meetings v2** | Meeting **agenda** entity + link to gaps; `generate-agenda` stub from open gaps | **✅ Done** — `meeting_agenda_items`, REST + dashboard |
| **5 — Integrations slice** | One **SCM webhook** (e.g. push) → audit event + optional story link | **✅ Done** — `POST /webhooks/scm/github`, HMAC, audit; URL query for project/story |
| **6 — Hardening** | Postgres option, migrations tool, backup notes, load **one** reference dataset | **✅ Done** — `/health` & `/ready`, CLI (`migrate` / `seed` / `backup`), [deploy runbook](docs/deploy-runbook.md), [Postgres notes](docs/postgres-notes.md), reference project `prj_reference` |

Phase **6** is complete; further work is feature backlog (Epic F/G, full PG port, etc.).

---

## Quick start (local)

```bash
pip install -r requirements.txt
cp .env.example .env   # optional
python3 run.py         # or: python run.py
```

- **Dashboard:** http://localhost:8000/context (`/` redirects here)
- **OpenAPI:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health · **Readiness (DB):** http://localhost:8000/ready

With **`CONTEXT_DASHBOARD_PASSWORD`** + **`CONTEXT_SESSION_SECRET`** (≥32 chars) set, the browser must sign in at **`/context/login`** before using the dashboard. Omit them for local open access.

---

## Deployment

**Full operator guide:** [docs/deploy-runbook.md](docs/deploy-runbook.md) (backups, migrations CLI, seed data, restore). This section is the short path.

### Run with Docker Compose (recommended)

1. **Build and start** (foreground logs):

   ```bash
   docker compose up --build
   ```

2. **Check** the app is up:

   ```bash
   curl -sSf http://127.0.0.1:8000/health
   curl -sSf http://127.0.0.1:8000/ready
   ```

3. **Open** the dashboard at http://localhost:8000/context

The Compose file maps **8000 → 8000**, stores SQLite and manufacturing outputs on a **named volume** (`context_platform_data` → `/app/data`). The image includes a **container healthcheck** against `/ready` (see [docker-compose.yml](docker-compose.yml)).

### Build and run the image alone

```bash
docker build -t context-platform .
docker run -d --name ctx -p 8000:8000 \
  -v context_data:/app/data \
  -e CONTEXT_API_KEY=your-api-key \
  -e CONTEXT_DASHBOARD_PASSWORD=your-dashboard-password \
  -e CONTEXT_SESSION_SECRET="$(openssl rand -hex 32)" \
  context-platform
curl -sSf http://127.0.0.1:8000/ready
```

Use **`-e PORT=...`** if your platform injects a non-8000 port (the image respects `HOST` / `PORT`).

### Production checklist

| Item | Notes |
|------|--------|
| **TLS** | Terminate HTTPS at your reverse proxy or platform; set **`CONTEXT_SESSION_HTTPS_ONLY=1`** when the app sees HTTPS. |
| **Probes** | Liveness: **`GET /health`**. Readiness / dependency: **`GET /ready`** (503 if SQLite cannot be opened). |
| **Dashboard auth** | **`CONTEXT_DASHBOARD_PASSWORD`** + **`CONTEXT_SESSION_SECRET`** (≥32 chars). |
| **REST** | **`CONTEXT_API_KEY`** on `/api/*` — **`/api/context/webhooks/*`** is exempt; use **`CONTEXT_SCM_WEBHOOK_SECRET`** + GitHub HMAC for SCM. |
| **SCM webhook** | Same secret in GitHub and **`CONTEXT_SCM_WEBHOOK_SECRET`**; webhook URL over HTTPS; optional **`?context_project=`** / **`?story_id=`**. |
| **Persistence** | Mount a volume on **`/app/data`** (Compose does this). Back up the SQLite file per [docs/deploy-runbook.md](docs/deploy-runbook.md). |
| **Manufacturing** | Image includes **`git`**. Set **`MANUFACTURING_*`** only if you use the git adapter; requires outbound network to clone. |
| **OpenAI** | Optional **`OPENAI_API_KEY`** for meeting extraction. |

### After deploy (optional)

- **Reference demo data** (idempotent, project `prj_reference`):  
  `docker compose exec web python -m src.context_platform.cli seed`  
  (or run the same command on the host against `CONTEXT_DB_PATH`.)
- **CI:** [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml) runs **`docker build`** plus a **`cli`** job (`migrate` + `seed`) on each push.

### Platform notes

- **Fly.io / Railway / Render:** Dockerfile deploy; bind **`0.0.0.0`**; mount persistent disk for **`/app/data`**; align **`PORT`** with the platform.
- **Kubernetes:** Deployment + Service; **livenessProbe** → `/health`, **readinessProbe** → `/ready`; PVC for **`/app/data`**; Secrets for env vars.

---

## API overview

| Area | Endpoints (prefix `/api/context`) |
|------|-----------------------------------|
| Projects | `GET/POST /projects` — scope via `X-Context-Project`, cookie `context_project_id`, or `CONTEXT_PROJECT_ID` |
| Roadmap | `/roadmap-cycles`, `/delivery-phases`, `/features`, `/roadmap-tree`, stories CRUD |
| D8 | `/sprints`, `/sprints/{id}`, `/sprints/{id}/commitments` |
| Package / D7 | `/stories/{id}/context-packages`, `PATCH`, `/sign-offs` |
| D9 / D10 | `/context-packages/{id}/manufacturing`, `/manufacturing/{id}/triage`, `GET /triage-results` |
| Meetings | `/meetings`, **D1** `GET/POST /meetings/{id}/agenda`, `POST /meetings/{id}/generate-agenda`; **D4** transcript, extract, confirm, per-item review |
| Integrations | **`POST /webhooks/scm/github`** — GitHub **push** / **ping** (JSON); signs with **`X-Hub-Signature-256`** when secret set |
| Health (Phase 6) | **`GET /health`** (liveness), **`GET /ready`** (DB ping — 503 if store fails) |
| Traceability | `/audit-events`, `/decision-records`, `/artifacts`, `/improvement-items` |

**D7:** CE + PO + (tech lead **or** developer); approved snapshot + hash frozen.  
**D8:** One story ↔ one sprint commitment; D7 required unless override env/checkbox.  
**D10:** Q1 notes; Q2 gap lines; Q3 root cause + narrative (`detail_json`).  
**D1 (Phase 4):** Agenda lines stored in `meeting_agenda_items`; optional link to `context_gaps.id`; **generate-agenda** appends one item per unresolved gap in the project (skips gaps already linked to that meeting).

**Phase 5 (SCM):** Configure GitHub → **Webhooks** → URL  
`https://<host>/api/context/webhooks/scm/github`  
Add **`?context_project=<project_id>`** if the default env project is wrong, and **`&story_id=<story_uuid>`** to attach a story (must exist in that project). Set **`CONTEXT_SCM_WEBHOOK_SECRET`** to a long random string; in GitHub use the same as the webhook **Secret** so `X-Hub-Signature-256` validates. Events appear in **`GET /api/context/audit-events`** as **`scm_push_received`**, **`scm_webhook_ping`**, or **`scm_webhook_event`**.

**Phase 6:** Operator procedures, backups, and **`python -m src.context_platform.cli`** (`migrate` / `seed` / `backup`) — [docs/deploy-runbook.md](docs/deploy-runbook.md). **PostgreSQL:** [docs/postgres-notes.md](docs/postgres-notes.md). Reference seed: [data/reference_manifest.json](data/reference_manifest.json).

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTEXT_DB_PATH` | `data/context_platform.db` | SQLite path |
| `CONTEXT_PROJECT_ID` | `prj_default` | Default project (override with header/cookie) |
| `CONTEXT_ACTOR` | `anonymous` | Default actor; per request: `X-Context-Actor` |
| `CONTEXT_API_KEY` | — | If set, `/api/*` requires `X-Context-API-Key` or `Authorization: Bearer` (webhooks under `/api/context/webhooks/` are exempt) |
| `CONTEXT_SCM_WEBHOOK_SECRET` | — | If set, **`POST /webhooks/scm/github`** requires HMAC-SHA256 (`X-Hub-Signature-256: sha256=<hex>` or `X-Context-SCM-Signature`) |
| `CONTEXT_DASHBOARD_PASSWORD` | — | If set, `/context/*` (except `/login`) requires session sign-in |
| `CONTEXT_SESSION_SECRET` | — | Required with dashboard password; ≥32 chars; signs session cookie |
| `CONTEXT_DASHBOARD_USER` | `admin` | Dashboard login username |
| `CONTEXT_SESSION_HTTPS_ONLY` | unset | `1` / `true` — `Secure` session cookie (use behind HTTPS) |
| `CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT` | unset | `1` / `true` allows D8 without D7 |
| `OPENAI_API_KEY` / `OPENAI_MODEL` | — / `gpt-4o-mini` | Optional LLM meeting extraction |
| `MANUFACTURING_OUTPUT_DIR` | `data/manufacturing_outputs` | Per-request output dir + `MANUFACTURING.md` |
| `MANUFACTURING_GIT_URL` | — | If set, **Phase 3 adapter**: shallow `git clone` into `<output>/<request_id>/repo` |
| `MANUFACTURING_GIT_REF` | — | Optional branch or tag for `git clone --branch …` |
| `MANUFACTURING_GIT_DEPTH` | `1` | Shallow clone depth |
| `MANUFACTURING_PATCH_FILE` | — | Optional unified diff on disk; `git apply` in repo after clone (mount into container if using Docker) |
| `MANUFACTURING_RUN_CMD` | — | Optional shell command run **in repo root** (e.g. `pytest -q` or `npm test`). **Runs as the app user** — treat like CI. |
| `MANUFACTURING_TIMEOUT_SEC` | `600` | Timeout for clone, apply, and run command |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Server bind |

See [.env.example](.env.example).

---

## Manufacturing v2 (Phase 3 — D9)

When **`MANUFACTURING_GIT_URL`** is set, each manufacturing request:

1. Moves **`queued` → `running` → `awaiting_triage`** on success, or **`failed`** if clone, patch, or the run command fails (unchanged lifecycle vs the stub).
2. Clones into **`MANUFACTURING_OUTPUT_DIR/<request_id>/repo`** (shallow by default).
3. Optionally runs **`git apply`** on **`MANUFACTURING_PATCH_FILE`** (host path; in Docker, bind-mount the patch into the container and point the env var at that path).
4. Optionally runs **`MANUFACTURING_RUN_CMD`** via `/bin/sh -c` from the repo root — use this for **tests**, linters, or a thin codegen wrapper.

If **`MANUFACTURING_GIT_URL`** is unset, behaviour matches the original **stub** (short sleep + accountability `MANUFACTURING.md`).

**Example (host)**

```bash
export MANUFACTURING_GIT_URL=https://github.com/octocat/Hello-World.git
export MANUFACTURING_RUN_CMD="test -f README"
```

Use a **small** public repo and a **bounded** command for demos; production should point at your application repo and the same CI entrypoint you trust elsewhere.

---

## Repository layout

```
├── main.py                 # FastAPI app + middleware
├── run.py                  # Uvicorn entry
├── Dockerfile              # Container image (uvicorn)
├── docker-compose.yml      # Volume-backed SQLite + port 8000
├── .dockerignore
├── .github/workflows/      # Docker build CI
├── docs/
│   ├── context-platform-process-architecture.md
│   ├── deploy-runbook.md
│   ├── postgres-notes.md
│   └── roadmap-github-issues.md
├── data/
│   └── reference_manifest.json
├── src/context_platform/
│   ├── api.py
│   ├── store.py
│   ├── schemas.py
│   ├── package_models.py
│   ├── context_actor.py
│   ├── context_project.py
│   ├── dashboard_auth.py
│   ├── middleware_*.py
│   ├── meeting_extraction.py
│   ├── manufacturing_worker.py
│   ├── scm_webhook.py
│   ├── reference_seed.py
│   └── cli.py
└── templates/
    ├── context_dashboard.html
    └── dashboard_login.html
```

---

## SQLite migration

Legacy `work_items` DBs are migrated on startup to the v2 hierarchy. New columns are added incrementally via `_ensure_extensions` (including **`meeting_agenda_items`** for Phase 4). There is **no separate Alembic migration pack**; run **`python -m src.context_platform.cli migrate`** to validate the file the same way the app does on boot. For production scale-out, plan a **single-writer** SQLite and follow [docs/deploy-runbook.md](docs/deploy-runbook.md), or plan a **Postgres port** ([docs/postgres-notes.md](docs/postgres-notes.md)).
