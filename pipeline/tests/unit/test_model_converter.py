"""
Unit tests for ModelConverter stage.
"""

import pytest
import numpy as np
from pathlib import Path
from src.stages.model_converter import ModelConverter
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestModelConverter:
    """Test cases for ModelConverter."""
    
    async def test_model_converter_initialization(self, test_config):
        """Test ModelConverter initialization."""
        converter = ModelConverter(test_config["model_converter"])
        assert converter.stage_name == "ModelConverter"
        assert converter.output_format == "STL"
        assert converter.quality == "medium"
    
    async def test_validate_valid_input(self, test_config, sample_video_output):
        """Test validation with valid input."""
        converter = ModelConverter(test_config["model_converter"])
        result = await converter.validate(sample_video_output, is_input=True)
        assert result is True
    
    async def test_validate_missing_video_path(self, test_config):
        """Test validation with missing video_path field."""
        converter = ModelConverter(test_config["model_converter"])
        
        with pytest.raises(ValidationError) as exc_info:
            await converter.validate({}, is_input=True)
        
        assert "Missing required field: 'video_path'" in str(exc_info.value)
    
    async def test_create_mesh(self, test_config):
        """Test mesh creation from frames."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create simple test frames and depth maps
        frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(3)]
        depth_maps = [np.random.randint(0, 255, (100, 100), dtype=np.uint8) for _ in range(3)]
        
        vertices, faces = await converter._create_mesh(frames, depth_maps)
        
        assert len(vertices) > 0
        assert len(faces) > 0
        assert vertices.shape[1] == 3  # 3D coordinates
        assert faces.shape[1] == 3  # Triangular faces
    
    async def test_generate_depth_maps(self, test_config):
        """Test depth map generation."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create simple test frames
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(3)]
        
        depth_maps = await converter._generate_depth_maps(frames)
        
        assert len(depth_maps) == len(frames)
        for depth_map in depth_maps:
            assert depth_map.shape == (100, 100)
            assert depth_map.dtype == np.uint8


@pytest.mark.asyncio
class TestModelConverterSTL:
    """Test STL export functionality."""
    
    async def test_export_stl(self, test_config, temp_dir):
        """Test STL file export."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create simple mesh
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ], dtype=np.int32)
        
        output_path = temp_dir / "test_model.stl"
        
        await converter._export_stl(vertices, faces, output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verify STL header
        with open(output_path, 'rb') as f:
            header = f.read(80)
            assert len(header) == 80
