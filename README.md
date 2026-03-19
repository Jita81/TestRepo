# Context Engineering Platform

MVP implementation of the **Automated Agile — Context Engineering Platform** process: work items, context packages (business / technical / testing sections), **D7** three-role sign-offs, **D9** manufacturing submission, **D10** Q1/Q2/Q3 triage, context gaps, and a meetings registry.

- Process specification: [docs/context-platform-process-architecture.md](docs/context-platform-process-architecture.md)  
- **GitHub issue roadmap** (epics A–I, copy-paste issue bodies): [docs/roadmap-github-issues.md](docs/roadmap-github-issues.md)

## Quick start

```bash
pip install -r requirements.txt
python run.py
```

- **Dashboard:** [http://localhost:8000/context](http://localhost:8000/context) (root `/` redirects here)
- **OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **JSON API:** `/api/context/...`

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTEXT_DB_PATH` | `data/context_platform.db` | SQLite database file |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Port |

Copy `.env.example` to `.env` if you want to override defaults.

## Project layout

```
├── main.py                 # FastAPI app
├── run.py                  # `uvicorn` entry
├── requirements.txt
├── docs/
│   └── context-platform-process-architecture.md
├── src/
│   └── context_platform/   # Schemas, SQLite store, HTTP API + dashboard
└── templates/
    └── context_dashboard.html
```
