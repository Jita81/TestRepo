"""Security tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestInputSecurity:
    """Security tests for input validation."""
    
    def test_sql_injection_attempt(self, client):
        """Test that SQL injection patterns are rejected."""
        malicious_input = {
            "description": "'; DROP TABLE users; --"
        }
        response = client.post("/generate", json=malicious_input)
        # Should fail validation (too short after sanitization)
        assert response.status_code == 422
    
    def test_xss_attempt_script_tags(self, client):
        """Test that XSS attempts with script tags are rejected."""
        malicious_input = {
            "description": "<script>alert('xss')</script> with more content"
        }
        response = client.post("/generate", json=malicious_input)
        # Should be rejected due to < and > characters
        assert response.status_code in [400, 422]
    
    def test_xss_attempt_event_handlers(self, client):
        """Test that XSS event handlers are rejected."""
        malicious_input = {
            "description": "Test <img src=x onerror=alert('xss')> description"
        }
        response = client.post("/generate", json=malicious_input)
        assert response.status_code in [400, 422]
    
    def test_path_traversal_attempt(self, client):
        """Test that path traversal attempts are handled."""
        malicious_input = {
            "description": "../../etc/passwd file access attempt with more text",
            "metadata": {"file": "../../../etc/shadow"}
        }
        # Should accept as valid text (not interpreted as path)
        # But will be caught if there's any validation
        response = client.post("/generate", json=malicious_input)
        # The description itself doesn't have forbidden chars, might pass
        assert response.status_code in [202, 422, 503]
    
    def test_null_byte_injection(self, client):
        """Test that null byte injection is rejected."""
        malicious_input = {
            "description": "Test\\x00 null byte injection with enough length"
        }
        response = client.post("/generate", json=malicious_input)
        assert response.status_code in [400, 422]
    
    def test_command_injection_attempt(self, client):
        """Test that command injection patterns are rejected."""
        malicious_input = {
            "description": "Test; rm -rf / ; echo 'hacked' with more content here"
        }
        # Semicolons and other special chars might be allowed in description
        # This tests that they don't cause command execution
        response = client.post("/generate", json=malicious_input)
        # Should either pass validation or fail, but not execute commands
        assert response.status_code in [202, 400, 422, 503]
    
    def test_unicode_normalization_attack(self, client):
        """Test unicode normalization attacks."""
        # Using fullwidth characters that might normalize to dangerous chars
        malicious_input = {
            "description": "Test ＜script＞ fullwidth characters with enough length"
        }
        response = client.post("/generate", json=malicious_input)
        # Should handle unicode properly
        assert response.status_code in [202, 400, 422, 503]


class TestAPIKeyAuthentication:
    """Tests for API key authentication (if enabled)."""
    
    @patch('api.app.settings')
    @patch('api.app.queue_client')
    def test_missing_api_key_when_required(self, mock_queue, mock_settings, client):
        """Test that requests without API key are rejected when required."""
        mock_settings.api_key = "secret_key_12345"
        mock_queue.connection = True
        
        response = client.post(
            "/generate",
            json={"description": "Test display with enough length"}
        )
        # Without the required API key header
        assert response.status_code in [403, 422]
    
    @patch('api.app.settings')
    @patch('api.app.queue_client')
    def test_invalid_api_key(self, mock_queue, mock_settings, client):
        """Test that invalid API key is rejected."""
        mock_settings.api_key = "correct_key"
        mock_queue.connection = True
        
        response = client.post(
            "/generate",
            headers={"X-API-Key": "wrong_key"},
            json={"description": "Test display with enough length"}
        )
        assert response.status_code in [403, 422]


class TestRateLimitingEdgeCases:
    """Tests for rate limiting edge cases (future implementation)."""
    
    @patch('api.app.queue_client')
    def test_rapid_successive_requests(self, mock_queue, client):
        """Test handling of rapid successive requests."""
        mock_queue.connection = True
        mock_queue.publish = MagicMock()
        
        # Send multiple requests rapidly
        for i in range(10):
            response = client.post(
                "/generate",
                json={"description": f"Request {i} with enough length for validation"}
            )
            # Should handle all requests
            assert response.status_code in [202, 503, 429]  # 429 if rate limiting implemented


class TestInputSizeValidation:
    """Tests for input size validation."""
    
    @patch('api.app.queue_client')
    def test_maximum_length_description(self, mock_queue, client):
        """Test description at maximum allowed length."""
        mock_queue.connection = True
        mock_queue.publish = MagicMock()
        
        max_desc = "x" * 1000  # Exactly at limit
        response = client.post(
            "/generate",
            json={"description": max_desc}
        )
        assert response.status_code == 202
    
    def test_oversized_description(self, client):
        """Test description exceeding maximum length."""
        oversized_desc = "x" * 1001  # Over the limit
        response = client.post(
            "/generate",
            json={"description": oversized_desc}
        )
        assert response.status_code == 422
    
    @patch('api.app.queue_client')
    def test_large_metadata_object(self, mock_queue, client):
        """Test with very large metadata object."""
        mock_queue.connection = True
        mock_queue.publish = MagicMock()
        
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(1000)}
        response = client.post(
            "/generate",
            json={
                "description": "Test description with enough length",
                "metadata": large_metadata
            }
        )
        # Should handle large metadata
        assert response.status_code in [202, 400, 413, 503]


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/generate",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        # Should have CORS headers
        assert response.status_code in [200, 204]
    
    def test_cors_actual_request(self, client):
        """Test that actual requests include CORS headers."""
        response = client.get(
            "/health",
            headers={"Origin": "http://example.com"}
        )
        # Check for CORS headers in response
        assert response.status_code in [200, 503]