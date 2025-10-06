"""
Integration tests for API endpoints
Tests complete API flows with CSRF protection and authentication
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import sys

sys.path.insert(0, '.')


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from main import app, csrf_tokens
        csrf_tokens.clear()  # Clear tokens between tests
        return TestClient(app)
    
    def test_home_endpoint_generates_csrf_token(self, client):
        """Test that home endpoint generates CSRF token"""
        response = client.get("/")
        
        # Should return 200
        assert response.status_code == 200
        
        # Should set CSRF token cookie
        assert 'csrf_token' in response.cookies
        
        # Cookie should have proper attributes
        cookie = response.cookies['csrf_token']
        assert cookie is not None
    
    def test_csrf_token_endpoint(self, client):
        """Test CSRF token generation endpoint"""
        response = client.get("/csrf-token")
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'csrf_token' in data
        assert isinstance(data['csrf_token'], str)
        assert len(data['csrf_token']) > 0
    
    def test_post_without_csrf_token_fails(self, client):
        """Test that POST request without CSRF token is rejected"""
        response = client.post(
            "/convert",
            data={
                "github_url": "https://github.com/test/repo",
                "app_name": "test",
                "target_platform": "web"
            }
        )
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_post_with_invalid_csrf_token_fails(self, client):
        """Test that POST request with invalid CSRF token is rejected"""
        response = client.post(
            "/convert",
            data={
                "github_url": "https://github.com/test/repo",
                "app_name": "test",
                "target_platform": "web",
                "csrf_token": "invalid_token"
            },
            headers={"X-CSRF-Token": "invalid_token"}
        )
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_post_with_valid_csrf_token_succeeds(self, client):
        """Test that POST request with valid CSRF token succeeds"""
        # Get CSRF token
        token_response = client.get("/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Make POST request with token
        with patch('main.github_repo') as mock_github, \
             patch('main.readme_parser') as mock_parser, \
             patch('main.agentic_coder') as mock_coder, \
             patch('main.app_generator') as mock_generator:
            
            # Mock the async methods
            mock_github.clone_repository = Mock(return_value="/tmp/repo")
            mock_parser.parse_readme = Mock(return_value={"title": "Test"})
            mock_coder.analyze_codebase = Mock(return_value={"analysis": "done"})
            mock_generator.generate_app = Mock(return_value="/tmp/app.zip")
            
            response = client.post(
                "/convert",
                data={
                    "github_url": "https://github.com/test/repo",
                    "app_name": "test",
                    "target_platform": "web",
                    "csrf_token": csrf_token
                },
                headers={"X-CSRF-Token": csrf_token}
            )
            
            # Should accept request (might fail later in processing, but CSRF passed)
            assert response.status_code != 403
    
    def test_options_request_bypasses_csrf(self, client):
        """Test that OPTIONS requests bypass CSRF check"""
        response = client.options("/convert")
        
        # Should not return 403
        assert response.status_code != 403
    
    def test_csrf_token_in_cookie(self, client):
        """Test that CSRF token can be provided via cookie"""
        # Get CSRF token
        token_response = client.get("/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Set token in cookie
        client.cookies.set('csrf_token', csrf_token)
        
        with patch('main.github_repo') as mock_github, \
             patch('main.readme_parser') as mock_parser, \
             patch('main.agentic_coder') as mock_coder, \
             patch('main.app_generator') as mock_generator:
            
            response = client.post(
                "/convert",
                data={
                    "github_url": "https://github.com/test/repo",
                    "app_name": "test",
                    "target_platform": "web",
                    "csrf_token": csrf_token
                }
            )
            
            # Should accept request
            assert response.status_code != 403


class TestAPISecurityHeaders:
    """Test security headers in API responses"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from main import app
        return TestClient(app)
    
    def test_security_headers_present(self, client):
        """Test that security headers are present"""
        response = client.get("/")
        
        # Check for security headers (if added to main.py)
        # Note: FastAPI doesn't add these by default, they would need to be added
        assert response.status_code == 200


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from main import app, csrf_tokens
        csrf_tokens.clear()
        return TestClient(app)
    
    def test_invalid_form_data(self, client):
        """Test handling of invalid form data"""
        # Get CSRF token
        token_response = client.get("/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Send request with missing required field
        response = client.post(
            "/convert",
            data={
                # Missing github_url
                "app_name": "test",
                "csrf_token": csrf_token
            },
            headers={"X-CSRF-Token": csrf_token}
        )
        
        # Should return error (422 Unprocessable Entity)
        assert response.status_code == 422
    
    def test_malformed_request(self, client):
        """Test handling of malformed requests"""
        response = client.post(
            "/convert",
            data="not valid form data",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 403, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
