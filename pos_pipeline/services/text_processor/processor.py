"""
Text Processing Service for the POS Pipeline.

This service validates and preprocesses input text for video generation.
"""
import asyncio
import time
import re
from typing import Dict, Any
import bleach
from utils.logging_config import get_logger
from utils.exceptions import ValidationError, TextProcessingError
from models.schemas import TextProcessingResult
from config.settings import settings


logger = get_logger("text_processor")


class TextProcessor:
    """Handles text validation and preprocessing for the pipeline."""
    
    def __init__(self):
        self.max_tokens = settings.max_text_length
        self.logger = logger
        
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize input text by removing potentially harmful characters.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text string
        """
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Clean HTML tags if present
        text = bleach.clean(text, tags=[], strip=True)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove non-printable characters except common punctuation
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text
    
    def _validate_length(self, text: str) -> None:
        """
        Validate text length is within acceptable limits.
        
        Args:
            text: Text to validate
            
        Raises:
            ValidationError: If text length exceeds limits
        """
        if not text or len(text.strip()) == 0:
            raise ValidationError(
                "Text cannot be empty or whitespace only",
                details={"length": len(text)}
            )
        
        if len(text) > self.max_tokens:
            raise ValidationError(
                f"Text exceeds maximum length of {self.max_tokens} characters",
                details={"length": len(text), "max_length": self.max_tokens}
            )
    
    def _validate_content(self, text: str) -> None:
        """
        Validate text content for meaningful input.
        
        Args:
            text: Text to validate
            
        Raises:
            ValidationError: If text content is invalid
        """
        # Check for minimum meaningful content
        words = text.split()
        if len(words) < 3:
            raise ValidationError(
                "Text must contain at least 3 words for meaningful processing",
                details={"word_count": len(words)}
            )
        
        # Check for unicode handling
        try:
            text.encode('utf-8')
        except UnicodeEncodeError as e:
            raise ValidationError(
                "Text contains invalid unicode characters",
                details={"error": str(e)}
            )
    
    def _extract_keywords(self, text: str) -> list:
        """
        Extract key descriptive words from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        
        # Common stop words to filter
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    async def validate_input(self, text: str) -> bool:
        """
        Validate input text meets all requirements.
        
        Args:
            text: Text to validate
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            self._validate_length(text)
            self._validate_content(text)
            self.logger.info(f"Input validation successful for text of length {len(text)}")
            return True
        except ValidationError as e:
            self.logger.error(f"Input validation failed: {e.message}")
            raise
    
    async def process(self, job_id: str, text: str) -> TextProcessingResult:
        """
        Process input text for video generation.
        
        Args:
            job_id: Unique job identifier
            text: Input text to process
            
        Returns:
            TextProcessingResult with processed text and metadata
            
        Raises:
            TextProcessingError: If processing fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting text processing for job {job_id}")
            
            # Validate input
            await self.validate_input(text)
            
            # Sanitize text
            processed_text = self._sanitize_text(text)
            self.logger.debug(f"Text sanitized: {processed_text[:100]}...")
            
            # Extract metadata
            keywords = self._extract_keywords(processed_text)
            token_count = len(processed_text.split())
            
            # Simulate processing delay (can be replaced with actual NLP processing)
            await asyncio.sleep(0.5)
            
            processing_time = time.time() - start_time
            
            result = TextProcessingResult(
                job_id=job_id,
                processed_text=processed_text,
                token_count=token_count,
                metadata={
                    "keywords": keywords,
                    "original_length": len(text),
                    "processed_length": len(processed_text)
                },
                processing_time=processing_time
            )
            
            self.logger.info(
                f"Text processing completed for job {job_id} in {processing_time:.2f}s"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Text processing failed for job {job_id}: {str(e)}")
            raise TextProcessingError(
                f"Failed to process text: {str(e)}",
                details={"job_id": job_id, "error": str(e)}
            )