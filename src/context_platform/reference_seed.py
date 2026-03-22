"""Idempotent reference dataset for Phase 6 — one project slice + draft package + gap."""

from __future__ import annotations

REF_PROJECT_ID = "prj_reference"


def run_reference_seed(db_path: str) -> str:
    from src.context_platform.context_project import reset_project_token, set_project_token
    from src.context_platform.schemas import (
        ContextGapCreate,
        ContextPackageCreate,
        DeliveryPhaseCreate,
        FeatureCreate,
        PhaseKind,
        RoadmapCycleCreate,
        StoryCreate,
    )
    from src.context_platform.store import get_store, init_store

    init_store(db_path)
    store = get_store()
    with store._connect() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO projects (id, name, created_at)
            VALUES (?, ?, datetime('now'))""",
            (REF_PROJECT_ID, "Reference dataset (Phase 6)"),
        )
        conn.commit()

    tok = set_project_token(REF_PROJECT_ID)
    try:
        if store.list_roadmap_cycles():
            return (
                f"seed: skipped — data already present for project `{REF_PROJECT_ID}`"
            )

        cycle = store.create_roadmap_cycle(
            RoadmapCycleCreate(name="2026 — Reference cycle")
        )
        phase = store.create_delivery_phase(
            DeliveryPhaseCreate(
                roadmap_cycle_id=cycle.id,
                name="Discovery",
                phase_kind=PhaseKind.discovery,
                sort_order=0,
            )
        )
        feature = store.create_feature(
            FeatureCreate(
                delivery_phase_id=phase.id,
                title="Customer authentication",
                description="Login, session, password reset",
                sort_order=0,
            )
        )
        story = store.create_story(
            StoryCreate(
                feature_id=feature.id,
                title="Send password reset email",
                description="User receives a time-limited link to set a new password.",
            )
        )
        pkg = store.create_context_package(ContextPackageCreate(story_id=story.id))
        store.create_gap(
            ContextGapCreate(
                story_id=story.id,
                context_package_id=pkg.id,
                description="Clarify expiry window for reset tokens in business rules.",
                gap_type="clarity",
                severity="medium",
                meeting_hint="M4",
            )
        )
        store.log_audit(
            "reference_dataset_loaded",
            "project",
            REF_PROJECT_ID,
            actor="cli_seed",
            detail={"story_id": story.id, "package_id": pkg.id},
        )
        return (
            f"seed: ok — project={REF_PROJECT_ID} story={story.id} package={pkg.id}"
        )
    finally:
        reset_project_token(tok)
