"""Tests for video generator service."""

import pytest
from pathlib import Path
import cv2

from video_generator.service import VideoGeneratorService
from common.exceptions import VideoGenerationError


class TestVideoGeneratorService:
    """Tests for VideoGeneratorService."""
    
    @pytest.fixture
    def service(self, test_settings, temp_storage):
        """Create video generator service with test settings."""
        test_settings.video_storage_path = str(temp_storage / "videos")
        Path(test_settings.video_storage_path).mkdir(parents=True, exist_ok=True)
        
        with patch('video_generator.service.settings', test_settings):
            service = VideoGeneratorService()
            return service
    
    def test_initialization(self, service):
        """Test service initialization."""
        assert service.output_dir.exists()
    
    def test_generate_video_success(self, service):
        """Test successful video generation."""
        description = "A modern retail display"
        request_id = "test_req_001"
        
        metadata = service.generate_video(description, request_id)
        
        assert metadata.video_path
        assert Path(metadata.video_path).exists()
        assert metadata.duration == 30.0
        assert metadata.frame_rate == 30
        assert metadata.size_bytes > 0
    
    def test_generate_video_creates_valid_file(self, service):
        """Test that generated video is valid."""
        description = "Test display"
        request_id = "test_req_002"
        
        metadata = service.generate_video(description, request_id)
        
        # Verify video can be opened
        cap = cv2.VideoCapture(metadata.video_path)
        assert cap.isOpened()
        
        # Verify frame count
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        assert frame_count == 900  # 30 fps * 30 seconds
        
        cap.release()
    
    def test_generate_frame(self, service):
        """Test frame generation."""
        frame = service._generate_frame(
            frame_idx=0,
            total_frames=100,
            width=512,
            height=512,
            description="Test"
        )
        
        assert frame.shape == (512, 512, 3)
        assert frame.dtype == 'uint8'


from unittest.mock import patch