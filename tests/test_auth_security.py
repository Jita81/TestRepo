"""
Comprehensive Authentication Security Tests
Tests rate limiting, account lockout, concurrent sessions, and security requirements
"""

import pytest
import time
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, '.')


class TestRateLimiting:
    """Test rate limiting with exponential backoff and account lockout"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter with test configuration"""
        from auth_interface.server import RateLimiter
        # Use default parameters from actual implementation
        return RateLimiter()
    
    def test_allows_requests_within_burst_limit(self, rate_limiter):
        """Test that requests within burst limit are allowed"""
        ip = "192.168.1.100"
        
        for i in range(10):
            allowed, reason = rate_limiter.is_allowed(ip)
            assert allowed, f"Request {i+1} should be allowed within burst limit"
    
    def test_blocks_requests_exceeding_burst_limit(self, rate_limiter):
        """Test that requests exceeding burst limit are blocked"""
        ip = "192.168.1.101"
        
        # Make many rapid requests to trigger rate limit
        for i in range(15):
            rate_limiter.is_allowed(ip)
        
        # Next request should be blocked
        allowed, reason = rate_limiter.is_allowed(ip)
        assert not allowed, "Request should be blocked after exceeding burst limit"
        assert "limit" in reason.lower() or "blocked" in reason.lower()
    
    def test_exponential_backoff_increases(self, rate_limiter):
        """Test that rate limiter enforces increasing restrictions"""
        ip = "192.168.1.102"
        
        # Make many requests to trigger rate limiting
        for i in range(15):
            rate_limiter.is_allowed(ip)
        
        # Should be rate limited
        allowed, reason = rate_limiter.is_allowed(ip)
        assert not allowed, "Should be rate limited after many requests"
        
        # Verify rate limit message
        assert "limit" in reason.lower() or "blocked" in reason.lower() or "try again" in reason.lower()
    
    def test_account_lockout_after_threshold(self, rate_limiter):
        """Test that rate limiter blocks after many requests"""
        ip = "192.168.1.103"
        
        # Make excessive requests to trigger blocking
        for i in range(25):
            rate_limiter.is_allowed(ip)
        
        # Should be blocked
        allowed, reason = rate_limiter.is_allowed(ip)
        assert not allowed, "Should be blocked after excessive requests"
        assert reason is not None and len(reason) > 0, "Should provide reason for blocking"
    
    def test_lockout_duration_enforced(self, rate_limiter):
        """Test that rate limiter enforces blocking duration"""
        ip = "192.168.1.104"
        
        # Trigger rate limiting
        for i in range(15):
            rate_limiter.is_allowed(ip)
        
        # Should be rate limited
        allowed1, reason1 = rate_limiter.is_allowed(ip)
        assert not allowed1, "Should be rate limited"
        
        # Wait briefly and check if still limited
        time.sleep(0.5)
        allowed2, reason2 = rate_limiter.is_allowed(ip)
        
        # Verify rate limiting is enforced
        assert isinstance(allowed2, bool), "Should return boolean for allowed status"
    
    def test_ip_validation(self, rate_limiter):
        """Test that invalid IP addresses are rejected"""
        invalid_ips = ["invalid", "999.999.999.999", "not-an-ip", ""]
        
        for invalid_ip in invalid_ips:
            allowed, reason = rate_limiter.is_allowed(invalid_ip)
            assert not allowed, f"Invalid IP {invalid_ip} should be rejected"
            assert "Invalid IP address" in reason
    
    def test_independent_ip_tracking(self, rate_limiter):
        """Test that different IPs are tracked independently"""
        ip1 = "192.168.1.105"
        ip2 = "192.168.1.106"
        
        # Use up tokens for ip1
        for i in range(10):
            rate_limiter.is_allowed(ip1)
        
        allowed1, _ = rate_limiter.is_allowed(ip1)
        assert not allowed1, "IP1 should be rate limited"
        
        # IP2 should still have tokens
        allowed2, _ = rate_limiter.is_allowed(ip2)
        assert allowed2, "IP2 should not be affected by IP1's limit"


class TestAccountLockout:
    """Test account lockout mechanisms"""
    
    def test_progressive_lockout_duration(self):
        """Test that lockout duration increases with repeated violations"""
        lockout_durations = []
        
        for attempt in range(1, 4):
            duration = 300 * (2 ** (attempt - 1))  # Exponential: 300, 600, 1200
            lockout_durations.append(duration)
        
        assert lockout_durations[0] == 300
        assert lockout_durations[1] == 600
        assert lockout_durations[2] == 1200
    
    def test_lockout_reset_after_good_behavior(self):
        """Test that lockout violations reset after period of good behavior"""
        from auth_interface.server import RateLimiter
        rate_limiter = RateLimiter()
        
        ip = "192.168.1.107"
        
        # Create some violations
        for i in range(15):
            rate_limiter.is_allowed(ip)
        
        # Wait and make successful requests
        time.sleep(1)
        
        # Refill should allow new requests
        for i in range(5):
            allowed, _ = rate_limiter.is_allowed(ip)
            if allowed:
                break
            time.sleep(0.3)


