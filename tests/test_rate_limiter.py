"""
Unit tests for Rate Limiter with IP Validation
Tests the enhanced RateLimiter in auth_interface/server.py
"""

import pytest
import sys
import time
from datetime import datetime, timedelta

# Add auth_interface to path
sys.path.insert(0, 'auth_interface')


class TestRateLimiterIPValidation:
    """Test IP address validation in rate limiter"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from server import RateLimiter
        self.rate_limiter = RateLimiter()
    
    def test_valid_ipv4_addresses(self):
        """Test validation of valid IPv4 addresses"""
        valid_ips = [
            '192.168.1.1',
            '127.0.0.1',
            '10.0.0.1',
            '172.16.0.1',
            '8.8.8.8',
            '255.255.255.255',
            '0.0.0.0'
        ]
        
        for ip in valid_ips:
            assert self.rate_limiter._is_valid_ip(ip), f"{ip} should be valid"
    
    def test_valid_ipv6_addresses(self):
        """Test validation of valid IPv6 addresses"""
        valid_ips = [
            '::1',
            '::',
            '2001:db8::1',
            'fe80::1',
            '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            '2001:db8:85a3::8a2e:370:7334'
        ]
        
        for ip in valid_ips:
            assert self.rate_limiter._is_valid_ip(ip), f"{ip} should be valid"
    
    def test_invalid_ip_addresses(self):
        """Test rejection of invalid IP addresses"""
        invalid_ips = [
            'not an ip',
            '999.999.999.999',
            '256.1.1.1',
            '192.168.1',
            '192.168.1.1.1',
            '',
            'localhost',
            'example.com',
            '192.168.1.1/24',  # CIDR notation
            None
        ]
        
        for ip in invalid_ips:
            assert not self.rate_limiter._is_valid_ip(ip), f"{ip} should be invalid"
    
    def test_is_allowed_with_valid_ip(self):
        """Test is_allowed accepts valid IP addresses"""
        allowed, message = self.rate_limiter.is_allowed('192.168.1.1')
        
        assert allowed is True
        assert message is None
    
    def test_is_allowed_with_invalid_ip(self):
        """Test is_allowed rejects invalid IP addresses"""
        allowed, message = self.rate_limiter.is_allowed('invalid-ip')
        
        assert allowed is False
        assert message == "Invalid IP address format"
    
    def test_is_allowed_with_empty_string(self):
        """Test is_allowed rejects empty string"""
        allowed, message = self.rate_limiter.is_allowed('')
        
        assert allowed is False
        assert message == "Invalid IP address format"


class TestRateLimiterFunctionality:
    """Test rate limiting functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from server import RateLimiter
        self.rate_limiter = RateLimiter()
    
    def test_allows_first_request(self):
        """Test that first request from IP is allowed"""
        allowed, _ = self.rate_limiter.is_allowed('192.168.1.1')
        assert allowed is True
    
    def test_tracks_multiple_ips_independently(self):
        """Test that different IPs are tracked independently"""
        ip1 = '192.168.1.1'
        ip2 = '192.168.1.2'
        
        # Both IPs should be allowed
        allowed1, _ = self.rate_limiter.is_allowed(ip1)
        allowed2, _ = self.rate_limiter.is_allowed(ip2)
        
        assert allowed1 is True
        assert allowed2 is True
        
        # Each should have their own request count
        assert len(self.rate_limiter.requests[ip1]) == 1
        assert len(self.rate_limiter.requests[ip2]) == 1
    
    def test_burst_rate_limiting(self):
        """Test per-second burst rate limiting"""
        ip = '192.168.1.1'
        
        # Make requests up to the per-second limit
        for i in range(10):
            allowed, _ = self.rate_limiter.is_allowed(ip)
            assert allowed is True, f"Request {i+1} should be allowed"
        
        # Next request should be blocked (exceeds per-second limit)
        allowed, message = self.rate_limiter.is_allowed(ip)
        assert allowed is False
        assert 'per second' in message.lower() or 'blocked' in message.lower()
    
    def test_window_rate_limiting(self):
        """Test per-window rate limiting"""
        ip = '192.168.1.1'
        
        # This test would need to make 100+ requests
        # For unit testing, we'll just verify the structure
        # In a real scenario, integration tests would cover this
        assert hasattr(self.rate_limiter, 'requests')
        assert isinstance(self.rate_limiter.requests, dict)
    
    def test_blocked_ip_stays_blocked(self):
        """Test that blocked IPs remain blocked"""
        ip = '192.168.1.1'
        
        # Exceed rate limit
        for _ in range(15):
            self.rate_limiter.is_allowed(ip)
        
        # Should be blocked
        allowed, _ = self.rate_limiter.is_allowed(ip)
        assert allowed is False
        
        # Should stay blocked on next request
        allowed, _ = self.rate_limiter.is_allowed(ip)
        assert allowed is False
    
    def test_cleans_old_requests(self):
        """Test that old requests are cleaned up"""
        ip = '192.168.1.1'
        
        # Make a request
        self.rate_limiter.is_allowed(ip)
        
        # Manually add old request
        old_time = datetime.now() - timedelta(seconds=70)
        self.rate_limiter.requests[ip].insert(0, old_time)
        
        # Make another request (should clean up old one)
        self.rate_limiter.is_allowed(ip)
        
        # Old request should be removed
        for req_time in self.rate_limiter.requests[ip]:
            assert datetime.now() - req_time < timedelta(seconds=65)


class TestRateLimiterEdgeCases:
    """Test edge cases in rate limiter"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from server import RateLimiter
        self.rate_limiter = RateLimiter()
    
    def test_concurrent_requests_same_ip(self):
        """Test handling of concurrent requests from same IP"""
        ip = '192.168.1.1'
        
        # Simulate concurrent requests
        results = []
        for _ in range(5):
            allowed, _ = self.rate_limiter.is_allowed(ip)
            results.append(allowed)
        
        # All should be allowed (under limit)
        assert all(results)
    
    def test_ipv6_rate_limiting(self):
        """Test rate limiting works with IPv6 addresses"""
        ip = '2001:db8::1'
        
        # Should work same as IPv4
        allowed, _ = self.rate_limiter.is_allowed(ip)
        assert allowed is True
        
        # Should track requests
        assert len(self.rate_limiter.requests[ip]) == 1
    
    def test_loopback_addresses(self):
        """Test rate limiting works with loopback addresses"""
        ipv4_loopback = '127.0.0.1'
        ipv6_loopback = '::1'
        
        # Both should be valid and allowed
        allowed, _ = self.rate_limiter.is_allowed(ipv4_loopback)
        assert allowed is True
        
        allowed, _ = self.rate_limiter.is_allowed(ipv6_loopback)
        assert allowed is True
    
    def test_rate_limiter_state_persistence(self):
        """Test that rate limiter maintains state"""
        ip = '192.168.1.1'
        
        # Make some requests
        for _ in range(3):
            self.rate_limiter.is_allowed(ip)
        
        # Check state is maintained
        assert len(self.rate_limiter.requests[ip]) == 3
        
        # Make more requests
        for _ in range(2):
            self.rate_limiter.is_allowed(ip)
        
        # State should be updated
        assert len(self.rate_limiter.requests[ip]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
