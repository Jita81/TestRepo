"""Operational CLI (Phase 6): verify migrations, load reference data, backup SQLite."""

from __future__ import annotations

import argparse
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
        description="Context platform operations (Phase 6 hardening).",
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

    args = p.parse_args(argv)
    if args.command == "migrate":
        return cmd_migrate()
    if args.command == "seed":
        return cmd_seed()
    if args.command == "backup":
        return cmd_backup(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
