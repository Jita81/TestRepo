# PostgreSQL (future / operator options)

The Context Engineering Platform **MVP stores all state in SQLite** with automatic, idempotent migrations on startup. There is **no** `DATABASE_URL` switch in this repository yet.

## Why SQLite first

- Single binary, minimal ops, matches the “one process” reference architecture.
- Complex SQL is written for SQLite (`sqlite_master`, `INSERT OR IGNORE`, partial indexes).

## Paths to PostgreSQL (not implemented)

1. **Application port** — Introduce a DB abstraction (e.g. SQLAlchemy 2) and translate schema + queries; add Alembic (or equivalent) for versioned migrations. Large effort; planned as a follow-on epic.

2. **Analytics / reporting** — Nightly export (CSV/SQL dump) or replicate SQLite to a warehouse with **ETL**; keeps the app on SQLite.

3. **Read replica** — Not applicable to single-file SQLite; use **backup + restore** to a static copy for BI tools.

## Until then

- Run **one writer** process per SQLite file (or accept corruption risk).
- Use **`/ready`** + backups per [deploy-runbook.md](deploy-runbook.md).
- Scale **out** by **sharding projects** to separate DB files only if you fork the product — not supported here.
