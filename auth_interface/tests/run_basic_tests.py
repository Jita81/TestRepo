#!/usr/bin/env python3
"""
Basic test runner that doesn't require pytest
Runs simple validation tests for the server module
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import RateLimiter, find_free_port, RATE_LIMIT_WINDOW, MAX_REQUESTS_PER_WINDOW, MAX_REQUESTS_PER_SECOND


def test_rate_limiter_allows_requests():
    """Test that rate limiter allows requests within limit"""
    print("Testing: Rate limiter allows requests...")
    limiter = RateLimiter()
    ip = '127.0.0.1'
    
    allowed, msg = limiter.is_allowed(ip)
    assert allowed is True, "First request should be allowed"
    assert msg is None, "Should have no error message"
    print("✅ PASS: Rate limiter allows first request")


def test_rate_limiter_blocks_burst():
    """Test that rate limiter blocks burst requests"""
    print("\nTesting: Rate limiter blocks burst requests...")
    limiter = RateLimiter()
    ip = '127.0.0.1'
    
    # Make requests up to burst limit
    for i in range(MAX_REQUESTS_PER_SECOND):
        allowed, msg = limiter.is_allowed(ip)
        assert allowed is True, f"Request {i+1} should be allowed"
    
    # Next request should be blocked
    allowed, msg = limiter.is_allowed(ip)
    assert allowed is False, "Request exceeding burst limit should be blocked"
    assert 'second' in msg.lower(), "Error message should mention 'second'"
    print(f"✅ PASS: Rate limiter blocks after {MAX_REQUESTS_PER_SECOND} requests/second")


def test_rate_limiter_separate_ips():
    """Test that rate limiter tracks IPs separately"""
    print("\nTesting: Rate limiter tracks IPs separately...")
    limiter = RateLimiter()
    
    # Fill limit for first IP
    for i in range(MAX_REQUESTS_PER_SECOND):
        limiter.is_allowed('192.168.1.1')
    
    # Second IP should still be allowed
    allowed, msg = limiter.is_allowed('192.168.1.2')
    assert allowed is True, "Different IP should not be affected"
    print("✅ PASS: Rate limiter tracks IPs independently")


def test_find_free_port():
    """Test port finding functionality"""
    print("\nTesting: Find free port...")
    port = find_free_port(8000)
    assert port is not None, "Should find a free port"
    assert port >= 8000, "Port should be at least start port"
    assert port < 8010, "Port should be within range"
    print(f"✅ PASS: Found free port: {port}")


def test_rate_limit_constants():
    """Test rate limit configuration"""
    print("\nTesting: Rate limit constants...")
    assert RATE_LIMIT_WINDOW > 0, "Window should be positive"
    assert MAX_REQUESTS_PER_WINDOW > 0, "Max requests should be positive"
    assert MAX_REQUESTS_PER_SECOND > 0, "Burst limit should be positive"
    assert MAX_REQUESTS_PER_SECOND < MAX_REQUESTS_PER_WINDOW, "Burst should be less than window limit"
    print(f"✅ PASS: Rate limits configured correctly")
    print(f"   - Window: {RATE_LIMIT_WINDOW}s")
    print(f"   - Max requests: {MAX_REQUESTS_PER_WINDOW}")
    print(f"   - Burst limit: {MAX_REQUESTS_PER_SECOND} req/s")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Running Basic Server Tests")
    print("="*60)
    
    tests = [
        test_rate_limiter_allows_requests,
        test_rate_limiter_blocks_burst,
        test_rate_limiter_separate_ips,
        test_find_free_port,
        test_rate_limit_constants
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
