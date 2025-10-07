"""Tests for model converter service."""

import pytest
from pathlib import Path
import numpy as np

from model_converter.service import ModelConverterService
from common.exceptions import ModelConversionError


class TestModelConverterService:
    """Tests for ModelConverterService."""
    
    @pytest.fixture
    def service(self, test_settings, temp_storage):
        """Create model converter service with test settings."""
        test_settings.model_storage_path = str(temp_storage / "models")
        test_settings.temp_storage_path = str(temp_storage / "temp")
        Path(test_settings.model_storage_path).mkdir(parents=True, exist_ok=True)
        Path(test_settings.temp_storage_path).mkdir(parents=True, exist_ok=True)
        
        from unittest.mock import patch
        with patch('model_converter.service.settings', test_settings):
            service = ModelConverterService()
            return service
    
    def test_initialization(self, service):
        """Test service initialization."""
        assert service.output_dir.exists()
        assert service.temp_dir.exists()
    
    def test_generate_point_cloud(self, service):
        """Test point cloud generation."""
        # Create dummy frames
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(5)]
        
        point_cloud = service._generate_point_cloud(frames, "test_req")
        
        assert len(point_cloud) > 0
        assert point_cloud.shape[1] == 3  # X, Y, Z coordinates
    
    def test_create_simple_mesh(self, service):
        """Test simple mesh creation."""
        # Create simple point cloud
        point_cloud = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
        ], dtype=np.float32)
        
        stl_path = service._create_simple_mesh(point_cloud, "test_req_mesh")
        
        assert Path(stl_path).exists()
        assert stl_path.endswith(".stl")
        
        # Verify file size
        assert Path(stl_path).stat().st_size > 0