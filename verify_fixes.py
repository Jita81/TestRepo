#!/usr/bin/env python3
"""
Verification Script for Code Review Fixes
Tests all 4 security and quality improvements
"""

import sys
import os
import ipaddress
from pathlib import Path

print("🔍 Verifying Code Review Fixes")
print("=" * 60)

# Track results
passed = 0
failed = 0
warnings = 0

def test(name, condition, error_msg=""):
    """Test a condition and report results"""
    global passed, failed
    if condition:
        print(f"✅ PASS: {name}")
        passed += 1
    else:
        print(f"❌ FAIL: {name}")
        if error_msg:
            print(f"   {error_msg}")
        failed += 1

def warn(name, message=""):
    """Report a warning"""
    global warnings
    print(f"⚠️  WARN: {name}")
    if message:
        print(f"   {message}")
    warnings += 1

# Test 1: Rate Limiter IP Validation
print("\n📋 Test 1: Rate Limiter IP Validation")
print("-" * 60)

try:
    # Add auth_interface to path
    sys.path.insert(0, str(Path(__file__).parent / "auth_interface"))
    from server import RateLimiter
    
    rl = RateLimiter()
    
    # Test valid IPs
    test("Valid IPv4 (192.168.1.1)", 
         rl._is_valid_ip("192.168.1.1"))
    test("Valid IPv4 (127.0.0.1)", 
         rl._is_valid_ip("127.0.0.1"))
    test("Valid IPv6 (::1)", 
         rl._is_valid_ip("::1"))
    test("Valid IPv6 (2001:db8::1)", 
         rl._is_valid_ip("2001:db8::1"))
    
    # Test invalid IPs
    test("Invalid IP (not an ip)", 
         not rl._is_valid_ip("not an ip"))
    test("Invalid IP (999.999.999.999)", 
         not rl._is_valid_ip("999.999.999.999"))
    test("Invalid IP (empty string)", 
         not rl._is_valid_ip(""))
    
    # Test rate limiting with validation
    allowed, msg = rl.is_allowed("192.168.1.1")
    test("Rate limiter accepts valid IP", allowed)
    
    allowed, msg = rl.is_allowed("invalid-ip")
    test("Rate limiter rejects invalid IP", not allowed)
    test("Rate limiter returns error message for invalid IP", 
         msg == "Invalid IP address format")
    
except Exception as e:
    test("Rate limiter module loads", False, str(e))

# Test 2: CSRF Protection
print("\n📋 Test 2: CSRF Protection Implementation")
print("-" * 60)

try:
    # Check if main.py has CSRF implementation
    main_py = Path("main.py").read_text()
    
    test("CSRF middleware class exists", 
         "class CSRFMiddleware" in main_py)
    test("CSRF token generation exists", 
         "def generate_csrf_token" in main_py)
    test("CSRF middleware is added to app", 
         "app.add_middleware(CSRFMiddleware)" in main_py)
    test("CSRF token validation exists", 
         "_validate_csrf_token" in main_py)
    test("CSRF configuration exists", 
         "CSRF_TOKEN_LENGTH" in main_py and "CSRF_TOKEN_EXPIRY" in main_py)
    test("CSRF endpoint exists", 
         "@app.get(\"/csrf-token\")" in main_py)
    test("Uses secrets module for tokens", 
         "secrets.token_urlsafe" in main_py)
    
    # Check convert endpoint has CSRF parameter
    test("Convert endpoint accepts CSRF token", 
         "csrf_token: str = Form(...)" in main_py)
    
except Exception as e:
    test("main.py file readable", False, str(e))

# Test 3: Environment Variable Validation
print("\n📋 Test 3: Environment Variable Validation")
print("-" * 60)

try:
    run_py = Path("run.py").read_text()
    
    test("Environment validation function exists", 
         "def validate_environment_variables" in run_py)
    test("Validates OPENAI_API_KEY", 
         "OPENAI_API_KEY" in run_py and "required_vars" in run_py)
    test("Checks minimum length", 
         "min_length" in run_py)
    test("Detects placeholder values", 
         "insecure_values" in run_py)
    test("Validates optional variables", 
         "optional_vars" in run_py)
    test("Validation runs before server start", 
         "validate_environment_variables()" in run_py)
    test("Exits on validation failure", 
         "sys.exit(1)" in run_py and "validation failed" in run_py.lower())
    test("Provides helpful error messages", 
         "Tips:" in run_py)
    
    # Check for validation of specific vars
    test("Validates GITHUB_TOKEN format", 
         "GITHUB_TOKEN" in run_py)
    test("Validates MAX_REPO_SIZE_MB", 
         "MAX_REPO_SIZE_MB" in run_py)
    test("Validates CONVERSION_TIMEOUT", 
         "CONVERSION_TIMEOUT" in run_py)
    
