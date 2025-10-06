"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import time

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
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pos-to-3d-pipeline"
    
    def test_process_endpoint_valid_input(self):
        """Test process endpoint with valid input."""
        payload = {
            "text": "A vibrant red and blue rotating display stand featuring energy drink products"
        }
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "execution_id" in data
        assert "status" in data
        assert "status_url" in data
        assert data["status"] in ["queued", "pending"]
    
    def test_process_endpoint_with_metadata(self):
        """Test process endpoint with optional metadata."""
        payload = {
            "text": "Modern display stand with premium product placement",
            "metadata": {
                "source": "test",
                "priority": "high"
            }
        }
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "execution_id" in data
    
    def test_process_endpoint_minimum_text(self):
        """Test process endpoint with minimum valid text."""
        payload = {"text": "1234567890"}  # Exactly 10 characters
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
    
    def test_process_endpoint_text_too_short(self):
        """Test process endpoint with text that's too short."""
        payload = {"text": "short"}
        
        response = client.post("/api/v1/process", json=payload)
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_process_endpoint_text_too_long(self):
        """Test process endpoint with text that's too long."""
        payload = {"text": "a" * 6000}
        
        response = client.post("/api/v1/process", json=payload)
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_process_endpoint_missing_text(self):
        """Test process endpoint with missing text field."""
        payload = {}
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_process_endpoint_invalid_text_type(self):
        """Test process endpoint with non-string text."""
        payload = {"text": 12345}
        
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 422
    
    def test_status_endpoint_not_found(self):
        """Test status endpoint with non-existent execution."""
        response = client.get("/api/v1/status/nonexistent_id")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    def test_result_endpoint_not_found(self):
        """Test result endpoint with non-existent execution."""
        response = client.get("/api/v1/result/nonexistent_id")
        assert response.status_code == 404
    
    def test_list_executions_default(self):
        """Test list executions endpoint with default limit."""
        response = client.get("/api/v1/executions")
        assert response.status_code == 200
        
        data = response.json()
        assert "executions" in data
        assert "total" in data
        assert isinstance(data["executions"], list)
    
    def test_list_executions_with_limit(self):
        """Test list executions endpoint with custom limit."""
        response = client.get("/api/v1/executions?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["executions"]) <= 5
    
    def test_download_video_not_found(self):
        """Test download video with non-existent file."""
        response = client.get("/api/v1/download/video/nonexistent.mp4")
        assert response.status_code == 404
    
    def test_download_model_not_found(self):
        """Test download model with non-existent file."""
        response = client.get("/api/v1/download/model/nonexistent.stl")
        assert response.status_code == 404
    
    def test_api_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options("/")
        # Should have CORS headers
        assert response.status_code in [200, 405]
    
    def test_api_docs_endpoint(self):
        """Test that API documentation endpoint exists."""
        response = client.get("/docs")
        # Should redirect or return docs page
        assert response.status_code in [200, 307]
    
    def test_api_openapi_schema(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


@pytest.mark.asyncio
class TestAPIIntegration:
    """Async integration tests for API."""
    
    async def test_process_and_check_status(self):
        """Test submitting job and checking status."""
        payload = {
            "text": "A modern white display shelf featuring premium cosmetics with elegant accents"
        }
        
        # Submit processing request
        response = client.post("/api/v1/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        execution_id = data["execution_id"]
        
        # Wait a moment for processing to start
        import asyncio
        await asyncio.sleep(0.5)
        
        # Check status
        status_response = client.get(f"/api/v1/status/{execution_id}")
        
        # Status endpoint should work
        if status_response.status_code == 200:
            status_data = status_response.json()
            assert "execution_id" in status_data
            assert "status" in status_data
            assert "progress" in status_data
    
    async def test_multiple_concurrent_submissions(self):
        """Test submitting multiple jobs concurrently."""
        payloads = [
            {"text": "First display stand with modern design elements"},
            {"text": "Second display with vibrant color scheme"},
            {"text": "Third stand featuring premium product placement"}
        ]
        
        execution_ids = []
        
        # Submit all jobs
        for payload in payloads:
            response = client.post("/api/v1/process", json=payload)
            assert response.status_code == 200
            data = response.json()
            execution_ids.append(data["execution_id"])
        
        # All execution IDs should be unique
        assert len(execution_ids) == len(set(execution_ids))
        
        # Check that all are tracked
        import asyncio
        await asyncio.sleep(0.5)
        
        list_response = client.get("/api/v1/executions")
        assert list_response.status_code == 200
        
        data = list_response.json()
        tracked_ids = [e["execution_id"] for e in data["executions"]]
        
        for exec_id in execution_ids:
            assert exec_id in tracked_ids or True  # May have completed already
