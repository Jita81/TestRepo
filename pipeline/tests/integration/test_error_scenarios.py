"""
Integration tests for error scenarios and edge cases.
"""

import pytest
from pathlib import Path
from src.core.orchestrator import PipelineOrchestrator
from src.core.status_tracker import StatusTracker, PipelineStatus
from src.stages.text_processor import TextProcessor
from src.stages.video_generator import VideoGenerator
from src.stages.model_converter import ModelConverter
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestErrorScenarios:
    """Test error handling throughout the pipeline."""
    
    async def test_invalid_text_length_too_short(self, test_config, temp_dir):
        """Test pipeline with text that's too short."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"text": "short"})
    
    async def test_invalid_text_length_too_long(self, test_config, temp_dir):
        """Test pipeline with text that's too long."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        long_text = "a" * 6000
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"text": long_text})
    
    async def test_invalid_text_type(self, test_config, temp_dir):
        """Test pipeline with non-string text."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"text": 12345})
    
    async def test_missing_text_field(self, test_config, temp_dir):
        """Test pipeline with missing text field."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"other_field": "value"})
    
    async def test_suspicious_content_script_tag(self, test_config, temp_dir):
        """Test pipeline rejects script tags."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({
                "text": "<script>alert('xss')</script> malicious content here"
            })
    
    async def test_suspicious_content_javascript(self, test_config, temp_dir):
        """Test pipeline rejects javascript: URLs."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({
                "text": "javascript:alert('xss') malicious content here with extra text"
            })
    
    async def test_null_byte_in_text(self, test_config, temp_dir):
        """Test pipeline rejects null bytes."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({
                "text": "Display stand\x00with null byte and more content here"
            })
    
    async def test_status_tracking_on_error(self, test_config, temp_dir):
        """Test that status is tracked correctly when error occurs."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        execution_id = "test_error_001"
        
        try:
            await orchestrator.execute_pipeline(
                {"text": "short"},
                execution_id=execution_id
            )
        except ValidationError:
            pass
        
        # Check that error was tracked
        status = await tracker.get_status(execution_id)
        assert status is not None
        assert status["status"] == PipelineStatus.FAILED.value
    
    async def test_multiple_errors_in_sequence(self, test_config, temp_dir):
        """Test multiple sequential errors."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        # First error
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"text": "short"}, execution_id="err1")
        
        # Second error
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({"text": 123}, execution_id="err2")
        
        # Both should be tracked
        status1 = await tracker.get_status("err1")
        status2 = await tracker.get_status("err2")
        
        assert status1["status"] == PipelineStatus.FAILED.value
        assert status2["status"] == PipelineStatus.FAILED.value
    
    async def test_empty_input_data(self, test_config, temp_dir):
        """Test pipeline with completely empty input."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        with pytest.raises(ValidationError):
            await orchestrator.execute_pipeline({})


@pytest.mark.asyncio
class TestBoundaryConditions:
    """Test boundary conditions for pipeline stages."""
    
    async def test_minimum_valid_text(self, test_config, temp_dir):
        """Test with minimum valid text length."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        # Exactly 10 characters (minimum)
        result = await orchestrator.execute_pipeline({"text": "1234567890"})
        
        assert "processed_text" in result
        assert result["_metadata"]["status"] == "success"
    
    async def test_maximum_valid_text(self, test_config, temp_dir):
        """Test with maximum valid text length."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        # Just under maximum (4999 characters)
        max_text = "a " * 2499  # 4998 characters
        result = await orchestrator.execute_pipeline({"text": max_text})
        
        assert "processed_text" in result
        assert result["_metadata"]["status"] == "success"
    
    async def test_unicode_text_processing(self, test_config, temp_dir):
        """Test processing of unicode characters."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        unicode_text = "Display with café, naïve design, € pricing and ™ branding elements"
        result = await orchestrator.execute_pipeline({"text": unicode_text})
        
        assert "processed_text" in result
        assert result["original_text"] == unicode_text
    
    async def test_special_characters(self, test_config, temp_dir):
        """Test text with special characters."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        special_text = "Display! Stand? With: special; characters, & more... 100%"
        result = await orchestrator.execute_pipeline({"text": special_text})
        
        assert "processed_text" in result
    
    async def test_numbers_in_text(self, test_config, temp_dir):
        """Test text with numerical values."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        numeric_text = "Display 2.5 meters tall, 360 degrees rotation, 24/7 operation, 100% visible"
        result = await orchestrator.execute_pipeline({"text": numeric_text})
        
        assert "processed_text" in result
        assert "keywords" in result


@pytest.mark.asyncio
class TestConcurrentExecution:
    """Test concurrent pipeline execution scenarios."""
    
    async def test_multiple_sequential_executions(self, test_config, temp_dir):
        """Test multiple sequential pipeline executions."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        # Execute multiple times
        texts = [
            "First display stand with modern design",
            "Second display with vibrant colors",
            "Third stand featuring premium products"
        ]
        
        results = []
        for i, text in enumerate(texts):
            result = await orchestrator.execute_pipeline(
                {"text": text},
                execution_id=f"exec_{i}"
            )
            results.append(result)
        
        # All should succeed
        assert len(results) == 3
        for result in results:
            assert "processed_text" in result
        
        # Check all statuses
        executions = await tracker.list_executions()
        assert len(executions) >= 3
    
    async def test_execution_id_uniqueness(self, test_config, temp_dir):
        """Test that execution IDs are unique."""
        tracker = StatusTracker(persist_path=temp_dir / "status.json")
        orchestrator = PipelineOrchestrator(status_tracker=tracker)
        orchestrator.add_stage(TextProcessor(test_config["text_processor"]))
        
        result1 = await orchestrator.execute_pipeline({
            "text": "First display stand with unique content"
        })
        
        result2 = await orchestrator.execute_pipeline({
            "text": "Second display stand with different content"
        })
        
        assert result1["execution_id"] != result2["execution_id"]
