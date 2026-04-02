"""
Text processing stage for marketing POS descriptions.
"""

import re
from typing import Dict, Any, List
import asyncio

from ..core.base import PipelineStage, ValidationError, ProcessingError
from ..utils.validators import InputValidator


class TextProcessor(PipelineStage):
    """
    Processes marketing POS text descriptions.
    
    Validates, normalizes, and enhances text input for video generation.
    """
    
    def _setup(self):
        """Initialize text processor."""
        self.validator = InputValidator()
        self.max_length = self.get_config("max_text_length", 5000)
        self.min_length = self.get_config("min_text_length", 10)
        self.enable_enhancement = self.get_config("enable_enhancement", True)
    
    async def validate(self, data: Dict[str, Any], is_input: bool = True) -> bool:
        """
        Validate text input or output.
        
        Args:
            data: Data to validate
            is_input: True for input validation, False for output
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        if is_input:
            # Validate input has required 'text' field
            if "text" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Missing required field: 'text'"
                )
            
            # Validate text content
            text = data["text"]
            if not isinstance(text, str):
                raise ValidationError(
                    stage=self.stage_name,
                    message="'text' field must be a string"
                )
            
            # Use validator for detailed checks
            try:
                self.validator.validate_text_input(text)
            except Exception as e:
                raise ValidationError(
                    stage=self.stage_name,
                    message=f"Text validation failed: {str(e)}"
                )
        else:
            # Validate output has processed text
            if "processed_text" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Output missing 'processed_text' field"
                )
            
            if "keywords" not in data:
                raise ValidationError(
                    stage=self.stage_name,
                    message="Output missing 'keywords' field"
                )
        
        return True
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process text description.
        
        Args:
            input_data: Dictionary containing 'text' field
            
        Returns:
            Dictionary with processed text and metadata
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            text = input_data["text"]
            
            # Normalize text
            normalized_text = await self._normalize_text(text)
            
            # Extract keywords and entities
            keywords = await self._extract_keywords(normalized_text)
            
            # Enhance text if enabled
            if self.enable_enhancement:
                enhanced_text = await self._enhance_text(normalized_text, keywords)
            else:
                enhanced_text = normalized_text
            
            # Extract visual elements
            visual_elements = await self._extract_visual_elements(enhanced_text)
            
            return {
                "original_text": text,
                "processed_text": enhanced_text,
                "normalized_text": normalized_text,
                "keywords": keywords,
                "visual_elements": visual_elements,
                "text_length": len(enhanced_text),
                "word_count": len(enhanced_text.split())
            }
            
        except Exception as e:
            raise ProcessingError(
                stage=self.stage_name,
                message=f"Text processing failed: {str(e)}",
                details={"exception_type": type(e).__name__}
            )
    
    async def _normalize_text(self, text: str) -> str:
        """
        Normalize text input.
        
        Args:
            text: Raw text input
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        normalized = normalized.strip()
        
        # Ensure proper sentence endings
        if normalized and normalized[-1] not in '.!?':
            normalized += '.'
        
        return normalized
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (in production, use NLP libraries)
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'it', 'its'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        
        # Get unique keywords, maintain order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        # Return top keywords
        return unique_keywords[:20]
    
    async def _enhance_text(self, text: str, keywords: List[str]) -> str:
        """
        Enhance text for better video generation.
        
        Args:
            text: Normalized text
            keywords: Extracted keywords
            
        Returns:
            Enhanced text
        """
        # Add visual cues based on keywords
        enhanced = text
        
        # Ensure text is descriptive enough for video generation
        if len(text.split()) < 20:
            # Add descriptive context
            enhanced = f"A marketing display featuring {text}"
        
        return enhanced
    
    async def _extract_visual_elements(self, text: str) -> Dict[str, Any]:
        """
        Extract visual elements mentioned in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of visual elements
        """
        visual_elements = {
            "colors": self._extract_colors(text),
            "objects": self._extract_objects(text),
            "actions": self._extract_actions(text),
            "style_hints": self._extract_style_hints(text)
        }
        
        return visual_elements
    
    def _extract_colors(self, text: str) -> List[str]:
        """Extract color mentions from text."""
        color_patterns = [
            r'\b(red|blue|green|yellow|orange|purple|pink|black|white|gray|grey|brown|gold|silver)\b'
        ]
        
        colors = []
        for pattern in color_patterns:
            matches = re.findall(pattern, text.lower())
            colors.extend(matches)
        
        return list(set(colors))
    
    def _extract_objects(self, text: str) -> List[str]:
        """Extract object mentions from text."""
        # Common POS display objects
        object_keywords = [
            'display', 'stand', 'shelf', 'rack', 'banner', 'sign', 'poster',
            'product', 'box', 'package', 'container', 'bottle', 'can',
            'logo', 'brand', 'text', 'image', 'graphic'
        ]
        
        objects = []
        text_lower = text.lower()
        for obj in object_keywords:
            if obj in text_lower:
                objects.append(obj)
        
        return objects
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract action words from text."""
        action_patterns = [
            r'\b(rotating|spinning|moving|displaying|showing|featuring|presenting)\b'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text.lower())
            actions.extend(matches)
        
        return list(set(actions))
    
    def _extract_style_hints(self, text: str) -> List[str]:
        """Extract style-related hints from text."""
        style_keywords = [
            'modern', 'classic', 'elegant', 'bold', 'minimal', 'vibrant',
            'professional', 'playful', 'luxurious', 'simple', 'complex'
        ]
        
        styles = []
        text_lower = text.lower()
        for style in style_keywords:
            if style in text_lower:
                styles.append(style)
        
        return styles
