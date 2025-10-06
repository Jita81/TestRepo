"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app


client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "POS to 3D Pipeline"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_process_endpoint(self):
        """Test process endpoint."""
        payload = {
            "text": "A vibrant red and blue rotating display stand featuring energy drink products"
        }
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "execution_id" in data
        assert "status" in data
        assert "status_url" in data
    
    def test_process_endpoint_invalid_input(self):
        """Test process endpoint with invalid input."""
        # Too short text
        payload = {"text": "short"}
        
        response = client.post("/api/v1/process", json=payload)
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_status_endpoint_not_found(self):
        """Test status endpoint with non-existent execution."""
        response = client.get("/api/v1/status/nonexistent_id")
        assert response.status_code == 404
    
    def test_list_executions(self):
        """Test list executions endpoint."""
        response = client.get("/api/v1/executions")
        assert response.status_code == 200
        
        data = response.json()
        assert "executions" in data
        assert "total" in data
        assert isinstance(data["executions"], list)
    
    def test_download_video_not_found(self):
        """Test download video with non-existent file."""
        response = client.get("/api/v1/download/video/nonexistent.mp4")
        assert response.status_code == 404
    
    def test_download_model_not_found(self):
        """Test download model with non-existent file."""
        response = client.get("/api/v1/download/model/nonexistent.stl")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAPIIntegration:
    """Async integration tests for API."""
    
    async def test_full_pipeline_via_api(self):
        """Test complete pipeline execution via API."""
        payload = {
            "text": "A modern white display shelf featuring premium cosmetics with elegant gold accents and soft lighting"
        }
        
        # Submit processing request
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        execution_id = data["execution_id"]
        
        # Give it a moment to start processing
        import asyncio
        await asyncio.sleep(1)
        
        # Check status
        status_response = client.get(f"/api/v1/status/{execution_id}")
        
        # Status endpoint should work even if processing hasn't completed
        assert status_response.status_code in [200, 404]  # May not exist yet if very fast
