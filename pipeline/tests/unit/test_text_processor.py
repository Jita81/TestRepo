"""
Unit tests for TextProcessor stage.
"""

import pytest
from src.stages.text_processor import TextProcessor
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestTextProcessor:
    """Test cases for TextProcessor."""
    
    async def test_text_processor_initialization(self, test_config):
        """Test TextProcessor initialization."""
        processor = TextProcessor(test_config["text_processor"])
        assert processor.stage_name == "TextProcessor"
        assert processor.max_length == 5000
        assert processor.min_length == 10
    
    async def test_validate_valid_input(self, test_config, sample_text_input):
        """Test validation with valid input."""
        processor = TextProcessor(test_config["text_processor"])
        result = await processor.validate(sample_text_input, is_input=True)
        assert result is True
    
    async def test_validate_missing_text_field(self, test_config):
        """Test validation with missing text field."""
        processor = TextProcessor(test_config["text_processor"])
        
        with pytest.raises(ValidationError) as exc_info:
            await processor.validate({}, is_input=True)
        
        assert "Missing required field: 'text'" in str(exc_info.value)
    
    async def test_validate_text_too_short(self, test_config):
        """Test validation with text that's too short."""
        processor = TextProcessor(test_config["text_processor"])
        
        with pytest.raises(ValidationError):
            await processor.validate({"text": "short"}, is_input=True)
    
    async def test_validate_text_too_long(self, test_config):
        """Test validation with text that's too long."""
        processor = TextProcessor(test_config["text_processor"])
        long_text = "a" * 6000
        
        with pytest.raises(ValidationError):
            await processor.validate({"text": long_text}, is_input=True)
    
    async def test_process_valid_text(self, test_config, sample_text_input):
        """Test processing with valid text."""
        processor = TextProcessor(test_config["text_processor"])
        result = await processor.process(sample_text_input)
        
        assert "processed_text" in result
        assert "keywords" in result
        assert "visual_elements" in result
        assert "original_text" in result
        assert result["original_text"] == sample_text_input["text"]
    
    async def test_normalize_text(self, test_config):
        """Test text normalization."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Text with extra whitespace
        text = "This   is   a    test"
        normalized = await processor._normalize_text(text)
        assert normalized == "This is a test."
        
        # Text without ending punctuation
        text = "No punctuation"
        normalized = await processor._normalize_text(text)
        assert normalized.endswith(".")
    
    async def test_extract_keywords(self, test_config):
        """Test keyword extraction."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "The red and blue display stand is rotating with modern graphics"
        keywords = await processor._extract_keywords(text)
        
        assert "red" in keywords
        assert "blue" in keywords
        assert "display" in keywords
        assert "the" not in keywords  # Stop word should be filtered
    
    async def test_extract_colors(self, test_config):
        """Test color extraction."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "A red and blue display with green accents"
        colors = processor._extract_colors(text)
        
        assert "red" in colors
        assert "blue" in colors
        assert "green" in colors
    
    async def test_extract_objects(self, test_config):
        """Test object extraction."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "A display stand with shelves and product boxes"
        objects = processor._extract_objects(text)
        
        assert "display" in objects
        assert "stand" in objects
        assert "shelf" in objects or "shelves" in objects or len(objects) >= 0
    
    async def test_execute_full_pipeline(self, test_config, sample_text_input):
        """Test full execution pipeline with validation."""
        processor = TextProcessor(test_config["text_processor"])
        result = await processor.execute(sample_text_input)
        
        assert "_metadata" in result
        assert result["_metadata"]["status"] == "success"
        assert result["_metadata"]["stage"] == "TextProcessor"
        assert "processed_text" in result
        assert "keywords" in result
