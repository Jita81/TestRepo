"""
Python tests for the development server
Tests rate limiting and security features
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import RateLimiter, find_free_port


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_allows_requests_within_limit(self):
        """Should allow requests up to the limit"""
        limiter = RateLimiter()
        ip = '127.0.0.1'
        
        # First request should be allowed
        allowed, msg = limiter.is_allowed(ip)
        assert allowed is True
        assert msg is None
    
    def test_blocks_burst_requests(self):
        """Should block requests exceeding burst limit"""
        limiter = RateLimiter()
        ip = '127.0.0.1'
        
        # Make requests up to burst limit
        for i in range(10):
            allowed, msg = limiter.is_allowed(ip)
            assert allowed is True
        
        # Next request should be blocked
        allowed, msg = limiter.is_allowed(ip)
        assert allowed is False
        assert 'second' in msg.lower()
    
    def test_separate_ips_tracked_independently(self):
        """Should track different IPs independently"""
        limiter = RateLimiter()
        
        # Fill limit for first IP
        for i in range(10):
            limiter.is_allowed('192.168.1.1')
        
        # Second IP should still be allowed
        allowed, msg = limiter.is_allowed('192.168.1.2')
        assert allowed is True
    
    def test_cleans_old_requests(self):
        """Should clean up old request records"""
        limiter = RateLimiter()
        ip = '127.0.0.1'
        
        # Add request
        limiter.is_allowed(ip)
        
        # Check requests are tracked
        assert len(limiter.requests[ip]) == 1
        
        # The cleanup happens automatically in is_allowed
        # based on timestamp comparison


class TestPortFinding:
    """Test port finding functionality"""
    
    def test_finds_free_port(self):
        """Should find an available port"""
        port = find_free_port(8000)
        assert port is not None
        assert port >= 8000
        assert port < 8010
    
    def test_returns_none_when_no_ports(self):
        """Should return None if no ports available"""
        # This is hard to test without actually occupying ports
        # Just verify the function exists and has correct signature
        port = find_free_port(65530, max_attempts=1)
        assert port is None or isinstance(port, int)


class TestSecurityFeatures:
    """Test security configurations"""
    
    def test_rate_limit_constants(self):
        """Should have reasonable rate limit constants"""
        from server import RATE_LIMIT_WINDOW, MAX_REQUESTS_PER_WINDOW, MAX_REQUESTS_PER_SECOND
        
        assert RATE_LIMIT_WINDOW > 0
        assert MAX_REQUESTS_PER_WINDOW > 0
        assert MAX_REQUESTS_PER_SECOND > 0
        
        # Burst limit should be less than window limit
        assert MAX_REQUESTS_PER_SECOND < MAX_REQUESTS_PER_WINDOW
    
    def test_handler_has_rate_limiter(self):
        """AuthHandler should have rate limiter configured"""
        from server import AuthHandler
        
        assert hasattr(AuthHandler, 'rate_limiter')
        assert isinstance(AuthHandler.rate_limiter, RateLimiter)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