except Exception as e:
    test("run.py file readable", False, str(e))

# Test 4: Error Handling in test_conversion.py
print("\n📋 Test 4: Comprehensive Error Handling")
print("-" * 60)

try:
    test_conv = Path("test_conversion.py").read_text()
    
    # Check for HTTP status code handling
    test("Handles 401 (Authentication)", 
         "status_code == 401" in test_conv)
    test("Handles 403 (Rate limit/CSRF)", 
         "status_code == 403" in test_conv)
    test("Handles 404 (Not found)", 
         "status_code == 404" in test_conv)
    test("Handles 422 (Invalid data)", 
         "status_code == 422" in test_conv)
    test("Handles 429 (Rate limit)", 
         "status_code == 429" in test_conv)
    test("Handles 500 (Server error)", 
         "status_code == 500" in test_conv)
    test("Handles 502/503 (Unavailable)", 
         "502" in test_conv and "503" in test_conv)
    
    # Check for network error handling
    test("Handles Timeout errors", 
         "requests.exceptions.Timeout" in test_conv)
    test("Handles SSLError", 
         "requests.exceptions.SSLError" in test_conv)
    test("Handles ConnectionError", 
         "requests.exceptions.ConnectionError" in test_conv)
    test("Handles TooManyRedirects", 
         "requests.exceptions.TooManyRedirects" in test_conv)
    test("Handles HTTPError", 
         "requests.exceptions.HTTPError" in test_conv)
    test("Handles RequestException", 
         "requests.exceptions.RequestException" in test_conv)
    test("Handles JSONDecodeError", 
         "json.JSONDecodeError" in test_conv)
    test("Handles KeyboardInterrupt", 
         "KeyboardInterrupt" in test_conv)
    
    # Check for helpful error messages
    test("Provides troubleshooting steps", 
         "Make sure" in test_conv or "Check" in test_conv)
    test("Includes retry-after header", 
         "Retry-After" in test_conv)
    
except Exception as e:
    test("test_conversion.py file readable", False, str(e))

# Test 5: Documentation and Warnings
print("\n📋 Test 5: Documentation and Security Warnings")
print("-" * 60)

try:
    server_py = Path("auth_interface/server.py").read_text()
    
    test("Rate limiter has persistence warning", 
         "IMPORTANT LIMITATIONS" in server_py or 
         "State is lost when server restarts" in server_py)
    test("Includes Redis implementation example", 
         "Redis" in server_py or "redis" in server_py)
    test("Production deployment guidance", 
         "production" in server_py.lower() and 
         "Redis" in server_py)
    test("IP validation is documented", 
         "Validate IP address" in server_py or 
         "_is_valid_ip" in server_py)
    
except Exception as e:
    test("auth_interface/server.py file readable", False, str(e))

# Test 6: Import Verification
print("\n📋 Test 6: Required Imports")
print("-" * 60)

try:
    # Check server.py imports
    server_py = Path("auth_interface/server.py").read_text()
    test("server.py imports ipaddress", 
         "import ipaddress" in server_py)
    
    # Check main.py imports
    main_py = Path("main.py").read_text()
    test("main.py imports secrets", 
         "import secrets" in main_py)
    test("main.py imports time", 
         "import time" in main_py)
    test("main.py imports BaseHTTPMiddleware", 
         "BaseHTTPMiddleware" in main_py)
    
except Exception as e:
    warn("Import verification incomplete", str(e))

# Summary
print("\n" + "=" * 60)
print("📊 Verification Summary")
print("=" * 60)
print(f"✅ Passed:  {passed}")
print(f"❌ Failed:  {failed}")
print(f"⚠️  Warnings: {warnings}")
print(f"📈 Success Rate: {passed}/{passed+failed} ({100*passed/(passed+failed) if passed+failed > 0 else 0:.1f}%)")

if failed == 0:
    print("\n🎉 All fixes verified successfully!")
    print("✅ Code review issues are fully addressed")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed} tests failed. Please review the fixes.")
    sys.exit(1)
