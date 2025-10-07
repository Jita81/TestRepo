"""Integration tests for the full pipeline."""

import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from api.app import create_app
from video_generator.service import VideoGeneratorService
from model_converter.service import ModelConverterService


@pytest.mark.integration
class TestPipelineIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.fixture
    def api_client(self):
        """Create API test client."""
        app = create_app()
        return TestClient(app)
    
    @patch('api.app.queue_client')
    def test_api_accepts_request(self, mock_queue, api_client):
        """Test that API accepts and queues requests."""
        mock_queue.connection = True
        mock_queue.publish = MagicMock()
        
        input_data = {
            "description": "A modern retail display for energy drinks",
            "metadata": {"customer": "test"}
        }
        
        response = api_client.post("/generate", json=input_data)
        
        assert response.status_code == 202
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "pending"
        
        # Verify queue publish was called
        mock_queue.publish.assert_called_once()
    
    def test_video_to_model_conversion(self, test_settings, temp_storage):
        """Test video generation followed by model conversion."""
        # Setup
        test_settings.video_storage_path = str(temp_storage / "videos")
        test_settings.model_storage_path = str(temp_storage / "models")
        
        with patch('video_generator.service.settings', test_settings):
            video_service = VideoGeneratorService()
            
            # Generate video
            video_metadata = video_service.generate_video(
                "Test display",
                "integration_test_001"
            )
            
            assert Path(video_metadata.video_path).exists()
        
        with patch('model_converter.service.settings', test_settings):
            model_service = ModelConverterService()
            
            # Convert to 3D model
            model_metadata = model_service.convert_video_to_3d(
                video_metadata.video_path,
                "integration_test_001"
            )
            
            assert Path(model_metadata.model_path).exists()
            assert model_metadata.format == "stl"
            assert model_metadata.vertex_count > 0
            assert model_metadata.face_count > 0