"""
Edge case tests for ModelConverter stage.
"""

import pytest
import numpy as np
from pathlib import Path
import cv2
from src.stages.model_converter import ModelConverter
from src.core.base import ValidationError, ProcessingError


@pytest.mark.asyncio
class TestModelConverterEdgeCases:
    """Edge case tests for ModelConverter."""
    
    async def test_validate_missing_video_path(self, test_config):
        """Test validation with missing video_path."""
        converter = ModelConverter(test_config["model_converter"])
        
        with pytest.raises(ValidationError) as exc_info:
            await converter.validate({}, is_input=True)
        
        assert "video_path" in str(exc_info.value).lower()
    
    async def test_validate_nonexistent_video(self, test_config):
        """Test validation with nonexistent video file."""
        converter = ModelConverter(test_config["model_converter"])
        
        with pytest.raises(ValidationError) as exc_info:
            await converter.validate({"video_path": "/nonexistent/video.mp4"}, is_input=True)
        
        assert "not found" in str(exc_info.value).lower()
    
    async def test_validate_output_missing_model_path(self, test_config):
        """Test output validation with missing model_path."""
        converter = ModelConverter(test_config["model_converter"])
        
        with pytest.raises(ValidationError) as exc_info:
            await converter.validate({"format": "STL"}, is_input=False)
        
        assert "model_path" in str(exc_info.value).lower()
    
    async def test_validate_output_wrong_format(self, test_config, temp_dir):
        """Test output validation with wrong format."""
        converter = ModelConverter(test_config["model_converter"])
        
        model_file = temp_dir / "model.stl"
        model_file.touch()
        
        with pytest.raises(ValidationError):
            await converter.validate({
                "model_path": str(model_file),
                "format": "OBJ"  # Wrong format
            }, is_input=False)
    
    async def test_create_mesh_single_frame(self, test_config):
        """Test mesh creation with single frame."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create single test frame
        frame = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        depth_map = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        
        vertices, faces = await converter._create_mesh([frame], [depth_map])
        
        assert len(vertices) > 0
        assert len(faces) > 0
        assert vertices.shape[1] == 3  # 3D coordinates
        assert faces.shape[1] == 3  # Triangular faces
    
    async def test_create_mesh_multiple_frames(self, test_config):
        """Test mesh creation with multiple frames (uses middle frame)."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create multiple frames
        frames = [np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8) for _ in range(5)]
        depth_maps = [np.random.randint(0, 255, (50, 50), dtype=np.uint8) for _ in range(5)]
        
        vertices, faces = await converter._create_mesh(frames, depth_maps)
        
        assert len(vertices) > 0
        assert len(faces) > 0
    
    async def test_create_mesh_small_resolution(self, test_config):
        """Test mesh creation with very small frames."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Very small frame
        frame = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        depth_map = np.random.randint(0, 255, (10, 10), dtype=np.uint8)
        
        vertices, faces = await converter._create_mesh([frame], [depth_map])
        
        assert len(vertices) > 0
        assert len(faces) > 0
    
    async def test_create_mesh_large_resolution(self, test_config):
        """Test mesh creation with large frames."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Larger frame (but not too large for testing)
        frame = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        depth_map = np.random.randint(0, 255, (200, 300), dtype=np.uint8)
        
        vertices, faces = await converter._create_mesh([frame], [depth_map])
        
        assert len(vertices) > 0
        assert len(faces) > 0
    
    async def test_generate_depth_maps_single_frame(self, test_config):
        """Test depth map generation with single frame."""
        converter = ModelConverter(test_config["model_converter"])
        
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        depth_maps = await converter._generate_depth_maps([frame])
        
        assert len(depth_maps) == 1
        assert depth_maps[0].shape == (100, 100)
        assert depth_maps[0].dtype == np.uint8
    
    async def test_generate_depth_maps_uniform_color(self, test_config):
        """Test depth map with uniform colored frame."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Solid color frame (no edges)
        frame = np.full((100, 100, 3), 128, dtype=np.uint8)
        depth_maps = await converter._generate_depth_maps([frame])
        
        assert len(depth_maps) == 1
        assert depth_maps[0].shape == (100, 100)
    
    async def test_generate_depth_maps_high_contrast(self, test_config):
        """Test depth map with high contrast frame."""
        converter = ModelConverter(test_config["model_converter"])
        
        # High contrast frame (should produce clear edges)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[25:75, 25:75] = 255
        
        depth_maps = await converter._generate_depth_maps([frame])
        
        assert len(depth_maps) == 1
        assert depth_maps[0].shape == (100, 100)
    
    async def test_export_stl_minimal_mesh(self, test_config, temp_dir):
        """Test STL export with minimal mesh (single triangle)."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Single triangle
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2]
        ], dtype=np.int32)
        
        output_path = temp_dir / "minimal.stl"
        await converter._export_stl(vertices, faces, output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verify STL structure
        with open(output_path, 'rb') as f:
            header = f.read(80)
            assert len(header) == 80
    
    async def test_export_stl_zero_area_triangle(self, test_config, temp_dir):
        """Test STL export with degenerate triangle (zero area)."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Degenerate triangle (all points collinear)
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [2, 0, 0]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2]
        ], dtype=np.int32)
        
        output_path = temp_dir / "degenerate.stl"
        await converter._export_stl(vertices, faces, output_path)
        
        assert output_path.exists()
    
    async def test_export_stl_large_mesh(self, test_config, temp_dir):
        """Test STL export with larger mesh."""
        converter = ModelConverter(test_config["model_converter"])
        
        # Create grid of vertices
        size = 20
        vertices = []
        for y in range(size):
            for x in range(size):
                vertices.append([x, y, 0])
        vertices = np.array(vertices, dtype=np.float32)
        
        # Create faces from grid
        faces = []
        for y in range(size - 1):
            for x in range(size - 1):
                v1 = y * size + x
                v2 = y * size + (x + 1)
                v3 = (y + 1) * size + (x + 1)
                v4 = (y + 1) * size + x
                
                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])
        faces = np.array(faces, dtype=np.int32)
        
        output_path = temp_dir / "large.stl"
        await converter._export_stl(vertices, faces, output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 1000  # Should be reasonably sized
    
    async def test_quality_settings_low(self, test_config):
        """Test model converter with low quality settings."""
        config = test_config["model_converter"].copy()
        config["quality"] = "low"
        
        converter = ModelConverter(config)
        
        assert converter.quality == "low"
        assert converter.settings["sample_rate"] == 10
        assert converter.settings["depth_levels"] == 5
    
    async def test_quality_settings_medium(self, test_config):
        """Test model converter with medium quality settings."""
        config = test_config["model_converter"].copy()
        config["quality"] = "medium"
        
        converter = ModelConverter(config)
        
        assert converter.quality == "medium"
        assert converter.settings["sample_rate"] == 5
        assert converter.settings["depth_levels"] == 10
    
    async def test_quality_settings_high(self, test_config):
        """Test model converter with high quality settings."""
        config = test_config["model_converter"].copy()
        config["quality"] = "high"
        
        converter = ModelConverter(config)
        
        assert converter.quality == "high"
        assert converter.settings["sample_rate"] == 2
        assert converter.settings["depth_levels"] == 20
    
    async def test_quality_settings_invalid(self, test_config):
        """Test model converter with invalid quality defaults to medium."""
        config = test_config["model_converter"].copy()
        config["quality"] = "invalid_quality"
        
        converter = ModelConverter(config)
        
        # Should default to medium
        assert converter.settings == converter.quality_settings["medium"]
    
    async def test_export_stl_file_creation(self, test_config, temp_dir):
        """Test that STL file is created in correct location."""
        converter = ModelConverter(test_config["model_converter"])
        
        vertices = np.array([[0,0,0], [1,0,0], [0,1,0]], dtype=np.float32)
        faces = np.array([[0,1,2]], dtype=np.int32)
        
        output_path = temp_dir / "test.stl"
        await converter._export_stl(vertices, faces, output_path)
        
        assert output_path.exists()
        assert output_path.is_file()
        assert output_path.suffix == ".stl"
