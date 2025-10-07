"""Tests for custom exceptions."""

import pytest
from common.exceptions import (
    PipelineError,
    VideoGenerationError,
    ModelConversionError,
    ValidationError,
    QueueError,
    ResourceError
)


class TestPipelineError:
    """Tests for PipelineError base exception."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = PipelineError("test_stage", "Test message")
        assert error.stage == "test_stage"
        assert error.message == "Test message"
        assert str(error) == "[test_stage] Test message"
    
    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"key": "value", "code": 123}
        error = PipelineError("test_stage", "Test message", details)
        assert error.details == details
        assert error.details["key"] == "value"
    
    def test_error_without_details(self):
        """Test error without details defaults to empty dict."""
        error = PipelineError("test_stage", "Test message")
        assert error.details == {}


class TestVideoGenerationError:
    """Tests for VideoGenerationError."""
    
    def test_video_error(self):
        """Test video generation error."""
        error = VideoGenerationError("Failed to generate video")
        assert error.stage == "video_generation"
        assert error.message == "Failed to generate video"
    
    def test_video_error_with_details(self):
        """Test video error with details."""
        details = {"frame": 100, "reason": "timeout"}
        error = VideoGenerationError("Generation failed", details)
        assert error.details["frame"] == 100


class TestModelConversionError:
    """Tests for ModelConversionError."""
    
    def test_model_error(self):
        """Test model conversion error."""
        error = ModelConversionError("Failed to convert model")
        assert error.stage == "model_conversion"
        assert error.message == "Failed to convert model"
    
    def test_model_error_with_details(self):
        """Test model error with details."""
        details = {"vertices": 0, "reason": "invalid_mesh"}
        error = ModelConversionError("Conversion failed", details)
        assert error.details["vertices"] == 0


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError("Invalid input format")
        assert error.stage == "validation"
        assert error.message == "Invalid input format"


class TestQueueError:
    """Tests for QueueError."""
    
    def test_queue_error(self):
        """Test queue error."""
        error = QueueError("Failed to connect to queue")
        assert error.stage == "queue"
        assert error.message == "Failed to connect to queue"


class TestResourceError:
    """Tests for ResourceError."""
    
    def test_resource_error(self):
        """Test resource error."""
        error = ResourceError("Insufficient memory")
        assert error.stage == "resource"
        assert error.message == "Insufficient memory"