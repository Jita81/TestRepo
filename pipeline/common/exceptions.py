"""Custom exceptions for the pipeline."""


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    
    def __init__(self, stage: str, message: str, details: dict = None):
        self.stage = stage
        self.message = message
        self.details = details or {}
        super().__init__(f"[{stage}] {message}")


class VideoGenerationError(PipelineError):
    """Exception raised during video generation."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("video_generation", message, details)


class ModelConversionError(PipelineError):
    """Exception raised during 3D model conversion."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("model_conversion", message, details)


class ValidationError(PipelineError):
    """Exception raised during input validation."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("validation", message, details)


class QueueError(PipelineError):
    """Exception raised during queue operations."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("queue", message, details)


class ResourceError(PipelineError):
    """Exception raised when resources are insufficient."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("resource", message, details)