"""
Custom exceptions for the POS Pipeline system.
"""
from typing import Dict, Optional, Any
from models.schemas import ProcessingStage


class PipelineException(Exception):
    """Base exception for pipeline errors."""
    
    def __init__(
        self,
        message: str,
        stage: ProcessingStage,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ):
        self.message = message
        self.stage = stage
        self.details = details or {}
        self.recoverable = recoverable
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "stage": self.stage.value,
            "details": self.details,
            "recoverable": self.recoverable
        }


class ValidationError(PipelineException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            stage=ProcessingStage.TEXT_PROCESSING,
            details=details,
            recoverable=False
        )


class TextProcessingError(PipelineException):
    """Raised when text processing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            stage=ProcessingStage.TEXT_PROCESSING,
            details=details,
            recoverable=True
        )


class VideoGenerationError(PipelineException):
    """Raised when video generation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            stage=ProcessingStage.VIDEO_GENERATION,
            details=details,
            recoverable=True
        )


class ModelConversionError(PipelineException):
    """Raised when 3D model conversion fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            stage=ProcessingStage.MODEL_CONVERSION,
            details=details,
            recoverable=True
        )


class StorageError(PipelineException):
    """Raised when storage operations fail."""
    
    def __init__(
        self,
        message: str,
        stage: ProcessingStage,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            stage=stage,
            details=details,
            recoverable=False
        )


class TimeoutError(PipelineException):
    """Raised when processing exceeds timeout."""
    
    def __init__(
        self,
        message: str,
        stage: ProcessingStage,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            stage=stage,
            details=details,
            recoverable=True
        )


class ResourceLimitError(PipelineException):
    """Raised when resource limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        stage: ProcessingStage,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            stage=stage,
            details=details,
            recoverable=False
        )