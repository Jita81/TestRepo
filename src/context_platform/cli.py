"""Operational CLI (Phase 6): verify migrations, load reference data, backup SQLite."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def _db_path() -> str:
    return os.environ.get("CONTEXT_DB_PATH", "data/context_platform.db")


def cmd_migrate() -> int:
    from dotenv import load_dotenv

    load_dotenv()
    from src.context_platform.store import get_store, init_store

    db = _db_path()
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    init_store(db)
    get_store().ping()
    print(f"migrate: ok — SQLite schema current ({db})")
    return 0


def cmd_seed() -> int:
    from dotenv import load_dotenv

    load_dotenv()
    from src.context_platform.reference_seed import run_reference_seed

    msg = run_reference_seed(_db_path())
    print(msg)
    return 0


def cmd_index_codebase(ns: argparse.Namespace) -> int:
    from dotenv import load_dotenv

    load_dotenv()
    from pathlib import Path

    from src.context_platform.store import get_store, init_store

    root = Path(ns.root).resolve()
    if not root.is_dir():
        print(f"index-codebase: error — not a directory: {root}", file=sys.stderr)
        return 1
    init_store(_db_path())
    try:
        stats = get_store().reindex_codebase_mirror(root, max_files=ns.max_files)
    except Exception as e:
        print(f"index-codebase: error — {e}", file=sys.stderr)
        return 1
    print(json.dumps(stats, indent=2))
    return 0


def cmd_backup(ns: argparse.Namespace) -> int:
    db = Path(ns.db or _db_path())
    if not db.is_file():
        print(f"backup: error — not a file: {db}", file=sys.stderr)
        return 1
    out_dir = Path(ns.out or "data/backups")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = out_dir / f"context_platform_backup_{ts}.db"
    shutil.copy2(db, dest)
    print(f"backup: copied {db.resolve()} -> {dest.resolve()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m src.context_platform.cli",
        description="Context platform operations (migrations, seed, backup, codebase index).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("migrate", help="Open DB and apply idempotent migrations (same as app startup).")
    sub.add_parser(
        "seed",
        help="Load the reference dataset (fixed project id prj_reference).",
    )

    bp = sub.add_parser("backup", help="Copy the SQLite file to data/backups/ with a timestamp.")
    bp.add_argument("--db", help="SQLite path (default: CONTEXT_DB_PATH or data/context_platform.db).")
    bp.add_argument(
        "--out",
        help="Backup directory (default: data/backups).",
    )

    ic = sub.add_parser(
        "index-codebase",
        help="Phase 11: mirror text files from --root into SQLite for /codebase-search.",
    )
    ic.add_argument(
        "--root",
        required=True,
        help="Absolute or relative path to repository root to index.",
    )
    ic.add_argument(
        "--max-files",
        type=int,
        default=50_000,
        help="Safety cap on number of files (default 50000).",
    )

    args = p.parse_args(argv)
    if args.command == "migrate":
        return cmd_migrate()
    if args.command == "seed":
        return cmd_seed()
    if args.command == "backup":
        return cmd_backup(args)
    if args.command == "index-codebase":
        return cmd_index_codebase(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
