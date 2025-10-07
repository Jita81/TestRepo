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
        input_data = TextInput(description="  Test description  ")
        assert input_data.description == "Test description"
    
    def test_default_metadata(self):
        """Test default metadata is empty dict."""
        input_data = TextInput(description="Test description")
        assert input_data.metadata == {}


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