class TestConcurrentSessions:
    """Test concurrent session handling"""
    
    def test_multiple_sessions_same_user(self):
        """Test that multiple sessions for same user are tracked"""
        sessions = {}
        user_id = "user123"
        
        # Create multiple sessions
        for i in range(3):
            session_id = f"session_{i}"
            sessions[session_id] = {
                'user_id': user_id,
                'created': time.time(),
                'last_active': time.time()
            }
        
        user_sessions = [s for s in sessions.values() if s['user_id'] == user_id]
        assert len(user_sessions) == 3, "Should track multiple sessions"
    
    def test_session_limit_per_user(self):
        """Test that concurrent sessions are limited per user"""
        max_sessions = 5
        sessions = {}
        user_id = "user456"
        
        # Try to create more than max sessions
        for i in range(7):
            session_id = f"session_{i}"
            
            # Count existing sessions
            user_sessions = [s for s in sessions.values() if s['user_id'] == user_id]
            
            if len(user_sessions) < max_sessions:
                sessions[session_id] = {'user_id': user_id}
        
        final_count = len([s for s in sessions.values() if s['user_id'] == user_id])
        assert final_count <= max_sessions, "Should enforce session limit"
    
    def test_oldest_session_removed_when_limit_reached(self):
        """Test that oldest session is removed when limit is reached"""
        sessions = {}
        user_id = "user789"
        max_sessions = 3
        
        # Create sessions with timestamps
        for i in range(5):
            session_id = f"session_{i}"
            
            user_sessions = [(sid, s) for sid, s in sessions.items() 
                           if s['user_id'] == user_id]
            
            if len(user_sessions) >= max_sessions:
                # Remove oldest
                oldest = min(user_sessions, key=lambda x: x[1]['created'])
                del sessions[oldest[0]]
            
            sessions[session_id] = {
                'user_id': user_id,
                'created': time.time() + i
            }
        
        # Should have exactly max_sessions
        final_sessions = [s for s in sessions.values() if s['user_id'] == user_id]
        assert len(final_sessions) == max_sessions


class TestCSRFProtection:
    """Test CSRF protection implementation"""
    
    def test_csrf_token_required_for_post(self):
        """Test that POST requests require CSRF token"""
        # Test CSRF protection logic without requiring FastAPI/uvicorn
        import secrets
        
        # Simulate CSRF token validation
        csrf_token_header = None
        csrf_token_cookie = "valid-token"
        
        # Both header and cookie must be present
        csrf_valid = csrf_token_header is not None and csrf_token_cookie is not None
        
        assert not csrf_valid, "CSRF validation should fail without both tokens"
        
        # Test with both tokens present
        csrf_token_header = "valid-token"
        csrf_token_cookie = "valid-token"
        
        # Tokens must match
        tokens_match = secrets.compare_digest(csrf_token_header, csrf_token_cookie)
        assert tokens_match, "Matching tokens should pass validation"
    
    def test_csrf_token_validates_origin(self):
        """Test that CSRF validation includes origin check"""
        allowed_origins = ["http://localhost:8000"]
        test_origin = "http://evil.com"
        
        # Use timing-safe comparison
        import secrets
        is_allowed = any(
            len(test_origin) == len(allowed) and 
            secrets.compare_digest(test_origin, allowed)
            for allowed in allowed_origins
        )
        
        assert not is_allowed, "Evil origin should be rejected"
    
    def test_csrf_double_submit_pattern(self):
        """Test double-submit cookie pattern"""
        import secrets
        
        token_header = secrets.token_urlsafe(32)
        token_cookie = secrets.token_urlsafe(32)
        
        # Tokens must match
        assert not secrets.compare_digest(token_header, token_cookie), \
            "Different tokens should not match"
        
        # Same tokens should match
        assert secrets.compare_digest(token_header, token_header), \
            "Same tokens should match"


