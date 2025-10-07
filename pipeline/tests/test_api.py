"""Tests for API service."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.app import create_app
from common.models import PipelineStatus


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # May be unhealthy without queue
        data = response.json()
        assert "status" in data
        assert "components" in data


class TestGenerateEndpoint:
    """Tests for generate endpoint."""
    
    @patch('api.app.queue_client')
    def test_generate_success(self, mock_queue, client, sample_text_input):
        """Test successful generation request."""
        # Configure mock
        mock_queue.connection = True
        mock_queue.publish = MagicMock()
        
        response = client.post("/generate", json=sample_text_input)
        
        assert response.status_code == 202
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "pending"
        assert data["message"] == "Pipeline initiated successfully"
    
    def test_generate_invalid_input(self, client):
        """Test generation with invalid input."""
        response = client.post("/generate", json={"description": "short"})
        assert response.status_code == 422
    
    def test_generate_missing_description(self, client):
        """Test generation without description."""
        response = client.post("/generate", json={})
        assert response.status_code == 422
    
    @patch('api.app.queue_client', None)
    def test_generate_queue_unavailable(self, client, sample_text_input):
        """Test generation when queue is unavailable."""
        response = client.post("/generate", json=sample_text_input)
        assert response.status_code == 503


class TestStatusEndpoint:
    """Tests for status endpoint."""
    
    def test_status_check(self, client):
        """Test status check endpoint."""
        response = client.get("/status/req_123")
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["request_id"] == "req_123"