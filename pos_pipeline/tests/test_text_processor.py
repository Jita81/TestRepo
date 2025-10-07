"""
Unit tests for Text Processing Service.
"""
import pytest
from services.text_processor import TextProcessor
from utils.exceptions import ValidationError, TextProcessingError


class TestTextProcessor:
    """Tests for TextProcessor class."""
    
    @pytest.mark.asyncio
    async def test_validate_input_success(self, text_processor, sample_text):
        """Test successful input validation."""
        result = await text_processor.validate_input(sample_text)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_empty_text(self, text_processor):
        """Test validation fails for empty text."""
        with pytest.raises(ValidationError) as exc_info:
            await text_processor.validate_input("")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_validate_whitespace_only(self, text_processor):
        """Test validation fails for whitespace-only text."""
        with pytest.raises(ValidationError) as exc_info:
            await text_processor.validate_input("   \n\t  ")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_validate_too_long(self, text_processor):
        """Test validation fails for text exceeding max length."""
        long_text = "word " * 300  # Exceeds max_tokens
        
        with pytest.raises(ValidationError) as exc_info:
            await text_processor.validate_input(long_text)
        
        assert "exceeds maximum length" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_validate_too_few_words(self, text_processor):
        """Test validation fails for insufficient words."""
        with pytest.raises(ValidationError) as exc_info:
            await text_processor.validate_input("Two words")
        
        assert "at least 3 words" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_sanitize_text(self, text_processor):
        """Test text sanitization."""
        dirty_text = "Test  \x00 <script>alert('xss')</script>  multiple   spaces"
        sanitized = text_processor._sanitize_text(dirty_text)
        
        assert "\x00" not in sanitized
        assert "<script>" not in sanitized
        assert "  " not in sanitized  # Multiple spaces normalized
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, text_processor, sample_text):
        """Test keyword extraction."""
        keywords = text_processor._extract_keywords(sample_text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "modern" in keywords
        assert "display" in keywords
        # Stop words should be filtered
        assert "a" not in keywords
        assert "for" not in keywords
    
    @pytest.mark.asyncio
    async def test_process_success(self, text_processor, sample_text):
        """Test successful text processing."""
        result = await text_processor.process("test-job-123", sample_text)
        
        assert result.job_id == "test-job-123"
        assert result.processed_text
        assert result.token_count > 0
        assert "keywords" in result.metadata
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_process_preserves_meaning(self, text_processor):
        """Test processing preserves text meaning."""
        original = "Display modern electronics with red and white colors"
        result = await text_processor.process("test-job", original)
        
        # Key words should be preserved
        processed_lower = result.processed_text.lower()
        assert "display" in processed_lower
        assert "modern" in processed_lower
        assert "electronics" in processed_lower


class TestTextProcessorEdgeCases:
    """Test edge cases for TextProcessor."""
    
    @pytest.mark.asyncio
    async def test_unicode_text(self, text_processor):
        """Test handling of unicode characters."""
        unicode_text = "Modern POS display 日本語 العربية with emoji 🎨"
        result = await text_processor.process("test-job", unicode_text)
        
        assert result.processed_text
        assert result.token_count > 0
    
    @pytest.mark.asyncio
    async def test_special_characters(self, text_processor):
        """Test handling of special characters."""
        special_text = "POS display with 50% discount! Now $99.99 (was $199.99)"
        result = await text_processor.process("test-job", special_text)
        
        assert result.processed_text
        assert "$" in result.processed_text or "99.99" in result.processed_text
    
    @pytest.mark.asyncio
    async def test_multiple_languages_mixed(self, text_processor):
        """Test mixed language text."""
        mixed_text = "Modern POS display moderne Anzeige display moderno"
        result = await text_processor.process("test-job", mixed_text)
        
        assert result.processed_text
        assert "display" in result.processed_text.lower()