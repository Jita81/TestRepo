"""
Phase 11 — Codebase mirror + substring index for agent-style search.

Walks a directory tree, stores truncated UTF-8 text per file in SQLite, and supports
multi-token ``LIKE`` search plus optional **verify** regex (see ``CONTEXT_CODEBASE_INDEX_ROOT``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

MAX_FILE_BYTES = 512_000
MAX_SEARCHABLE_CHARS = 64_000
DEFAULT_MAX_FILES = 50_000

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
        ".tox",
        "target",
        ".idea",
        ".vscode",
    }
)

TEXT_SUFFIXES = frozenset(
    {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sql",
        ".html",
        ".htm",
        ".css",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".jsx",
        ".sh",
        ".rs",
        ".go",
        ".java",
        ".kt",
        ".rb",
        ".php",
    }
)

ALLOW_FILE_NAMES = frozenset(
    {
        "dockerfile",
        "makefile",
        "gemfile",
        "rakefile",
        "cargo.toml",
        "pyproject.toml",
    }
)


def _should_index_path(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    for part in rel.parts:
        if part in SKIP_DIR_NAMES:
            return False
    name = path.name.lower()
    suf = path.suffix.lower()
    if name in ALLOW_FILE_NAMES:
        return True
    if suf in TEXT_SUFFIXES:
        return True
    if name == "dockerfile" or name.endswith(".dockerfile"):
        return True
    return False


def iter_indexable_files(
    root: Path, *, max_files: int = DEFAULT_MAX_FILES
) -> Iterator[tuple[str, bytes]]:
    """Yield ``(posix_relpath, raw_bytes)`` for text-like files under ``root``."""

    root = root.resolve()
    if not root.is_dir():
        return
    count = 0
    for path in root.rglob("*"):
        if count >= max_files:
            break
        if not path.is_file():
            continue
        if not _should_index_path(path, root):
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        if st.st_size > MAX_FILE_BYTES:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in data[:8192]:
            continue
        rel = path.relative_to(root).as_posix()
        count += 1
        yield rel, data


def to_searchable_text(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")[:MAX_SEARCHABLE_CHARS]


def tokenize_query(q: str, *, max_tokens: int = 8) -> list[str]:
    """Non-empty tokens of length ≥ 2 (substring search)."""

    out: list[str] = []
    for t in q.replace("\r", " ").split():
        s = t.strip()
        if len(s) >= 2:
            out.append(s)
        if len(out) >= max_tokens:
            break
    return out


def sql_like_literal(token: str) -> str:
    """Pattern for ``LIKE ? ESCAPE '\\'`` (token is substring)."""

    esc = (
        token.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{esc}%"


def verify_regex_on_disk(
    mirror_root: Path,
    relpath: str,
    pattern: re.Pattern[str],
) -> bool:
    """Run regex on file bytes under ``mirror_root`` if the file still exists."""

    path = (mirror_root / relpath).resolve()
    try:
        path.relative_to(mirror_root.resolve())
    except ValueError:
        return False
    if not path.is_file():
        return False
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in data[:8192]:
        return False
    text = data.decode("utf-8", errors="replace")[: MAX_FILE_BYTES + 1]
    return pattern.search(text) is not None


def verify_regex_on_snippet(
    searchable_text: str,
    pattern: re.Pattern[str],
) -> bool:
    """Fallback verify when mirror root is missing (indexed text only)."""

    return pattern.search(searchable_text) is not None
