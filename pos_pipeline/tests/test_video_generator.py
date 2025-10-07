"""
Unit tests for Video Generation Service.
"""
import pytest
import asyncio
from pathlib import Path
from services.video_generator import VideoGenerator
from utils.exceptions import VideoGenerationError, StorageError


class TestVideoGenerator:
    """Tests for VideoGenerator class."""
    
    @pytest.mark.asyncio
    async def test_generate_video_success(self, video_generator, sample_text):
        """Test successful video generation."""
        result = await video_generator.generate_video(
            "test-job-123",
            sample_text,
            duration=30
        )
        
        assert result.job_id == "test-job-123"
        assert Path(result.video_path).exists()
        assert result.duration == 30
        assert result.format == "mp4"
        assert result.fps > 0
        assert result.file_size_mb > 0
        assert result.processing_time > 0
        
        # Verify file exists and has content
        video_file = Path(result.video_path)
        assert video_file.stat().st_size > 0
    
    @pytest.mark.asyncio
    async def test_minimum_duration_validation(self, video_generator, sample_text):
        """Test video duration must meet minimum."""
        with pytest.raises(VideoGenerationError) as exc_info:
            await video_generator.generate_video(
                "test-job",
                sample_text,
                duration=10  # Less than minimum
            )
        
        assert "at least" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_video_format(self, video_generator, sample_text):
        """Test video is in correct format."""
        result = await video_generator.generate_video(
            "test-job",
            sample_text
        )
        
        assert result.format == "mp4"
        assert result.video_path.endswith(".mp4")
    
    @pytest.mark.asyncio
    async def test_video_resolution(self, video_generator, sample_text):
        """Test video has correct resolution."""
        result = await video_generator.generate_video(
            "test-job",
            sample_text
        )
        
        assert result.resolution == (512, 512)
    
    @pytest.mark.asyncio
    async def test_video_url_generation(self, video_generator, sample_text):
        """Test video URL is generated correctly."""
        result = await video_generator.generate_video(
            "test-job-xyz",
            sample_text
        )
        
        assert result.video_url.startswith("/storage/videos/")
        assert "test-job-xyz" in result.video_url
        assert result.video_url.endswith(".mp4")
    
    @pytest.mark.asyncio
    async def test_different_durations(self, video_generator, sample_text):
        """Test video generation with different durations."""
        for duration in [30, 45, 60]:
            result = await video_generator.generate_video(
                f"test-job-{duration}",
                sample_text,
                duration=duration
            )
            
            assert result.duration == duration


class TestVideoGeneratorEdgeCases:
    """Test edge cases for VideoGenerator."""
    
    @pytest.mark.asyncio
    async def test_very_long_text(self, video_generator):
        """Test video generation with very long text."""
        long_text = "Modern POS display " * 50
        
        result = await video_generator.generate_video(
            "test-job-long",
            long_text
        )
        
        assert result.video_path
        assert Path(result.video_path).exists()
    
    @pytest.mark.asyncio
    async def test_special_characters_in_text(self, video_generator):
        """Test video generation with special characters."""
        special_text = "POS display: 50% OFF! @#$%^&*()"
        
        result = await video_generator.generate_video(
            "test-job-special",
            special_text
        )
        
        assert result.video_path
        assert Path(result.video_path).exists()
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, video_generator, sample_text):
        """Test concurrent video generation doesn't conflict."""
        tasks = [
            video_generator.generate_video(f"job-{i}", sample_text)
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert len(set(r.video_path for r in results)) == 3  # All unique