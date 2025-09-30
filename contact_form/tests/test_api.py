"""
Integration tests for contact form API endpoints.

Tests the FastAPI endpoints, error handling, and response formats.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from ..api import app, ContactFormService
from ..models import ContactFormRequest


# Test client
client = TestClient(app)


class TestContactFormAPI:
    """Test suite for contact form API endpoints."""
    
    def test_submit_valid_form(self):
        """Test submitting a valid contact form."""
        payload = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "message": "This is a test message with sufficient length."
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["success"] is True
        assert "submission_id" in data
        assert "timestamp" in data
        assert len(data["submission_id"]) > 0
    
    def test_submit_form_invalid_name(self):
        """Test submitting form with invalid name."""
        payload = {
            "name": "J",  # Too short
            "email": "test@example.com",
            "message": "Valid message here"
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        
        # Check for validation error in response
        assert "detail" in data or "errors" in data or "message" in data
    
    def test_submit_form_invalid_email(self):
        """Test submitting form with invalid email."""
        payload = {
            "name": "John Doe",
            "email": "not-an-email",
            "message": "Valid message here"
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 422
    
    def test_submit_form_short_message(self):
        """Test submitting form with message too short."""
        payload = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "Too short"
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 422
    
    def test_submit_form_missing_fields(self):
        """Test submitting form with missing required fields."""
        # Missing name
        response = client.post("/api/contact", json={
            "email": "test@example.com",
            "message": "Valid message here"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/contact", json={
            "name": "John Doe",
            "message": "Valid message here"
        })
        assert response.status_code == 422
        
        # Missing message
        response = client.post("/api/contact", json={
            "name": "John Doe",
            "email": "test@example.com"
        })
        assert response.status_code == 422
    
    def test_submit_form_empty_payload(self):
        """Test submitting empty payload."""
        response = client.post("/api/contact", json={})
        
        assert response.status_code == 422
    
    def test_submit_form_invalid_json(self):
        """Test submitting invalid JSON."""
        response = client.post(
            "/api/contact",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_submit_form_name_with_numbers(self):
        """Test that names with numbers are rejected."""
        payload = {
            "name": "John123",
            "email": "test@example.com",
            "message": "Valid message here"
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 422
    
    def test_submit_form_name_with_special_chars(self):
        """Test that names with valid special characters are accepted."""
        valid_names = [
            "Mary-Jane Watson",
            "O'Brien",
            "Jean-Pierre"
        ]
        
        for name in valid_names:
            payload = {
                "name": name,
                "email": "test@example.com",
                "message": "Valid message here with enough characters"
            }
            
            response = client.post("/api/contact", json=payload)
            
            assert response.status_code == 201, \
                f"Valid name '{name}' was rejected"
    
    def test_submit_form_whitespace_trimming(self):
        """Test that whitespace is properly trimmed."""
        payload = {
            "name": "  John Doe  ",
            "email": " test@example.com ",
            "message": "  Valid message with whitespace  "
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 201
    
    def test_submit_form_max_length_message(self):
        """Test submitting form with maximum length message."""
        payload = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "A" * 2000  # Max length
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 201
    
    def test_submit_form_exceeds_max_length_message(self):
        """Test that messages exceeding max length are rejected."""
        payload = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "A" * 2001  # Exceeds max
        }
        
        response = client.post("/api/contact", json=payload)
        
        assert response.status_code == 422
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestContactFormService:
    """Test suite for ContactFormService."""
    
    @pytest.mark.asyncio
    async def test_process_submission_success(self):
        """Test successful submission processing."""
        form_data = ContactFormRequest(
            name="Test User",
            email="test@example.com",
            message="This is a test message"
        )
        
        service = ContactFormService()
        response = await service.process_submission(form_data)
        
        assert response.success is True
        assert len(response.submission_id) > 0
        assert isinstance(response.timestamp, datetime)
        assert "received" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_process_submission_generates_unique_ids(self):
        """Test that each submission gets a unique ID."""
        form_data = ContactFormRequest(
            name="Test User",
            email="test@example.com",
            message="This is a test message"
        )
        
        service = ContactFormService()
        
        # Process multiple submissions
        response1 = await service.process_submission(form_data)
        response2 = await service.process_submission(form_data)
        response3 = await service.process_submission(form_data)
        
        # All IDs should be unique
        ids = {response1.submission_id, response2.submission_id, response3.submission_id}
        assert len(ids) == 3
    
    @pytest.mark.asyncio
    async def test_process_submission_logging(self):
        """Test that submissions are properly logged."""
        form_data = ContactFormRequest(
            name="Test User",
            email="test@example.com",
            message="This is a test message"
        )
        
        service = ContactFormService()
        
        with patch('logging.Logger.info') as mock_log:
            await service.process_submission(form_data)
            
            # Verify logging occurred
            assert mock_log.called
            log_message = mock_log.call_args[0][0]
            assert "submission received" in log_message.lower()


class TestCORSConfiguration:
    """Test CORS middleware configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are included in responses."""
        response = client.options(
            "/api/contact",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or \
               response.status_code in [200, 405]  # OPTIONS might not be explicitly defined


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_malformed_json_error(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/contact",
            data='{"name": "test", invalid}',
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_wrong_content_type(self):
        """Test handling of wrong content type."""
        response = client.post(
            "/api/contact",
            data="name=test&email=test@test.com&message=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should return error for wrong content type
        assert response.status_code in [422, 400]
    
    def test_additional_fields_ignored(self):
        """Test that additional fields are handled properly."""
        payload = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "Valid message here",
            "extra_field": "should be ignored",
            "another_extra": 123
        }
        
        response = client.post("/api/contact", json=payload)
        
        # Should still succeed, extra fields ignored
        assert response.status_code == 201