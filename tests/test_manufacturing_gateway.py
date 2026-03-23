"""Phase 10 — manufacturing gateway prompt layout + triage heuristic."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.context_platform.manufacturing_gateway import (
    build_manufacturing_prompt_bundle,
    format_manufacturing_prompt_markdown,
    predict_triage_queue_heuristic,
)
from src.context_platform.schemas import ContextPackageRead, PackageStatus


def _pkg(**kwargs: object) -> ContextPackageRead:
    base = dict(
        id="pkg-1",
        story_id="story-1",
        version=1,
        status=PackageStatus.approved,
        readiness_score=80.0,
        package_schema_version=3,
        business_context={"summary": "Reset password"},
        technical_approach={"components": []},
        testing_contract={},
        success_patterns={},
        risks_and_dependencies={},
        section_provenance={},
        gap_analysis={"gaps": [], "gap_count": 0},
        content_hash="deadbeef",
        approved_at=None,
        created_at=datetime.now(timezone.utc),
        sign_offs=[],
    )
    base.update(kwargs)
    return ContextPackageRead.model_validate(base)


class TestManufacturingGateway(unittest.TestCase):
    def test_bundle_has_stable_keys(self) -> None:
        b = build_manufacturing_prompt_bundle(_pkg(), story_title="T1")
        self.assertEqual(b["gateway_version"], "1.0")
        self.assertEqual(b["context_package_id"], "pkg-1")
        self.assertEqual(b["story_title"], "T1")
        self.assertIn("business_context", b)
        self.assertIn("predicted_triage_queue_hint", b)

    def test_markdown_contains_package_id_and_json_blocks(self) -> None:
        p = _pkg()
        md = format_manufacturing_prompt_markdown(build_manufacturing_prompt_bundle(p))
        self.assertIn("pkg-1", md)
        self.assertIn("# Manufacturing gateway (Phase 10)", md)
        self.assertIn("## business_context", md)
        self.assertIn("```json", md)
        self.assertIn("Reset password", md)

    def test_heuristic_q2_when_gaps(self) -> None:
        p = _pkg(
            gap_analysis={"gaps": ["missing SLA"], "gap_count": 1},
            readiness_score=95.0,
        )
        self.assertEqual(predict_triage_queue_heuristic(p), "Q2")

    def test_heuristic_q3_low_readiness(self) -> None:
        p = _pkg(readiness_score=40.0, gap_analysis={"gaps": [], "gap_count": 0})
        self.assertEqual(predict_triage_queue_heuristic(p), "Q3")

    def test_heuristic_q1_high_readiness_no_gaps(self) -> None:
        p = _pkg(readiness_score=90.0, gap_analysis={"gaps": [], "gap_count": 0})
        self.assertEqual(predict_triage_queue_heuristic(p), "Q1")

    def test_heuristic_none_mid_band(self) -> None:
        p = _pkg(readiness_score=60.0, gap_analysis={"gaps": [], "gap_count": 0})
        self.assertIsNone(predict_triage_queue_heuristic(p))


if __name__ == "__main__":
    unittest.main()
