"""Tests for data models."""

import pytest
from pydantic import ValidationError
from datetime import datetime

from common.models import (
    TextInput,
    GenerateResponse,
    PipelineMessage,
    PipelineStage,
    PipelineStatus,
    VideoMetadata,
    ModelMetadata
)


class TestTextInput:
    """Tests for TextInput model."""
    
    def test_valid_input(self):
        """Test valid text input creation."""
        input_data = TextInput(
            description="A modern retail display for products",
            metadata={"test": "value"}
        )
        assert input_data.description == "A modern retail display for products"
        assert input_data.metadata == {"test": "value"}
    
    def test_min_length_validation(self):
        """Test minimum length validation."""
        with pytest.raises(ValidationError):
            TextInput(description="short")
    
    def test_max_length_validation(self):
        """Test maximum length validation."""
        with pytest.raises(ValidationError):
            TextInput(description="x" * 1001)
    
    def test_invalid_characters(self):
        """Test invalid character detection."""
        with pytest.raises(ValidationError):
            TextInput(description="Invalid <script>alert('xss')</script>")
    
    def test_whitespace_stripping(self):
        """Test whitespace is stripped."""
        input_data = TextInput(description="  Test description with enough length  ")
        assert input_data.description == "Test description with enough length"
    
    def test_default_metadata(self):
        """Test default metadata is empty dict."""
        input_data = TextInput(description="Test description with length")
        assert input_data.metadata == {}
    
    def test_edge_case_exact_min_length(self):
        """Test input with exact minimum length."""
        input_data = TextInput(description="1234567890")  # Exactly 10 chars
        assert len(input_data.description) == 10
    
    def test_edge_case_exact_max_length(self):
        """Test input with exact maximum length."""
        desc = "x" * 1000  # Exactly 1000 chars
        input_data = TextInput(description=desc)
        assert len(input_data.description) == 1000
    
    def test_null_byte_in_description(self):
        """Test that null bytes are rejected."""
        with pytest.raises(ValidationError):
            TextInput(description="Test\x00description with null byte")
    
    def test_unicode_characters(self):
        """Test that valid unicode characters are accepted."""
        input_data = TextInput(description="Display with émojis 🎨 and spëcial chars")
        assert "émojis" in input_data.description
    
    def test_empty_metadata(self):
        """Test that empty metadata is handled."""
        input_data = TextInput(description="Test description", metadata={})
        assert input_data.metadata == {}
    
    def test_nested_metadata(self):
        """Test that nested metadata is preserved."""
        metadata = {
            "customer": {"id": "123", "name": "Test"},
            "project": "retail"
        }
        input_data = TextInput(description="Test description", metadata=metadata)
        assert input_data.metadata["customer"]["id"] == "123"


class TestGenerateResponse:
    """Tests for GenerateResponse model."""
    
    def test_valid_response(self):
        """Test valid response creation."""
        response = GenerateResponse(
            request_id="req_123",
            status=PipelineStatus.PENDING,
            message="Success"
        )
        assert response.request_id == "req_123"
        assert response.status == PipelineStatus.PENDING
        assert isinstance(response.created_at, datetime)


class TestPipelineMessage:
    """Tests for PipelineMessage model."""
    
    def test_valid_message(self):
        """Test valid message creation."""
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload={"key": "value"},
            status=PipelineStatus.PENDING
        )
        assert message.request_id == "req_123"
        assert message.stage == PipelineStage.INPUT
        assert message.retry_count == 0
    
    def test_default_timestamp(self):
        """Test default timestamp is set."""
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload={},
            status=PipelineStatus.PENDING
        )
        assert isinstance(message.timestamp, datetime)


class TestVideoMetadata:
    """Tests for VideoMetadata model."""
    
    def test_valid_metadata(self):
        """Test valid video metadata creation."""
        metadata = VideoMetadata(
            video_path="/path/to/video.mp4",
            duration=30.0,
            frame_rate=30,
            resolution=(512, 512),
            size_bytes=1024000
        )
        assert metadata.video_path == "/path/to/video.mp4"
        assert metadata.duration == 30.0
        assert metadata.resolution == (512, 512)


class TestModelMetadata:
    """Tests for ModelMetadata model."""
    
    def test_valid_metadata(self):
        """Test valid model metadata creation."""
        metadata = ModelMetadata(
            model_path="/path/to/model.stl",
            vertex_count=1000,
            face_count=500,
            size_bytes=50000
        )
        assert metadata.model_path == "/path/to/model.stl"
        assert metadata.format == "stl"
        assert metadata.vertex_count == 1000