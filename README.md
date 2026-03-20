# Context Engineering Platform

MVP for the **Automated Agile — Context Engineering Platform**: **roadmap hierarchy**, **v2 structured context packages**, **D7** frozen approval snapshot + hash, **D8 sprints** (commit stories with D7 gate + optional override), **stub manufacturing** + on-disk artifact, **D10 triage**, **D11 improvement backlog** (auto from **Q2/Q3** triage), **append-only audit trail**, **`decision_records`** (typed **D7 / D8 / D10 / D4** entries) + **`artifacts`** (approved package, triage, meeting extraction, sprint commitment), **meeting extraction** (optional OpenAI or pattern stub) with **per-item accept/reject**, context gaps, meetings registry.

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
| D8 Sprints | `POST/GET /api/context/sprints`, `GET /api/context/sprints/{id}` (board + commitments), `POST …/sprints/{id}/commitments`, `DELETE …/commitments/{story_id}` |
| Package | `POST …/context-packages`, `PATCH …/context-packages/{id}`, sign-offs |
| Manufacturing | `POST …/context-packages/{id}/manufacturing` (starts **background stub job**), `POST …/manufacturing/{id}/triage` |
| Meetings | `PUT …/transcript`, `POST …/extract-stub`, `POST …/extraction-items/{i}/review`, `POST …/extraction-accept-all`, `POST …/confirm-extraction`, `GET …/meetings/{id}` |
| Audit | `GET /api/context/audit-events` (optional `entity_type`, `entity_id`, `limit`) |
| Decisions | `GET /api/context/decision-records` (filter by `entity_type`, `entity_id`, `decision_code`) |
| Artifacts | `GET /api/context/artifacts` (filter by `entity_type`, `entity_id`, `artifact_kind`) |
| D11 | `GET /api/context/improvement-items`, `POST …/improvement-items/{id}/resolve` |

**D7:** requires **context_engineer**, **product_owner**, and **either** **tech_lead** or **developer**. On completion, an **approved JSON snapshot** and **SHA-256 hash** are stored; the live package rows are no longer editable.

**D8:** a story may appear in **at most one** sprint commitment. By default the story must have an **approved** package; set **`CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT=1`** (or use the dashboard checkbox / API `allow_unapproved`) to bypass for admins.

**Meeting extraction:** set **`OPENAI_API_KEY`** (and optional **`OPENAI_MODEL`**, default `gpt-4o-mini`) for LLM-based draft items; without a key, the **DECISION:/ACTION:/REQ:** pattern stub runs. **`python-dotenv`** loads `.env` from `main.py`.

**Manufacturing output:** each stub run writes **`MANUFACTURING.md`** under **`MANUFACTURING_OUTPUT_DIR`** (default `data/manufacturing_outputs/<request_id>/`).

**SQLite migration:** existing DBs that used `work_items` are migrated on startup into cycles/phases/features/stories; `context_packages` gains `story_id` and approval columns.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTEXT_DB_PATH` | `data/context_platform.db` | SQLite database file |
| `OPENAI_API_KEY` | — | Optional; enables LLM meeting extraction |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model for extraction |
| `MANUFACTURING_OUTPUT_DIR` | `data/manufacturing_outputs` | Stub manufacturing artifacts |
| `CONTEXT_ACTOR` | `anonymous` | Default actor; override per request with **`X-Context-Actor`** |
| `CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT` | unset | If `1` / `true`, allow D8 sprint commits without an approved package |
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
│   ├── context_actor.py    # request-scoped actor (context var)
│   ├── middleware_actor.py # X-Context-Actor header
│   ├── meeting_llm.py
│   ├── meeting_extraction.py
│   ├── manufacturing_worker.py
│   ├── package_models.py
│   ├── schemas.py
│   └── store.py
└── templates/
    └── context_dashboard.html
```
