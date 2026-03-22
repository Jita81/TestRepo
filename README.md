# Context Engineering Platform

Reference implementation for the **Automated Agile — Context Engineering Platform**: a **self-curating context graph** (roadmap → story → **D7** context package → **D8** sprint commitment → **D9** manufacturing → **D10** triage → **D11** improvement backlog) with **meetings (D4 extraction)**, **audit trail**, **decision/artifact records**, and **project-scoped** workspaces.

**Spec:** [docs/context-platform-process-architecture.md](docs/context-platform-process-architecture.md) · **Issue-style backlog:** [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md)

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
| Integrations | F | **Not done** |
| Codebase intelligence | G | **Not done** |

---

## What’s left (grouped backlog)

1. **Graph & governance:** Optional **PostgreSQL** for multi-instance deploys; org-level tenancy above `project_id`.
2. **Identity:** OAuth / SSO; roles (PO, CE, dev) beyond shared dashboard password; service accounts for automation.
3. **Delivery depth:** D8 sprint calendar/capacity UI; **D12** release sign-off placeholder; manufacturing **PR automation** / org-specific CI beyond env-driven git adapter.
4. **Meetings:** **D1** item status / ordering rules beyond MVP; **D3** richer gap-driven agenda heuristics; richer M1–M7 registry.
5. **Product / analytics:** Triage trends, improvement metrics, exports; **B4** predicted queue heuristic.
6. **Integrations:** Chat, PM, SCM webhooks (roadmap outlines in [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md)).

---

## Agent cycle phases (suggested autonomous work units)

Use these as **sequenced iterations** for coding agents (or human sprints). Each phase has a clear “done” signal without requiring calendar estimates.

| Phase | Focus | Done when |
|-------|--------|-----------|
| **1 — Scope completion** | Attach **project_id** to `audit_events`, `decision_records`, `artifacts`; filter list APIs; backfill | **✅ Done** — columns + `WHERE project_id = ?` on list/get; legacy rows backfilled to `prj_default` |
| **2 — Auth MVP** | Session login for **`/context/*`** when password env set; **`CONTEXT_API_KEY`** unchanged for `/api/*` | **✅ Done** — `/context/login`, signed cookie, `POST`/`GET` dashboard gated |
| **3 — Manufacturing v2** | **git clone + optional `git apply` + optional shell command** (tests/build); status machine unchanged | **✅ Done** — env-driven adapter + Docker `git` + README path |
| **4 — Meetings v2** | Meeting **agenda** entity + link to gaps; `generate-agenda` stub from open gaps | **✅ Done** — `meeting_agenda_items`, REST + dashboard |
| **5 — Integrations slice** | One **SCM webhook** (e.g. push) → audit event + optional story link | End-to-end demo path |
| **6 — Hardening** | Postgres option, migrations tool, backup notes, load **one** reference dataset | Deploy runbook validated |

Phase **5** (next) is **integrations**; **6** is ops hardening.

---

## Quick start (local)

```bash
pip install -r requirements.txt
cp .env.example .env   # optional
python run.py
```

- **Dashboard:** http://localhost:8000/context ( `/` redirects here )
- **OpenAPI:** http://localhost:8000/docs

With **`CONTEXT_DASHBOARD_PASSWORD`** + **`CONTEXT_SESSION_SECRET`** (≥32 chars) set, the browser must sign in at **`/context/login`** before using the dashboard. Omit them for local open access.

---

## Deployment

### Docker (recommended)

```bash
docker compose up --build
```

- App listens on **8000**.
- SQLite and manufacturing outputs use a **named volume** (`data`) so they survive restarts—see [docker-compose.yml](docker-compose.yml).

**Production checklist**

| Item | Notes |
|------|--------|
| **Dashboard auth** | Set **`CONTEXT_DASHBOARD_PASSWORD`** and **`CONTEXT_SESSION_SECRET`** (≥32 chars, e.g. `openssl rand -hex 32`). Set **`CONTEXT_SESSION_HTTPS_ONLY=1`** when TLS terminates at the app. |
| **REST** | Set **`CONTEXT_API_KEY`** so `/api/*` is not anonymous |
| **Project default** | Set `CONTEXT_PROJECT_ID` or rely on UI cookie / `X-Context-Project` |
| **Persistence** | Mount a volume at `/app/data` (see compose) or switch DB later |
| **Manufacturing (D9)** | Image includes **`git`**. For the git adapter set `MANUFACTURING_GIT_URL` (and optionally `MANUFACTURING_PATCH_FILE`, `MANUFACTURING_RUN_CMD`). Needs outbound network to clone. |
| **HTTPS** | Terminate TLS at your reverse proxy / platform load balancer |
| **OpenAI** | Optional `OPENAI_API_KEY` for meeting extraction |

**Build image only**

```bash
docker build -t context-platform .
docker run -p 8000:8000 -v context_data:/app/data \
  -e CONTEXT_API_KEY=your-api-key \
  -e CONTEXT_DASHBOARD_PASSWORD=your-dashboard-password \
  -e CONTEXT_SESSION_SECRET=$(openssl rand -hex 32) \
  context-platform
```

### CI

The repo includes [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml): each push runs **`docker build`** so the image stays buildable (no registry push unless you extend the workflow).

### Platform examples

- **Fly.io / Railway / Render:** Dockerfile deploy; set `PORT` if the platform injects it; bind `0.0.0.0` (default). Mount persistent disk for `/app/data`.
- **Kubernetes:** Single Deployment + PVC for `/app/data`; Secret for env vars.

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
| Traceability | `/audit-events`, `/decision-records`, `/artifacts`, `/improvement-items` |

**D7:** CE + PO + (tech lead **or** developer); approved snapshot + hash frozen.  
**D8:** One story ↔ one sprint commitment; D7 required unless override env/checkbox.  
**D10:** Q1 notes; Q2 gap lines; Q3 root cause + narrative (`detail_json`).  
**D1 (Phase 4):** Agenda lines stored in `meeting_agenda_items`; optional link to `context_gaps.id`; **generate-agenda** appends one item per unresolved gap in the project (skips gaps already linked to that meeting).

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTEXT_DB_PATH` | `data/context_platform.db` | SQLite path |
| `CONTEXT_PROJECT_ID` | `prj_default` | Default project (override with header/cookie) |
| `CONTEXT_ACTOR` | `anonymous` | Default actor; per request: `X-Context-Actor` |
| `CONTEXT_API_KEY` | — | If set, `/api/*` requires `X-Context-API-Key` or `Authorization: Bearer` |
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
│   └── roadmap-github-issues.md
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
│   └── manufacturing_worker.py
└── templates/
    ├── context_dashboard.html
    └── dashboard_login.html
```

---

## SQLite migration

Legacy `work_items` DBs are migrated on startup to the v2 hierarchy. New columns are added incrementally via `_ensure_extensions` (including **`meeting_agenda_items`** for Phase 4). For production scale-out, plan a **single-writer** SQLite or move to Postgres (future phase).
