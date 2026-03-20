# Context Engineering Platform

MVP for the **Automated Agile — Context Engineering Platform**: **roadmap hierarchy**, **v2 structured context packages**, **D7** frozen approval snapshot + hash, **stub manufacturing** + on-disk artifact, **D10 triage**, **D11 improvement backlog** (auto from **Q2/Q3** triage), **append-only audit trail**, **meeting extraction** (optional OpenAI or pattern stub) with **per-item accept/reject** before confirm, context gaps, meetings registry.

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
| Meetings | `PUT …/transcript`, `POST …/extract-stub`, `POST …/extraction-items/{i}/review`, `POST …/extraction-accept-all`, `POST …/confirm-extraction`, `GET …/meetings/{id}` |
| Audit | `GET /api/context/audit-events` (optional `entity_type`, `entity_id`, `limit`) |
| D11 | `GET /api/context/improvement-items`, `POST …/improvement-items/{id}/resolve` |

**D7:** requires **context_engineer**, **product_owner**, and **either** **tech_lead** or **developer**. On completion, an **approved JSON snapshot** and **SHA-256 hash** are stored; the live package rows are no longer editable.

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
│   ├── meeting_llm.py      # optional OpenAI extraction
│   ├── meeting_extraction.py
│   ├── manufacturing_worker.py
│   ├── package_models.py
│   ├── schemas.py
│   └── store.py
└── templates/
    └── context_dashboard.html
```
