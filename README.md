# Context Engineering Platform

MVP for the **Automated Agile — Context Engineering Platform**: **roadmap hierarchy** (cycle → delivery phase → feature → **story**), **v2 structured context packages**, **D7** frozen approval snapshot + hash, **stub manufacturing pipeline** (H1: `queued` → `running` → `awaiting_triage` → D10 triage → `completed`), **meeting transcript + stub extraction** (D2: `DECISION:` / `ACTION:` / `REQ:` lines → draft → human confirm), context gaps, meetings registry.

- Process specification: [docs/context-platform-process-architecture.md](docs/context-platform-process-architecture.md)  
- GitHub issue roadmap: [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md)

## Quick start

```bash
pip install -r requirements.txt
python run.py
```

- **Dashboard:** [http://localhost:8000/context](http://localhost:8000/context) (root `/` redirects here)  
- **OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)

## API highlights

| Area | Endpoints |
|------|-----------|
| Roadmap | `POST/GET /api/context/roadmap-cycles`, `POST/GET /api/context/delivery-phases?cycle_id=`, `POST/GET /api/context/features?delivery_phase_id=`, `GET /api/context/roadmap-tree` |
| Stories | `POST /api/context/stories`, `POST /api/context/stories/quick` (default backlog), `GET /api/context/stories` |
| Package | `POST …/context-packages`, `PATCH …/context-packages/{id}`, sign-offs |
| Manufacturing | `POST …/context-packages/{id}/manufacturing` (starts **background stub job**), `POST …/manufacturing/{id}/triage` |
| Meetings | `PUT …/meetings/{id}/transcript`, `POST …/extract-stub`, `POST …/confirm-extraction`, `GET …/meetings/{id}` |

**D7:** requires **context_engineer**, **product_owner**, and **either** **tech_lead** or **developer**. On completion, an **approved JSON snapshot** and **SHA-256 hash** are stored; the live package rows are no longer editable.

**SQLite migration:** existing DBs that used `work_items` are migrated on startup into cycles/phases/features/stories; `context_packages` gains `story_id` and approval columns.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTEXT_DB_PATH` | `data/context_platform.db` | SQLite database file |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Port |

Copy `.env.example` to `.env` if you want to override defaults.

## Project layout

```
├── main.py
├── run.py
├── requirements.txt
├── docs/
│   ├── context-platform-process-architecture.md
│   └── roadmap-github-issues.md
├── src/context_platform/
│   ├── api.py
│   ├── package_models.py   # v2 section schemas + readiness / gap_analysis
│   ├── schemas.py
│   └── store.py
└── templates/
    └── context_dashboard.html
```
