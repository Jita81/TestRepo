"""Data models for pipeline communication."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class PipelineStage(str, Enum):
    """Pipeline processing stages."""
    INPUT = "input"
    VIDEO_GENERATION = "video_generation"
    MODEL_CONVERSION = "model_conversion"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TextInput(BaseModel):
    """Input model for text description."""
    description: str = Field(..., min_length=10, max_length=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description for security."""
        if any(char in v for char in ['<', '>', '{', '}', '\x00']):
            raise ValueError('Invalid characters detected in description')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "A modern retail display for energy drinks with LED backlighting",
                "metadata": {"customer_id": "12345"}
            }
        }


class GenerateResponse(BaseModel):
    """Response model for generation request."""
    request_id: str
    status: PipelineStatus
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "status": "pending",
                "message": "Pipeline initiated successfully",
                "created_at": "2025-10-07T12:00:00Z"
            }
        }


class PipelineMessage(BaseModel):
    """Message format for inter-service communication."""
    request_id: str
    stage: PipelineStage
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: PipelineStatus
    error_message: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        use_enum_values = True


class VideoMetadata(BaseModel):
    """Metadata for generated video."""
    video_path: str
    duration: float
    frame_rate: int
    resolution: tuple[int, int]
    size_bytes: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelMetadata(BaseModel):
    """Metadata for generated 3D model."""
    model_path: str
    format: str = "stl"
    vertex_count: int
    face_count: int
    size_bytes: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineResult(BaseModel):
    """Complete pipeline result."""
    request_id: str
    status: PipelineStatus
    video_metadata: Optional[VideoMetadata] = None
    model_metadata: Optional[ModelMetadata] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None