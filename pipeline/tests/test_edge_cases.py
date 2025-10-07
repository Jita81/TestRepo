"""Tests for edge cases and error scenarios."""

import pytest
from pydantic import ValidationError
from common.models import TextInput, PipelineMessage, PipelineStage, PipelineStatus
from common.exceptions import PipelineError


class TestInputEdgeCases:
    """Edge case tests for input validation."""
    
    def test_description_with_newlines(self):
        """Test description with newline characters."""
        input_data = TextInput(description="Line 1\nLine 2\nLine 3 with enough length")
        assert "\n" in input_data.description
    
    def test_description_with_tabs(self):
        """Test description with tab characters."""
        input_data = TextInput(description="Column1\tColumn2\tColumn3 with length")
        assert "\t" in input_data.description
    
    def test_description_all_spaces(self):
        """Test description with only spaces."""
        with pytest.raises(ValidationError):
            # After stripping, this will be empty
            TextInput(description="          ")
    
    def test_description_leading_trailing_newlines(self):
        """Test description with leading/trailing newlines."""
        input_data = TextInput(description="\n\nTest description with enough length\n\n")
        # Should be stripped
        assert not input_data.description.startswith("\n")
    
    def test_very_long_metadata_key(self):
        """Test metadata with very long key."""
        long_key = "k" * 1000
        metadata = {long_key: "value"}
        input_data = TextInput(
            description="Test description",
            metadata=metadata
        )
        assert long_key in input_data.metadata
    
    def test_metadata_with_none_values(self):
        """Test metadata with None values."""
        metadata = {"key1": None, "key2": "value"}
        input_data = TextInput(
            description="Test description",
            metadata=metadata
        )
        assert input_data.metadata["key1"] is None
    
    def test_metadata_with_numeric_values(self):
        """Test metadata with various numeric types."""
        metadata = {
            "int": 123,
            "float": 45.67,
            "negative": -10,
            "zero": 0
        }
        input_data = TextInput(
            description="Test description",
            metadata=metadata
        )
        assert input_data.metadata["int"] == 123
        assert input_data.metadata["float"] == 45.67


class TestPipelineMessageEdgeCases:
    """Edge case tests for pipeline messages."""
    
    def test_message_with_empty_payload(self):
        """Test message with empty payload."""
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload={},
            status=PipelineStatus.PENDING
        )
        assert message.payload == {}
    
    def test_message_with_large_payload(self):
        """Test message with large payload."""
        large_data = {"data": "x" * 10000}
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload=large_data,
            status=PipelineStatus.PENDING
        )
        assert len(message.payload["data"]) == 10000
    
    def test_message_with_nested_payload(self):
        """Test message with deeply nested payload."""
        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": "deep"
                    }
                }
            }
        }
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload=nested,
            status=PipelineStatus.PENDING
        )
        assert message.payload["level1"]["level2"]["level3"]["data"] == "deep"
    
    def test_message_high_retry_count(self):
        """Test message with high retry count."""
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.INPUT,
            payload={},
            status=PipelineStatus.PENDING,
            retry_count=100
        )
        assert message.retry_count == 100
    
    def test_message_with_error(self):
        """Test message with error information."""
        message = PipelineMessage(
            request_id="req_123",
            stage=PipelineStage.VIDEO_GENERATION,
            payload={},
            status=PipelineStatus.FAILED,
            error_message="Generation failed due to timeout"
        )
        assert message.error_message == "Generation failed due to timeout"
        assert message.status == PipelineStatus.FAILED


class TestConcurrencyEdgeCases:
    """Edge cases related to concurrent operations."""
    
    def test_same_request_id_different_stages(self):
        """Test handling same request ID at different stages."""
        message1 = PipelineMessage(
            request_id="req_same",
            stage=PipelineStage.INPUT,
            payload={},
            status=PipelineStatus.PENDING
        )
        message2 = PipelineMessage(
            request_id="req_same",
            stage=PipelineStage.VIDEO_GENERATION,
            payload={},
            status=PipelineStatus.PROCESSING
        )
        
        assert message1.request_id == message2.request_id
        assert message1.stage != message2.stage
    
    def test_multiple_requests_same_description(self):
        """Test multiple requests with identical descriptions."""
        desc = "Identical description for multiple requests"
        input1 = TextInput(description=desc)
        input2 = TextInput(description=desc)
        
        assert input1.description == input2.description
        # They should still be separate objects
        assert input1 is not input2


class TestResourceLimitEdgeCases:
    """Edge cases for resource limits."""
    
    def test_zero_duration_video_metadata(self):
        """Test handling zero duration video."""
        from common.models import VideoMetadata
        
        metadata = VideoMetadata(
            video_path="/path/to/video.mp4",
            duration=0.0,
            frame_rate=30,
            resolution=(512, 512),
            size_bytes=0
        )
        assert metadata.duration == 0.0
    
    def test_zero_size_model_metadata(self):
        """Test handling zero size model."""
        from common.models import ModelMetadata
        
        metadata = ModelMetadata(
            model_path="/path/to/model.stl",
            vertex_count=0,
            face_count=0,
            size_bytes=0
        )
        assert metadata.vertex_count == 0
        assert metadata.face_count == 0


class TestErrorPropagation:
    """Test error handling and propagation."""
    
    def test_pipeline_error_preserves_stage(self):
        """Test that errors preserve stage information."""
        error = PipelineError("video_generation", "Test error")
        
        try:
            raise error
        except PipelineError as e:
            assert e.stage == "video_generation"
            assert e.message == "Test error"
    
    def test_error_with_complex_details(self):
        """Test error with complex details object."""
        details = {
            "timestamp": "2025-10-07T12:00:00",
            "request_id": "req_123",
            "error_code": 500,
            "stack_trace": ["line1", "line2", "line3"],
            "metadata": {"key": "value"}
        }
        error = PipelineError("test", "Complex error", details)
        
        assert error.details["error_code"] == 500
        assert len(error.details["stack_trace"]) == 3