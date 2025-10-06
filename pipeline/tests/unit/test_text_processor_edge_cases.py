"""
Edge case tests for TextProcessor stage.
"""

import pytest
from src.stages.text_processor import TextProcessor
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestTextProcessorEdgeCases:
    """Edge case tests for TextProcessor."""
    
    async def test_minimum_length_text(self, test_config):
        """Test processing text at minimum length boundary."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Exactly 10 characters (minimum)
        input_data = {"text": "1234567890"}
        result = await processor.execute(input_data)
        
        assert "processed_text" in result
        assert len(result["original_text"]) >= 10
    
    async def test_maximum_length_text(self, test_config):
        """Test processing text at maximum length boundary."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Just under maximum (5000 chars)
        long_text = "A " * 2499  # 4998 characters
        input_data = {"text": long_text}
        result = await processor.execute(input_data)
        
        assert "processed_text" in result
        assert len(result["original_text"]) < 5000
    
    async def test_text_with_special_characters(self, test_config):
        """Test text with various special characters."""
        processor = TextProcessor(test_config["text_processor"])
        
        special_text = "Display with café, naïve design & bold 100% graphics! #marketing"
        result = await processor.process({"text": special_text})
        
        assert "processed_text" in result
        assert result["original_text"] == special_text
    
    async def test_text_with_numbers(self, test_config):
        """Test text with numerical values."""
        processor = TextProcessor(test_config["text_processor"])
        
        numeric_text = "Display stand 2.5 meters tall with 360 degree rotation and 24/7 lighting"
        result = await processor.process({"text": numeric_text})
        
        assert "processed_text" in result
        assert "keywords" in result
    
    async def test_text_with_unicode(self, test_config):
        """Test text with unicode characters."""
        processor = TextProcessor(test_config["text_processor"])
        
        unicode_text = "Modern display with ™ branding and © copyright symbols, € pricing"
        result = await processor.process({"text": unicode_text})
        
        assert "processed_text" in result
    
    async def test_text_with_multiple_spaces(self, test_config):
        """Test text normalization with excessive whitespace."""
        processor = TextProcessor(test_config["text_processor"])
        
        spaced_text = "Display    stand    with     multiple      spaces"
        normalized = await processor._normalize_text(spaced_text)
        
        # Should be normalized to single spaces
        assert "  " not in normalized
        assert "multiple spaces" in normalized
    
    async def test_text_with_newlines_and_tabs(self, test_config):
        """Test text with newlines and tabs."""
        processor = TextProcessor(test_config["text_processor"])
        
        formatted_text = "Display\nstand\twith\nformatting"
        normalized = await processor._normalize_text(formatted_text)
        
        # Newlines and tabs should be normalized to spaces
        assert "\n" not in normalized
        assert "\t" not in normalized
    
    async def test_text_without_ending_punctuation(self, test_config):
        """Test that text gets proper ending punctuation."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Display stand without punctuation"
        normalized = await processor._normalize_text(text)
        
        assert normalized.endswith(".")
    
    async def test_text_with_ending_punctuation(self, test_config):
        """Test that existing punctuation is preserved."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Display stand with punctuation!"
        normalized = await processor._normalize_text(text)
        
        assert normalized.endswith("!")
    
    async def test_empty_keywords_extraction(self, test_config):
        """Test keyword extraction with minimal content."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Text with mostly stop words
        text = "The a an and or but in on at to for of with"
        keywords = await processor._extract_keywords(text)
        
        # Should filter out all stop words
        assert len(keywords) == 0
    
    async def test_keyword_deduplication(self, test_config):
        """Test that duplicate keywords are removed."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "red display red stand red shelf red product"
        keywords = await processor._extract_keywords(text)
        
        # "red" should appear only once
        assert keywords.count("red") == 1
    
    async def test_no_colors_detected(self, test_config):
        """Test color extraction with no colors."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Modern display stand with premium product"
        colors = processor._extract_colors(text)
        
        assert len(colors) == 0
    
    async def test_multiple_colors_detected(self, test_config):
        """Test extraction of multiple colors."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Red and blue display with green accents and yellow highlights"
        colors = processor._extract_colors(text)
        
        assert "red" in colors
        assert "blue" in colors
        assert "green" in colors
        assert "yellow" in colors
        assert len(colors) == 4
    
    async def test_no_objects_detected(self, test_config):
        """Test object extraction with generic text."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Very nice amazing wonderful excellent"
        objects = processor._extract_objects(text)
        
        assert len(objects) == 0
    
    async def test_no_actions_detected(self, test_config):
        """Test action extraction with static description."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Static display stand with fixed position"
        actions = processor._extract_actions(text)
        
        assert len(actions) == 0
    
    async def test_enhancement_with_short_text(self, test_config):
        """Test text enhancement with very short input."""
        processor = TextProcessor(test_config["text_processor"])
        
        short_text = "Red display"
        enhanced = await processor._enhance_text(short_text, ["red", "display"])
        
        # Should be enhanced with context
        assert len(enhanced) > len(short_text)
        assert "display" in enhanced.lower()
    
    async def test_enhancement_with_long_text(self, test_config):
        """Test text enhancement with already long input."""
        processor = TextProcessor(test_config["text_processor"])
        
        long_text = "A very detailed description of a marketing display stand with many words and comprehensive details about the product placement and visual design elements"
        enhanced = await processor._enhance_text(long_text, ["detailed", "display"])
        
        # Should not significantly change already detailed text
        assert "display" in enhanced.lower()
    
    async def test_all_visual_elements_empty(self, test_config):
        """Test visual elements extraction with minimal input."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Very simple item"
        visual_elements = await processor._extract_visual_elements(text)
        
        assert "colors" in visual_elements
        assert "objects" in visual_elements
        assert "actions" in visual_elements
        assert "style_hints" in visual_elements
    
    async def test_all_visual_elements_present(self, test_config):
        """Test visual elements extraction with rich input."""
        processor = TextProcessor(test_config["text_processor"])
        
        text = "Modern red and blue rotating display stand with elegant design showing premium products"
        visual_elements = await processor._extract_visual_elements(text)
        
        assert len(visual_elements["colors"]) > 0
        assert len(visual_elements["objects"]) > 0
        assert len(visual_elements["actions"]) > 0
        assert len(visual_elements["style_hints"]) > 0
    
    async def test_suspicious_content_detection(self, test_config):
        """Test that suspicious content is rejected."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Test script tag
        with pytest.raises(ValidationError):
            await processor.validate({"text": "<script>alert('xss')</script>"}, is_input=True)
    
    async def test_null_byte_rejection(self, test_config):
        """Test that null bytes are rejected."""
        processor = TextProcessor(test_config["text_processor"])
        
        with pytest.raises(ValidationError):
            await processor.validate({"text": "Display\x00stand"}, is_input=True)
    
    async def test_non_string_input(self, test_config):
        """Test that non-string input is rejected."""
        processor = TextProcessor(test_config["text_processor"])
        
        with pytest.raises(ValidationError):
            await processor.validate({"text": 123}, is_input=True)
        
        with pytest.raises(ValidationError):
            await processor.validate({"text": ["list", "of", "words"]}, is_input=True)
    
    async def test_missing_text_field(self, test_config):
        """Test that missing text field is caught."""
        processor = TextProcessor(test_config["text_processor"])
        
        with pytest.raises(ValidationError) as exc_info:
            await processor.validate({}, is_input=True)
        
        assert "text" in str(exc_info.value).lower()
    
    async def test_output_validation_success(self, test_config):
        """Test output validation with valid data."""
        processor = TextProcessor(test_config["text_processor"])
        
        valid_output = {
            "processed_text": "Some text",
            "keywords": ["word1", "word2"],
            "visual_elements": {}
        }
        
        result = await processor.validate(valid_output, is_input=False)
        assert result is True
    
    async def test_output_validation_failure(self, test_config):
        """Test output validation with invalid data."""
        processor = TextProcessor(test_config["text_processor"])
        
        # Missing required fields
        invalid_output = {
            "processed_text": "Some text"
        }
        
        with pytest.raises(ValidationError):
            await processor.validate(invalid_output, is_input=False)
