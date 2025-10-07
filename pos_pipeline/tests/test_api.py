"""
API endpoint tests for the POS Pipeline.
"""
import pytest
from httpx import AsyncClient
from services.api_gateway.main import app
from config.settings import settings


@pytest.fixture
def api_headers():
    """API headers with authentication."""
    return {"X-API-Key": settings.api_key}


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint returns service info."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_process_pipeline_success(self, api_headers):
        """Test successful pipeline submission."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={
                    "text": "Modern red and white POS display for electronics",
                    "metadata": {"category": "electronics"}
                },
                headers=api_headers
            )
        
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert "status_url" in data
        assert "result_url" in data
    
    @pytest.mark.asyncio
    async def test_process_pipeline_no_api_key(self):
        """Test pipeline submission fails without API key."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={"text": "Test POS display stand"}
            )
        
        assert response.status_code == 422  # Missing header
    
    @pytest.mark.asyncio
    async def test_process_pipeline_invalid_api_key(self):
        """Test pipeline submission fails with invalid API key."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={"text": "Test POS display stand"},
                headers={"X-API-Key": "invalid-key"}
            )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_process_pipeline_invalid_text(self, api_headers):
        """Test pipeline submission fails with invalid text."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={"text": "ab"},  # Too short
                headers=api_headers
            )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_status_nonexistent_job(self, api_headers):
        """Test getting status for non-existent job."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/pipeline/status/nonexistent-job-id",
                headers=api_headers
            )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_result_nonexistent_job(self, api_headers):
        """Test getting result for non-existent job."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/pipeline/result/nonexistent-job-id",
                headers=api_headers
            )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_api_validation_empty_text(self, api_headers):
        """Test API validates empty text."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={"text": ""},
                headers=api_headers
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_api_validation_text_too_long(self, api_headers):
        """Test API validates text length."""
        long_text = "word " * 500
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/pipeline/process",
                json={"text": long_text},
                headers=api_headers
            )
        
        assert response.status_code == 422


class TestAPIWorkflow:
    """Test complete API workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, api_headers):
        """Test complete API workflow from submission to result."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Submit job
            submit_response = await client.post(
                "/pipeline/process",
                json={
                    "text": "Modern blue and white POS display for retail products",
                    "metadata": {"category": "retail"}
                },
                headers=api_headers
            )
            
            assert submit_response.status_code == 202
            job_id = submit_response.json()["job_id"]
            
            # Check status
            import asyncio
            await asyncio.sleep(1)
            
            status_response = await client.get(
                f"/pipeline/status/{job_id}",
                headers=api_headers
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["job_id"] == job_id
            assert "stage" in status_data
            assert "progress" in status_data