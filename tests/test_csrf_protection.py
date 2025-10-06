"""
Unit tests for CSRF Protection
Tests the CSRF middleware implementation in main.py
"""

import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from starlette.requests import Request
from starlette.responses import Response


class TestCSRFProtection:
    """Test CSRF protection middleware"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Import here to avoid import errors if dependencies not installed
        import sys
        sys.path.insert(0, '.')
        from main import CSRFMiddleware, generate_csrf_token, csrf_tokens
        
        self.CSRFMiddleware = CSRFMiddleware
        self.generate_csrf_token = generate_csrf_token
        self.csrf_tokens = csrf_tokens
        self.csrf_tokens.clear()
    
    def test_generate_csrf_token(self):
        """Test CSRF token generation"""
        token = self.generate_csrf_token()
        
        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should be stored with expiration
        assert token in self.csrf_tokens
        assert self.csrf_tokens[token] > time.time()
    
    def test_csrf_token_uniqueness(self):
        """Test that each token is unique"""
        token1 = self.generate_csrf_token()
        token2 = self.generate_csrf_token()
        
        assert token1 != token2
    
    def test_csrf_token_expiration(self):
        """Test token expiration"""
        token = self.generate_csrf_token()
        
        # Token should be valid initially
        assert token in self.csrf_tokens
        
        # Manually set expiration to past
        self.csrf_tokens[token] = time.time() - 100
        
        # Token should be considered expired
        middleware = self.CSRFMiddleware(Mock())
        assert not middleware._validate_csrf_token(token)
        
        # Expired token should be removed
        assert token not in self.csrf_tokens
    
    def test_csrf_token_cleanup(self):
        """Test that expired tokens are cleaned up"""
        # Generate multiple tokens
        tokens = [self.generate_csrf_token() for _ in range(5)]
        
        # Set some to expired
        for token in tokens[:3]:
            self.csrf_tokens[token] = time.time() - 100
        
        # Generate new token should clean up expired ones
        new_token = self.generate_csrf_token()
        
        # Check that at least some cleanup happened
        # (exact count may vary due to timing)
        assert len(self.csrf_tokens) < 6
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_allows_get_requests(self):
        """Test that GET requests bypass CSRF check"""
        middleware = self.CSRFMiddleware(Mock())
        
        # Create mock request
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        
        # Create mock call_next
        async def mock_call_next(req):
            return Response("OK", status_code=200)
        
        # Should allow GET request without CSRF token
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_blocks_post_without_token(self):
        """Test that POST requests without CSRF token are blocked"""
        middleware = self.CSRFMiddleware(Mock())
        
        # Create mock request
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/convert"
        request.headers = {}
        request.cookies = {}
        
        async def mock_call_next(req):
            return Response("OK", status_code=200)
        
        # Should block POST request without CSRF token
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_allows_post_with_valid_token(self):
        """Test that POST requests with valid CSRF token are allowed"""
        middleware = self.CSRFMiddleware(Mock())
        
        # Generate valid token
        token = self.generate_csrf_token()
        
        # Create mock request with token in header
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/convert"
        request.headers = {"X-CSRF-Token": token}
        request.cookies = {}
        
        async def mock_call_next(req):
            return Response("OK", status_code=200)
        
        # Should allow POST request with valid CSRF token
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_allows_token_in_cookie(self):
        """Test that CSRF token can be provided via cookie"""
        middleware = self.CSRFMiddleware(Mock())
        
        # Generate valid token
        token = self.generate_csrf_token()
        
        # Create mock request with token in cookie
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/convert"
        request.headers = {}
        request.cookies = {"csrf_token": token}
        
        async def mock_call_next(req):
            return Response("OK", status_code=200)
        
        # Should allow POST request with valid CSRF token in cookie
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_blocks_expired_token(self):
        """Test that expired CSRF tokens are rejected"""
        middleware = self.CSRFMiddleware(Mock())
        
        # Generate token and immediately expire it
        token = self.generate_csrf_token()
        self.csrf_tokens[token] = time.time() - 100
        
        # Create mock request
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/convert"
        request.headers = {"X-CSRF-Token": token}
        request.cookies = {}
        
        async def mock_call_next(req):
            return Response("OK", status_code=200)
        
        # Should block POST request with expired token
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_allows_safe_methods(self):
        """Test that safe HTTP methods bypass CSRF check"""
        middleware = self.CSRFMiddleware(Mock())
        
        safe_methods = ["GET", "HEAD", "OPTIONS"]
        
        for method in safe_methods:
            request = Mock(spec=Request)
            request.method = method
            request.url.path = "/test"
            
            async def mock_call_next(req):
                return Response("OK", status_code=200)
            
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200, f"{method} should be allowed"
    
    @pytest.mark.asyncio
    async def test_csrf_middleware_checks_unsafe_methods(self):
        """Test that unsafe HTTP methods require CSRF token"""
        middleware = self.CSRFMiddleware(Mock())
        
        unsafe_methods = ["POST", "PUT", "DELETE", "PATCH"]
        
        for method in unsafe_methods:
            request = Mock(spec=Request)
            request.method = method
            request.url.path = "/test"
            request.headers = {}
            request.cookies = {}
            
            async def mock_call_next(req):
                return Response("OK", status_code=200)
            
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 403, f"{method} should require CSRF token"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
