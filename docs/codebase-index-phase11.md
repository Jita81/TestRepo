# Codebase index (Phase 11)

Mirrors **text-like** files from a local directory into SQLite (`codebase_index_entries`) for **fast substring search** and an optional **regex verify** pass—aligned with [agent-context-retrieval.md](agent-context-retrieval.md) (semantic + indexed text).

## Operator flow

1. Set **`CONTEXT_PROJECT_ID`** (or header/cookie) to the workspace you want to attach the index to.
2. Run:

   ```bash
   python3 -m src.context_platform.cli index-codebase --root /path/to/repo
   ```

3. Query the API (with **`CONTEXT_API_KEY`** if enabled):

   ```bash
   curl -sS "http://127.0.0.1:8000/api/context/codebase-search?q=def+hello&limit=10" \
     -H "X-Context-API-Key: $CONTEXT_API_KEY"
   ```

4. **Verify pass** (regex must match file **on disk** when possible):

   ```bash
   export CONTEXT_CODEBASE_INDEX_ROOT=/path/to/repo   # same as --root
   curl -sS "http://127.0.0.1:8000/api/context/codebase-search?q=def&verify_pattern=def%5Cs%2Bhello&limit=5" \
     -H "X-Context-API-Key: $CONTEXT_API_KEY"
   ```

   If `CONTEXT_CODEBASE_INDEX_ROOT` is unset, verify runs only against the **truncated indexed snippet** (weaker).

## Audits

- **`codebase.index_completed`** — after each full re-index (per project).
- **`codebase.search`** — each search; `detail` includes `duration_ms`, `n_results`, `verify_pattern_set`.

Filter: `GET /api/context/audit-events?action=codebase.search`.

## Performance notes

- **Substring**: SQLite `LIKE` over per-file text (capped **64k chars** per file in the index; files over **512k bytes** skipped).
- **Large repos**: use `--max-files` on the CLI; consider excluding heavy trees via skips in `codebase_index.py` (`SKIP_DIR_NAMES`).
- **CI**: the **`unittest`** job runs `tests/test_codebase_index.py` with a tiny synthetic tree.

## Future

- Trigram / FTS5 / external indexer for multi-GB trees; keep this table as a **portable MVP**.
