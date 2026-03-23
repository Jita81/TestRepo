"""Structured context package sections (v2) — validated JSON payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UserStoryRef(BaseModel):
    """Lightweight story / AC carrier inside the business section (D4-aligned)."""

    title: str = ""
    given_when_then: str = ""


class BusinessContextSection(BaseModel):
    schema_version: int = Field(default=1, ge=1)
    summary: str = ""
    business_rules: list[str] = Field(default_factory=list)
    user_stories: list[UserStoryRef] = Field(default_factory=list)


class TechnicalComponent(BaseModel):
    name: str = ""
    responsibility: str = ""


class TechnicalApproachSection(BaseModel):
    schema_version: int = Field(default=1, ge=1)
    components: list[TechnicalComponent] = Field(default_factory=list)
    files_to_touch: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    error_handling: str = ""


class TestScenario(BaseModel):
    name: str = ""
    scenario_type: str = "happy_path"
    steps: str = ""


class TestingContractSection(BaseModel):
    schema_version: int = Field(default=1, ge=1)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    scenarios: list[TestScenario] = Field(default_factory=list)


class ContextPackageSectionsV2(BaseModel):
    """All three sections for API PATCH / form save."""

    business: BusinessContextSection = Field(default_factory=BusinessContextSection)
    technical: TechnicalApproachSection = Field(default_factory=TechnicalApproachSection)
    testing: TestingContractSection = Field(default_factory=TestingContractSection)


def sections_from_legacy_dicts(
    business_context: dict[str, Any],
    technical_approach: dict[str, Any],
    testing_contract: dict[str, Any],
) -> ContextPackageSectionsV2:
    """Coerce legacy flat dicts into v2 models (tolerates empty {})."""

    def _biz(d: dict[str, Any]) -> BusinessContextSection:
        if not d:
            return BusinessContextSection()
        if "summary" in d or "business_rules" in d or "user_stories" in d:
            return BusinessContextSection.model_validate(d)
        # Heuristic: old blob might be { "notes": "..." } or arbitrary keys
        return BusinessContextSection(
            summary=str(d.get("summary") or d.get("notes") or "") or str(d)[:2000]
        )

    def _tech(d: dict[str, Any]) -> TechnicalApproachSection:
        if not d:
            return TechnicalApproachSection()
        if "components" in d or "files_to_touch" in d:
            return TechnicalApproachSection.model_validate(d)
        return TechnicalApproachSection(
            files_to_touch=[str(x) for x in d.get("files", [])]
            if isinstance(d.get("files"), list)
            else [],
            patterns=[str(x) for x in d.get("patterns", [])]
            if isinstance(d.get("patterns"), list)
            else [],
        )

    def _test(d: dict[str, Any]) -> TestingContractSection:
        if not d:
            return TestingContractSection()
        if "scenarios" in d or "preconditions" in d:
            return TestingContractSection.model_validate(d)
        return TestingContractSection()

    return ContextPackageSectionsV2(
        business=_biz(business_context),
        technical=_tech(technical_approach),
        testing=_test(testing_contract),
    )


def compute_readiness_v2(sec: ContextPackageSectionsV2) -> float:
    score = 0.0
    b, t, tst = sec.business, sec.technical, sec.testing
    if b.summary.strip():
        score += 20
    if b.business_rules:
        score += 15
    if b.user_stories and any(us.title or us.given_when_then for us in b.user_stories):
        score += 15
    if t.components or t.files_to_touch:
        score += 20
    if t.patterns or t.error_handling.strip():
        score += 10
    if tst.preconditions or tst.postconditions or tst.invariants:
        score += 10
    if tst.scenarios:
        score += 10
    return round(min(100.0, score), 1)


def compute_readiness_with_extensions(
    sec: ContextPackageSectionsV2,
    success_patterns: dict[str, Any],
    risks_and_dependencies: dict[str, Any],
) -> float:
    """Phase 7: small bonuses when EA extension sections are populated."""

    base = compute_readiness_v2(sec)
    pats = success_patterns.get("patterns") if isinstance(success_patterns, dict) else None
    if isinstance(pats, list) and len(pats) > 0:
        base = min(100.0, base + 5.0)
    if isinstance(risks_and_dependencies, dict) and any(
        risks_and_dependencies.get(k)
        for k in ("risks", "technical_dependencies", "team_dependencies", "notes")
    ):
        base = min(100.0, base + 3.0)
    return round(min(100.0, base), 1)


def ea_gap_hints(
    success_patterns: dict[str, Any],
    risks_and_dependencies: dict[str, Any],
    section_provenance: dict[str, Any],
) -> list[str]:
    """Non-blocking EA completeness hints (dashboard / API)."""

    hints: list[str] = []
    pats = success_patterns.get("patterns") if isinstance(success_patterns, dict) else None
    if not isinstance(pats, list) or len(pats) == 0:
        hints.append("ea: success_patterns.patterns empty")
    if not isinstance(risks_and_dependencies, dict) or not any(
        risks_and_dependencies.get(k)
        for k in ("risks", "technical_dependencies", "team_dependencies")
    ):
        hints.append("ea: risks_and_dependencies thin")
    if not isinstance(section_provenance, dict) or len(section_provenance) == 0:
        hints.append("ea: section_provenance empty")
    return hints


def gap_analysis_dict(sec: ContextPackageSectionsV2) -> dict[str, Any]:
    """Human-readable gap list for D7 / dashboard."""

    gaps: list[str] = []
    b, t, tst = sec.business, sec.technical, sec.testing
    if not b.summary.strip():
        gaps.append("business.summary missing")
    if not b.business_rules:
        gaps.append("business.business_rules empty")
    if not b.user_stories:
        gaps.append("business.user_stories empty")
    if not t.components and not t.files_to_touch:
        gaps.append("technical: no components or files_to_touch")
    if not t.patterns and not t.error_handling.strip():
        gaps.append("technical: patterns / error_handling thin")
    if not tst.scenarios:
        gaps.append("testing.scenarios empty")
    if not (tst.preconditions or tst.postconditions):
        gaps.append("testing: pre/post conditions empty")
    return {"gaps": gaps, "gap_count": len(gaps)}


def sections_to_storage_tuple(sec: ContextPackageSectionsV2) -> tuple[str, str, str]:
    import json

    return (
        json.dumps(sec.business.model_dump(), ensure_ascii=False),
        json.dumps(sec.technical.model_dump(), ensure_ascii=False),
        json.dumps(sec.testing.model_dump(), ensure_ascii=False),
    )
