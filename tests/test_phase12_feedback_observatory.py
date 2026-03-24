"""Phase 12 — Q2 diff attachment + analytics summary."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from src.context_platform.schemas import (
    ContextPackageCreate,
    ContextPackageSections,
    ContextPackageUpdate,
    ManufacturingStatus,
    ManufacturingSubmit,
    SignOffCreate,
    SignOffRole,
    TriageQueue,
    TriageSubmit,
)
from src.context_platform.store import ContextStore, init_store


class TestPhase12TriageDiffAndAnalytics(unittest.TestCase):
    def setUp(self) -> None:
        self._td = TemporaryDirectory()
        self.db = Path(self._td.name) / "p12.db"
        os.environ["CONTEXT_DB_PATH"] = str(self.db)
        os.environ["CONTEXT_PROJECT_ID"] = "prj_default"
        init_store(self.db)
        self.store = ContextStore(self.db)

    def tearDown(self) -> None:
        self._td.cleanup()
        os.environ.pop("CONTEXT_DB_PATH", None)

    def _approved_package_and_mfg(self) -> tuple[str, str]:
        story = self.store.create_story_on_default_backlog("s1", "")
        pkg = self.store.create_context_package(ContextPackageCreate(story_id=story.id))
        self.store.update_context_package(
            pkg.id,
            ContextPackageUpdate(
                sections=ContextPackageSections(
                    business_context={"summary": "x"},
                    technical_approach={"components": []},
                    testing_contract={"scenarios": []},
                )
            ),
        )
        for role in (
            SignOffRole.context_engineer,
            SignOffRole.product_owner,
            SignOffRole.tech_lead,
        ):
            self.store.add_sign_off(
                pkg.id,
                SignOffCreate(role=role, signed_by="t"),
            )
        m = self.store.submit_manufacturing(
            pkg.id,
            ManufacturingSubmit(
                submitted_by="dev",
                predicted_triage_queue=TriageQueue.Q2,
            ),
        )
        self.store.update_manufacturing_status(
            m.id,
            ManufacturingStatus.awaiting_triage,
        )
        return pkg.id, m.id

    def test_q2_diff_stored_in_detail(self) -> None:
        _pkg_id, mid = self._approved_package_and_mfg()
        tri = self.store.submit_triage(
            mid,
            TriageSubmit(
                queue=TriageQueue.Q2,
                gap_items=["gap one"],
                diff_ref="https://example.com/pr/1",
                diff_format="url",
            ),
        )
        self.assertIn("diff_attachment", tri.detail)
        self.assertEqual(tri.detail["diff_attachment"]["format"], "url")
        self.assertIn("pr/1", tri.detail["diff_attachment"]["ref"])

    def test_diff_only_for_q2_validation(self) -> None:
        with self.assertRaises(ValidationError):
            TriageSubmit(
                queue=TriageQueue.Q1,
                feedback="ok",
                diff_ref="https://x",
            )

    def test_analytics_summary_keys(self) -> None:
        _pkg_id, mid = self._approved_package_and_mfg()
        self.store.submit_triage(
            mid,
            TriageSubmit(
                queue=TriageQueue.Q2,
                gap_items=["g"],
                diff_summary="@@ -1 +1 @@\n-old\n+new",
            ),
        )
        s = self.store.get_analytics_summary()
        self.assertEqual(s["project_id"], "prj_default")
        self.assertIn("triage_by_queue", s)
        self.assertEqual(s["triage_by_queue"].get("Q2"), 1)
        self.assertEqual(s["q2_with_diff_attachment"], 1)
        self.assertIn("triage_prediction", s)
        self.assertEqual(s["triage_prediction"]["with_prediction"], 1)
        self.assertEqual(s["triage_prediction"]["matches_actual"], True)