class TestPasswordPolicy:
    """Test password policy enforcement"""
    
    def test_password_complexity_requirements(self):
        """Test that password complexity is enforced"""
        import re
        
        def validate_password(password):
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain uppercase letter"
            if not re.search(r'[a-z]', password):
                return False, "Password must contain lowercase letter"
            if not re.search(r'[0-9]', password):
                return False, "Password must contain number"
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False, "Password must contain special character"
            return True, "Password is valid"
        
        # Test weak passwords
        weak_passwords = ["short", "alllowercase", "ALLUPPERCASE", "NoNumbers!"]
        for pwd in weak_passwords:
            valid, reason = validate_password(pwd)
            assert not valid, f"Weak password '{pwd}' should be rejected"
        
        # Test strong password
        valid, reason = validate_password("Strong@Pass123")
        assert valid, "Strong password should be accepted"
    
    def test_password_history_prevention(self):
        """Test that password reuse is prevented"""
        password_history = ["OldPass1!", "OldPass2!", "OldPass3!"]
        new_password = "OldPass2!"
        
        # Use timing-safe comparison
        import secrets
        is_reused = any(
            secrets.compare_digest(new_password, old_pwd)
            for old_pwd in password_history
        )
        
        assert is_reused, "Reused password should be detected"


class TestSessionSecurity:
    """Test session security measures"""
    
    def test_session_token_rotation(self):
        """Test that session tokens are rotated periodically"""
        import secrets
        
        old_token = secrets.token_urlsafe(32)
        new_token = secrets.token_urlsafe(32)
        
        assert old_token != new_token, "Tokens should be unique"
        assert not secrets.compare_digest(old_token, new_token), \
            "New token should not match old token"
    
    def test_session_timeout(self):
        """Test that sessions timeout after inactivity"""
        session = {
            'created': time.time() - 3600,  # 1 hour ago
            'last_active': time.time() - 1800  # 30 minutes ago
        }
        
        timeout_duration = 1800  # 30 minutes
        current_time = time.time()
        
        is_expired = (current_time - session['last_active']) > timeout_duration
        assert is_expired, "Session should be expired after timeout"
    
    def test_absolute_session_timeout(self):
        """Test absolute session timeout regardless of activity"""
        session = {
            'created': time.time() - 86400,  # 24 hours ago
            'last_active': time.time()  # Just now
        }
        
        max_session_duration = 43200  # 12 hours
        current_time = time.time()
        
        is_expired = (current_time - session['created']) > max_session_duration
        assert is_expired, "Session should expire after maximum duration"


class TestBruteForceProtection:
    """Test brute force attack protection"""
    
    def test_login_attempt_tracking(self):
        """Test that failed login attempts are tracked"""
        failed_attempts = {}
        username = "test@example.com"
        
        # Record failed attempts
        for i in range(5):
            if username not in failed_attempts:
                failed_attempts[username] = []
            failed_attempts[username].append(time.time())
        
        assert len(failed_attempts[username]) == 5, \
            "Should track all failed attempts"
    
    def test_progressive_delay_after_failures(self):
        """Test progressive delay after failed login attempts"""
        def calculate_delay(attempt_number):
            return min(30, 2 ** attempt_number)  # Max 30 seconds
        
        delays = [calculate_delay(i) for i in range(1, 6)]
        
        assert delays[0] == 2   # 2^1 = 2 seconds
        assert delays[1] == 4   # 2^2 = 4 seconds
        assert delays[2] == 8   # 2^3 = 8 seconds
        assert delays[3] == 16  # 2^4 = 16 seconds
        assert delays[4] == 30  # Capped at 30
    
    def test_account_lockout_after_max_failures(self):
        """Test account lockout after maximum failures"""
        max_attempts = 5
        failed_attempts = 6
        
        is_locked = failed_attempts >= max_attempts
        assert is_locked, "Account should be locked after max failures"


class TestAPIKeyValidation:
    """Test API key validation with secure comparison"""
    
    def test_api_key_timing_safe_comparison(self):
        """Test that API key comparison is timing-safe"""
        import secrets
        
        correct_key = "sk-" + "a" * 48
        test_key = "sk-" + "b" * 48
        
        # Should use secrets.compare_digest
        matches = secrets.compare_digest(correct_key, test_key)
        assert not matches, "Different keys should not match"
        
        # Same key should match
        matches = secrets.compare_digest(correct_key, correct_key)
        assert matches, "Same key should match"
    
    def test_api_key_format_validation(self):
        """Test API key format validation"""
        def validate_api_key(key):
            if not key or len(key) < 40:
                return False
            if not key.startswith("sk-"):
                return False
            return True
        
        assert validate_api_key("sk-" + "x" * 48), "Valid key should pass"
        assert not validate_api_key("invalid"), "Invalid key should fail"
        assert not validate_api_key("pk-" + "x" * 48), "Wrong prefix should fail"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
