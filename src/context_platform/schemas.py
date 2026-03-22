from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PhaseKind(str, Enum):
    """Delivery phase within a roadmap cycle (inception / discovery / delivery)."""

    inception = "inception"
    discovery = "discovery"
    delivery = "delivery"


class PackageStatus(str, Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"


class SignOffRole(str, Enum):
    context_engineer = "context_engineer"
    tech_lead = "tech_lead"
    developer = "developer"
    product_owner = "product_owner"


class TriageQueue(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"


class TriageRootCauseCategory(str, Enum):
    """Q3 structured root-cause bucket (D10)."""

    requirements = "requirements"
    scope = "scope"
    technical = "technical"
    process = "process"
    data = "data"
    quality = "quality"
    other = "other"


class ManufacturingStatus(str, Enum):
    queued = "queued"
    running = "running"
    awaiting_triage = "awaiting_triage"
    failed = "failed"
    completed = "completed"


# --- Projects (tenant / workspace scope) ---


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ProjectRead(BaseModel):
    id: str
    name: str
    created_at: datetime


# --- Roadmap hierarchy (A1) ---


class RoadmapCycleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class RoadmapCycleRead(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: datetime


class DeliveryPhaseCreate(BaseModel):
    roadmap_cycle_id: str
    name: str = Field(..., min_length=1, max_length=200)
    phase_kind: PhaseKind = PhaseKind.discovery
    sort_order: int = 0


class DeliveryPhaseRead(BaseModel):
    id: str
    roadmap_cycle_id: str
    name: str
    phase_kind: PhaseKind
    sort_order: int
    created_at: datetime


class FeatureCreate(BaseModel):
    delivery_phase_id: str
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    sort_order: int = 0


class FeatureRead(BaseModel):
    id: str
    delivery_phase_id: str
    title: str
    description: str
    sort_order: int
    created_at: datetime


class StoryCreate(BaseModel):
    feature_id: str
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""


class StoryQuickCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""


class StoryRead(BaseModel):
    id: str
    feature_id: str
    project_id: str
    title: str
    description: str
    created_at: datetime


# --- Sprints & D8 commitment ---


class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    roadmap_cycle_id: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    capacity_notes: str = ""


class SprintRead(BaseModel):
    id: str
    project_id: str
    name: str
    roadmap_cycle_id: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    capacity_notes: str = ""
    created_at: datetime


class SprintCommitStoryBody(BaseModel):
    story_id: str
    sort_order: int = 0
    allow_unapproved: bool = False


class SprintCommitmentRead(BaseModel):
    id: str
    sprint_id: str
    story_id: str
    sort_order: int
    story_title: str
    has_approved_context: bool
    created_at: datetime


class SprintBoardRead(BaseModel):
    sprint: SprintRead
    commitments: list[SprintCommitmentRead] = Field(default_factory=list)


# --- Context package ---


class ContextPackageCreate(BaseModel):
    story_id: str


class ContextPackageSections(BaseModel):
    """API body: three JSON objects (validated as v2 sections on write)."""

    business_context: dict[str, Any] = Field(default_factory=dict)
    technical_approach: dict[str, Any] = Field(default_factory=dict)
    testing_contract: dict[str, Any] = Field(default_factory=dict)


class ContextPackageUpdate(BaseModel):
    sections: Optional[ContextPackageSections] = None
    readiness_score: Optional[float] = Field(None, ge=0, le=100)


class SignOffCreate(BaseModel):
    role: SignOffRole
    signed_by: str = Field(..., min_length=1, max_length=200)


class SignOffRead(BaseModel):
    role: SignOffRole
    signed_by: str
    signed_at: datetime


class ContextPackageRead(BaseModel):
    id: str
    story_id: str
    version: int
    status: PackageStatus
    readiness_score: float
    package_schema_version: int = 2
    business_context: dict[str, Any]
    technical_approach: dict[str, Any]
    testing_contract: dict[str, Any]
    gap_analysis: dict[str, Any] = Field(default_factory=dict)
    content_hash: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    sign_offs: list[SignOffRead] = Field(default_factory=list)


class ContextGapCreate(BaseModel):
    story_id: str
    context_package_id: Optional[str] = None
    description: str = Field(..., min_length=1)
    gap_type: str = ""
    severity: str = "medium"
    meeting_hint: str = ""


class ContextGapRead(BaseModel):
    id: str
    story_id: str
    context_package_id: Optional[str]
    description: str
    gap_type: str
    severity: str
    meeting_hint: str
    resolved: bool
    created_at: datetime


class ManufacturingSubmit(BaseModel):
    submitted_by: str = Field(..., min_length=1, max_length=200)


class ManufacturingRead(BaseModel):
    id: str
    context_package_id: str
    package_content_hash: Optional[str] = None
    submitted_by: str
    submitted_at: datetime
    status: ManufacturingStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None


class TriageSubmit(BaseModel):
    """
    D10 triage: queue-specific rules — Q1 needs notes; Q2 needs ≥1 gap line;
    Q3 needs root-cause category + narrative.
    """

    queue: TriageQueue
    feedback: str = ""
    gap_items: list[str] = Field(default_factory=list)
    root_cause_category: Optional[TriageRootCauseCategory] = None
    root_cause_narrative: Optional[str] = None

    @model_validator(mode="after")
    def validate_by_queue(self) -> "TriageSubmit":
        if self.queue == TriageQueue.Q1:
            if not self.feedback.strip():
                raise ValueError("q1_requires_feedback")
        elif self.queue == TriageQueue.Q2:
            gaps = [g.strip() for g in self.gap_items if g and g.strip()]
            if len(gaps) < 1:
                raise ValueError("q2_requires_at_least_one_gap_item")
        elif self.queue == TriageQueue.Q3:
            if self.root_cause_category is None:
                raise ValueError("q3_requires_root_cause_category")
            if not self.root_cause_narrative or len(self.root_cause_narrative.strip()) < 2:
                raise ValueError("q3_requires_root_cause_narrative")
        return self


class TriageRead(BaseModel):
    id: str
    manufacturing_request_id: str
    queue: TriageQueue
    feedback: str
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class MeetingTypeRef(str, Enum):
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M7 = "M7"


class MeetingCreate(BaseModel):
    meeting_type: MeetingTypeRef
    title: str = ""
    scheduled_at: Optional[datetime] = None


class MeetingRead(BaseModel):
    id: str
    project_id: str
    meeting_type: MeetingTypeRef
    title: str
    scheduled_at: Optional[datetime]
    status: str
    created_at: datetime
    transcript: Optional[str] = None
    extraction_status: str = "none"
    extraction_draft: dict[str, Any] = Field(default_factory=dict)
    extraction_confirmed_at: Optional[datetime] = None


class MeetingAgendaItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    notes: str = Field(default="", max_length=4000)
    context_gap_id: Optional[str] = None
    sort_order: int = 0


class MeetingAgendaItemRead(BaseModel):
    id: str
    meeting_id: str
    project_id: str
    title: str
    notes: str
    sort_order: int
    context_gap_id: Optional[str] = None
    created_at: datetime


class MeetingTranscriptUpdate(BaseModel):
    text: str = Field(..., min_length=1)


class MeetingExtractionConfirm(BaseModel):
    """
    If `accepted_indices` is set: legacy one-shot confirm of that subset only.
    Otherwise: when `item_reviews` exists on the draft, every item must be
    accepted or rejected before confirm; confirmed payload = accepted items only.
    If there are no per-item reviews (old drafts), all proposed items confirm.
    """

    accepted_indices: list[int] = Field(default_factory=list)


class ExtractionItemReviewBody(BaseModel):
    decision: Literal["accept", "reject"]


class AuditEventRead(BaseModel):
    id: str
    project_id: str
    occurred_at: datetime
    action: str
    entity_type: str
    entity_id: str
    actor: str
    detail: dict[str, Any] = Field(default_factory=dict)


class DecisionRecordRead(BaseModel):
    id: str
    project_id: str
    decision_code: str
    summary: str
    entity_type: str
    entity_id: str
    actor: str
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ArtifactRead(BaseModel):
    id: str
    project_id: str
    artifact_kind: str
    entity_type: str
    entity_id: str
    title: str
    body: dict[str, Any] = Field(default_factory=dict)
    actor: str
    created_at: datetime


class ImprovementItemRead(BaseModel):
    id: str
    source_triage_id: Optional[str] = None
    story_id: Optional[str] = None
    context_package_id: Optional[str] = None
    manufacturing_request_id: Optional[str] = None
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime
