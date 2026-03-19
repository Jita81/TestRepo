from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Phase(str, Enum):
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
    product_owner = "product_owner"


class TriageQueue(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"


class ManufacturingStatus(str, Enum):
    queued = "queued"
    in_progress = "in_progress"
    completed = "completed"


class WorkItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    phase: Phase = Phase.discovery


class WorkItemRead(BaseModel):
    id: str
    title: str
    description: str
    phase: Phase
    created_at: datetime


class ContextPackageCreate(BaseModel):
    work_item_id: str


class ContextPackageSections(BaseModel):
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
    work_item_id: str
    version: int
    status: PackageStatus
    readiness_score: float
    business_context: dict[str, Any]
    technical_approach: dict[str, Any]
    testing_contract: dict[str, Any]
    created_at: datetime
    sign_offs: list[SignOffRead] = Field(default_factory=list)


class ContextGapCreate(BaseModel):
    work_item_id: str
    context_package_id: Optional[str] = None
    description: str = Field(..., min_length=1)
    gap_type: str = ""
    severity: str = "medium"
    meeting_hint: str = ""


class ContextGapRead(BaseModel):
    id: str
    work_item_id: str
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
    submitted_by: str
    submitted_at: datetime
    status: ManufacturingStatus


class TriageSubmit(BaseModel):
    queue: TriageQueue
    feedback: str = Field(..., min_length=1)


class TriageRead(BaseModel):
    id: str
    manufacturing_request_id: str
    queue: TriageQueue
    feedback: str
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
    meeting_type: MeetingTypeRef
    title: str
    scheduled_at: Optional[datetime]
    status: str
    created_at: datetime
