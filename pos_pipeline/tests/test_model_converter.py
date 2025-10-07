"""
Unit tests for 3D Model Conversion Service.
"""
import pytest
from pathlib import Path
from services.video_generator import VideoGenerator
from services.model_converter import ModelConverter
from utils.exceptions import ModelConversionError


class TestModelConverter:
    """Tests for ModelConverter class."""
    
    @pytest.mark.asyncio
    async def test_convert_to_3d_success(
        self,
        model_converter,
        video_generator,
        sample_text
    ):
        """Test successful 3D model conversion."""
        # First generate a video
        video_result = await video_generator.generate_video(
            "test-job-123",
            sample_text
        )
        
        # Convert to 3D model
        result = await model_converter.convert_to_3d(
            "test-job-123",
            video_result.video_path
        )
        
        assert result.job_id == "test-job-123"
        assert Path(result.model_path).exists()
        assert result.format == "stl"
        assert result.vertex_count > 0
        assert result.face_count > 0
        assert result.file_size_mb > 0
        assert result.processing_time > 0
        
        # Verify file exists and has content
        model_file = Path(result.model_path)
        assert model_file.stat().st_size > 0
    
    @pytest.mark.asyncio
    async def test_model_format(self, model_converter, video_generator, sample_text):
        """Test model is in correct format."""
        video_result = await video_generator.generate_video("test-job", sample_text)
        result = await model_converter.convert_to_3d("test-job", video_result.video_path)
        
        assert result.format == "stl"
        assert result.model_path.endswith(".stl")
    
    @pytest.mark.asyncio
    async def test_model_url_generation(
        self,
        model_converter,
        video_generator,
        sample_text
    ):
        """Test model URL is generated correctly."""
        video_result = await video_generator.generate_video("test-job-xyz", sample_text)
        result = await model_converter.convert_to_3d("test-job-xyz", video_result.video_path)
        
        assert result.model_url.startswith("/storage/models/")
        assert "test-job-xyz" in result.model_url
        assert result.model_url.endswith(".stl")
    
    @pytest.mark.asyncio
    async def test_nonexistent_video(self, model_converter):
        """Test conversion fails for non-existent video."""
        with pytest.raises(ModelConversionError) as exc_info:
            await model_converter.convert_to_3d(
                "test-job",
                "/nonexistent/video.mp4"
            )
        
        assert "not found" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_mesh_has_geometry(
        self,
        model_converter,
        video_generator,
        sample_text
    ):
        """Test generated mesh has valid geometry."""
        video_result = await video_generator.generate_video("test-job", sample_text)
        result = await model_converter.convert_to_3d("test-job", video_result.video_path)
        
        # Mesh should have minimum geometry
        assert result.vertex_count >= 4  # Minimum for 3D shape
        assert result.face_count >= 4  # Minimum for tetrahedron


class TestModelConverterEdgeCases:
    """Test edge cases for ModelConverter."""
    
    @pytest.mark.asyncio
    async def test_short_video(self, model_converter, video_generator, sample_text):
        """Test conversion of minimum duration video."""
        video_result = await video_generator.generate_video(
            "test-job",
            sample_text,
            duration=30
        )
        
        result = await model_converter.convert_to_3d("test-job", video_result.video_path)
        
        assert result.model_path
        assert Path(result.model_path).exists()
    
    @pytest.mark.asyncio
    async def test_longer_video(self, model_converter, video_generator, sample_text):
        """Test conversion of longer video."""
        video_result = await video_generator.generate_video(
            "test-job",
            sample_text,
            duration=45
        )
        
        result = await model_converter.convert_to_3d("test-job", video_result.video_path)
        
        assert result.model_path
        assert result.vertex_count > 0