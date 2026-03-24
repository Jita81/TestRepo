"""Phase 11 — codebase mirror + search."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.context_platform.codebase_index import (
    sql_like_literal,
    tokenize_query,
    verify_regex_on_disk,
)
from src.context_platform.store import ContextStore, init_store


class TestCodebaseIndexHelpers(unittest.TestCase):
    def test_tokenize(self) -> None:
        self.assertEqual(tokenize_query("foo bar"), ["foo", "bar"])
        self.assertEqual(tokenize_query("a xx"), ["xx"])

    def test_sql_like_escape(self) -> None:
        self.assertIn("\\%", sql_like_literal("100%"))


class TestCodebaseIndexStore(unittest.TestCase):
    def setUp(self) -> None:
        self._td = TemporaryDirectory()
        self.db = Path(self._td.name) / "t.db"
        os.environ["CONTEXT_DB_PATH"] = str(self.db)
        os.environ["CONTEXT_PROJECT_ID"] = "prj_default"
        init_store(self.db)
        self.store = ContextStore(self.db)

    def tearDown(self) -> None:
        self._td.cleanup()
        os.environ.pop("CONTEXT_DB_PATH", None)

    def test_index_and_search(self) -> None:
        root = Path(self._td.name) / "repo"
        (root / "src").mkdir(parents=True)
        (root / "src" / "app.py").write_text("def hello():\n    return 42\n", encoding="utf-8")
        (root / "README.md").write_text("# Demo\n", encoding="utf-8")

        stats = self.store.reindex_codebase_mirror(root)
        self.assertGreaterEqual(stats["files_indexed"], 2)

        r = self.store.search_codebase_index("hello", limit=10)
        self.assertTrue(any("app.py" in m["relpath"] for m in r["matches"]))

    def test_verify_on_disk(self) -> None:
        root = Path(self._td.name) / "repo2"
        root.mkdir()
        (root / "mod.py").write_text("def target(x):\n    pass\n", encoding="utf-8")
        self.store.reindex_codebase_mirror(root)
        os.environ["CONTEXT_CODEBASE_INDEX_ROOT"] = str(root)
        try:
            r = self.store.search_codebase_index(
                "def",
                verify_pattern=r"def\s+target",
                limit=5,
            )
        finally:
            os.environ.pop("CONTEXT_CODEBASE_INDEX_ROOT", None)
        self.assertTrue(any("mod.py" in m["relpath"] for m in r["matches"]))
        self.assertTrue(r["verify_applied"])


class TestVerifyRegexOnDisk(unittest.TestCase):
    def test_path_escape(self) -> None:
        import re

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.py").write_text("x = 1\n", encoding="utf-8")
            pat = re.compile(r"x\s*=\s*1")
            self.assertTrue(verify_regex_on_disk(root, "a.py", pat))
            self.assertFalse(verify_regex_on_disk(root, "../outside", pat))


if __name__ == "__main__":
    unittest.main()
