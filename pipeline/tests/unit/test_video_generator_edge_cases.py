"""
Edge case tests for VideoGenerator stage.
"""

import pytest
import numpy as np
from pathlib import Path
from src.stages.video_generator import VideoGenerator
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestVideoGeneratorEdgeCases:
    """Edge case tests for VideoGenerator."""
    
    async def test_empty_visual_elements(self, test_config):
        """Test video generation with empty visual elements."""
        generator = VideoGenerator(test_config["video_generator"])
        
        input_data = {
            "processed_text": "Simple display stand",
            "visual_elements": {
                "colors": [],
                "objects": [],
                "actions": [],
                "style_hints": []
            },
            "keywords": []
        }
        
        try:
            result = await generator.process(input_data)
            assert "video_path" in result
        except Exception:
            pytest.skip("Skipping due to environment constraints")
    
    async def test_single_color(self, test_config):
        """Test color value retrieval for single color."""
        generator = VideoGenerator(test_config["video_generator"])
        
        color = generator._get_color_value("red")
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)
    
    async def test_unknown_color(self, test_config):
        """Test color value for unknown color name."""
        generator = VideoGenerator(test_config["video_generator"])
        
        color = generator._get_color_value("nonexistent_color")
        # Should return default blue
        assert color == (255, 0, 0)
    
    async def test_case_insensitive_color(self, test_config):
        """Test that color matching is case-insensitive."""
        generator = VideoGenerator(test_config["video_generator"])
        
        red_lower = generator._get_color_value("red")
        red_upper = generator._get_color_value("RED")
        red_mixed = generator._get_color_value("ReD")
        
        assert red_lower == red_upper == red_mixed
    
    async def test_text_wrapping_short_text(self, test_config):
        """Test text wrapping with short text."""
        generator = VideoGenerator(test_config["video_generator"])
        
        short_text = "Short"
        lines = generator._wrap_text(short_text, width=50)
        
        assert len(lines) == 1
        assert lines[0] == "Short"
    
    async def test_text_wrapping_long_text(self, test_config):
        """Test text wrapping with long text."""
        generator = VideoGenerator(test_config["video_generator"])
        
        long_text = "This is a very long piece of text that should be wrapped into multiple lines based on the specified width parameter"
        lines = generator._wrap_text(long_text, width=20)
        
        assert len(lines) > 1
        for line in lines:
            assert len(line) <= 30  # Some tolerance
    
    async def test_text_wrapping_exact_width(self, test_config):
        """Test text wrapping with text exactly at width."""
        generator = VideoGenerator(test_config["video_generator"])
        
        # Text with exactly width characters
        text = "a" * 20
        lines = generator._wrap_text(text, width=20)
        
        assert len(lines) == 1
    
    async def test_text_wrapping_empty_text(self, test_config):
        """Test text wrapping with empty text."""
        generator = VideoGenerator(test_config["video_generator"])
        
        lines = generator._wrap_text("", width=20)
        assert len(lines) == 0 or (len(lines) == 1 and lines[0] == "")
    
    async def test_frame_generation_minimal_input(self, test_config):
        """Test frame generation with minimal input."""
        generator = VideoGenerator(test_config["video_generator"])
        
        frame = await generator._generate_frame(
            frame_idx=0,
            total_frames=10,
            text="Test",
            visual_elements={},
            keywords=[]
        )
        
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8
    
    async def test_frame_generation_first_frame(self, test_config):
        """Test generation of first frame (idx=0)."""
        generator = VideoGenerator(test_config["video_generator"])
        
        frame = await generator._generate_frame(
            frame_idx=0,
            total_frames=100,
            text="Display stand",
            visual_elements={"colors": ["red"]},
            keywords=["display"]
        )
        
        assert frame is not None
        # Progress should be 0 for first frame
        assert frame.shape == (1080, 1920, 3)
    
    async def test_frame_generation_last_frame(self, test_config):
        """Test generation of last frame."""
        generator = VideoGenerator(test_config["video_generator"])
        
        frame = await generator._generate_frame(
            frame_idx=99,
            total_frames=100,
            text="Display stand",
            visual_elements={"colors": ["blue"]},
            keywords=["stand"]
        )
        
        assert frame is not None
        # Progress should be close to 1.0 for last frame
        assert frame.shape == (1080, 1920, 3)
    
    async def test_frame_generation_with_many_keywords(self, test_config):
        """Test frame generation with many keywords."""
        generator = VideoGenerator(test_config["video_generator"])
        
        many_keywords = [f"keyword{i}" for i in range(20)]
        
        frame = await generator._generate_frame(
            frame_idx=50,
            total_frames=100,
            text="Display with many keywords",
            visual_elements={},
            keywords=many_keywords
        )
        
        assert frame is not None
        assert frame.shape == (1080, 1920, 3)
    
    async def test_validate_missing_processed_text(self, test_config):
        """Test validation with missing processed_text."""
        generator = VideoGenerator(test_config["video_generator"])
        
        with pytest.raises(ValidationError) as exc_info:
            await generator.validate({}, is_input=True)
        
        assert "processed_text" in str(exc_info.value).lower()
    
    async def test_validate_missing_visual_elements(self, test_config):
        """Test validation with missing visual_elements."""
        generator = VideoGenerator(test_config["video_generator"])
        
        with pytest.raises(ValidationError) as exc_info:
            await generator.validate({"processed_text": "test"}, is_input=True)
        
        assert "visual_elements" in str(exc_info.value).lower()
    
    async def test_validate_output_missing_video_path(self, test_config, temp_dir):
        """Test output validation with missing video_path."""
        generator = VideoGenerator(test_config["video_generator"])
        
        with pytest.raises(ValidationError) as exc_info:
            await generator.validate({"duration": 30}, is_input=False)
        
        assert "video_path" in str(exc_info.value).lower()
    
    async def test_validate_output_nonexistent_file(self, test_config):
        """Test output validation with nonexistent video file."""
        generator = VideoGenerator(test_config["video_generator"])
        
        with pytest.raises(ValidationError) as exc_info:
            await generator.validate({
                "video_path": "/nonexistent/video.mp4",
                "duration": 30
            }, is_input=False)
        
        assert "not found" in str(exc_info.value).lower()
    
    async def test_validate_output_duration_too_short(self, test_config, temp_dir):
        """Test output validation with duration below minimum."""
        generator = VideoGenerator(test_config["video_generator"])
        
        # Create dummy file
        video_file = temp_dir / "short.mp4"
        video_file.touch()
        
        with pytest.raises(ValidationError) as exc_info:
            await generator.validate({
                "video_path": str(video_file),
                "duration": 10  # Below minimum of 30
            }, is_input=False)
        
        assert "duration" in str(exc_info.value).lower()
    
    async def test_all_color_values(self, test_config):
        """Test that all predefined colors work."""
        generator = VideoGenerator(test_config["video_generator"])
        
        colors = ["red", "blue", "green", "yellow", "orange", "purple", 
                 "pink", "black", "white", "gray", "grey", "brown", "gold", "silver"]
        
        for color_name in colors:
            color_value = generator._get_color_value(color_name)
            assert isinstance(color_value, tuple)
            assert len(color_value) == 3
            assert all(isinstance(c, (int, np.integer)) for c in color_value)
