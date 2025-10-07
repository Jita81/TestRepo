"""
Data schemas for the POS Pipeline system using Pydantic.
"""
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class ProcessingStage(str, Enum):
    """Pipeline processing stages."""
    QUEUED = "queued"
    TEXT_PROCESSING = "text_processing"
    VIDEO_GENERATION = "video_generation"
    MODEL_CONVERSION = "model_conversion"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineInput(BaseModel):
    """Input schema for pipeline processing."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Text description of the POS display"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata for processing"
    )
    
    @validator('text')
    def sanitize_text(cls, v):
        """Sanitize input text."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        # Remove potentially harmful characters
        sanitized = v.replace('\x00', '')
        return sanitized.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "A modern red and white POS display stand for electronics",
                "metadata": {"category": "electronics", "brand": "TechCo"}
            }
        }


class ProcessingStatus(BaseModel):
    """Status of pipeline processing."""
    job_id: str = Field(..., description="Unique job identifier")
    stage: ProcessingStage = Field(..., description="Current processing stage")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field("", description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class TextProcessingResult(BaseModel):
    """Result from text processing stage."""
    job_id: str
    processed_text: str
    token_count: int
    embeddings: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: float


class VideoGenerationResult(BaseModel):
    """Result from video generation stage."""
    job_id: str
    video_path: str
    video_url: Optional[str] = None
    duration: float
    format: str
    resolution: tuple
    fps: int
    file_size_mb: float
    processing_time: float


class ModelConversionResult(BaseModel):
    """Result from 3D model conversion stage."""
    job_id: str
    model_path: str
    model_url: Optional[str] = None
    format: str
    vertex_count: int
    face_count: int
    file_size_mb: float
    processing_time: float


class PipelineOutput(BaseModel):
    """Final output from the pipeline."""
    job_id: str = Field(..., description="Unique job identifier")
    status: ProcessingStage
    video_url: Optional[str] = Field(None, description="URL to generated video")
    model_url: Optional[str] = Field(None, description="URL to generated 3D model")
    video_path: Optional[str] = None
    model_path: Optional[str] = None
    processing_time: float = Field(..., description="Total processing time in seconds")
    stages: Dict[str, Any] = Field(
        default_factory=dict,
        description="Details from each processing stage"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "video_url": "/storage/videos/550e8400.mp4",
                "model_url": "/storage/models/550e8400.stl",
                "processing_time": 125.5,
                "stages": {
                    "text_processing": {"time": 2.3},
                    "video_generation": {"time": 95.2},
                    "model_conversion": {"time": 28.0}
                }
            }
        }


class PipelineError(BaseModel):
    """Error information from pipeline processing."""
    job_id: str
    stage: ProcessingStage
    error_type: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recoverable: bool = False