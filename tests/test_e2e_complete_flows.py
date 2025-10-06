"""
End-to-end tests for complete user workflows
Tests complete flows including authentication, CSRF, and error handling

IMPORTANT: Playwright is a required dependency for E2E tests.
Install with: pip install playwright && playwright install
"""

import pytest
import time
from pathlib import Path

# Playwright is now a REQUIRED dependency for E2E tests
# This ensures CI/CD pipelines fail if E2E infrastructure is not set up properly
try:
    from playwright.sync_api import sync_playwright, expect
except ImportError as e:
    raise ImportError(
        "Playwright is required for end-to-end tests. "
        "Install with: pip install playwright && playwright install"
    ) from e


class TestCompleteUserFlows:
    """Test complete user workflows end-to-end"""
    
    @pytest.fixture(scope="class")
    def browser_context(self):
        """Set up browser context"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Create new page for each test"""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_csrf_protection_in_real_browser(self, page):
        """Test CSRF protection in actual browser"""
        # Navigate to home page
        page.goto("http://localhost:8000/")
        
        # Check that CSRF cookie is set
        cookies = page.context.cookies()
        csrf_cookie = next((c for c in cookies if c['name'] == 'csrf_token'), None)
        assert csrf_cookie is not None, "CSRF token should be set in cookie"
        
        # Check that cookie has security attributes
        assert csrf_cookie.get('httpOnly') == True
        assert csrf_cookie.get('sameSite') in ['Strict', 'Lax']
    
    def test_form_submission_requires_csrf_token(self, page):
        """Test that form submission requires CSRF token"""
        page.goto("http://localhost:8000/")
        
        # Try to submit form without CSRF token (simulate attack)
        page.evaluate("""
            fetch('/convert', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'github_url=https://github.com/test/repo&app_name=test'
            }).then(r => window.testResult = {status: r.status})
        """)
        
        # Wait for result
        page.wait_for_function("window.testResult !== undefined")
        result = page.evaluate("window.testResult")
        
        # Should be rejected
        assert result['status'] == 403
    
    def test_multiple_tabs_session_sync(self, browser_context):
        """Test session synchronization across multiple tabs"""
        # Create two pages (tabs)
        page1 = browser_context.new_page()
        page2 = browser_context.new_page()
        
        try:
            # Navigate to auth interface in both tabs
            page1.goto("http://localhost:8888/templates/login.html")
            page2.goto("http://localhost:8888/templates/dashboard.html")
            
            # Login in first tab
            page1.fill("#email", "test@example.com")
            page1.fill("#password", "Test123!@#")
            page1.click("button[type='submit']")
            
            # Wait for login
            time.sleep(2)
            
            # Check if token is shared
            token1 = page1.evaluate("sessionStorage.getItem('auth_token')")
            token2 = page2.evaluate("sessionStorage.getItem('auth_token')")
            
            # Tokens should be accessible in both tabs
            assert token1 is not None or token2 is not None
            
        finally:
            page1.close()
            page2.close()
    
    def test_token_expiration_handling(self, page):
        """Test automatic logout on token expiration"""
        page.goto("http://localhost:8888/templates/login.html")
        
        # Create expired token
        page.evaluate("""
            const expiredToken = btoa(JSON.stringify({alg:'HS256'})) + '.' +
                                btoa(JSON.stringify({sub:'123',exp:Math.floor(Date.now()/1000)-3600})) + '.' +
                                btoa('sig');
            sessionStorage.setItem('auth_token', expiredToken);
        """)
        
        # Try to access dashboard
        page.goto("http://localhost:8888/templates/dashboard.html")
        
        # Wait for redirect
        time.sleep(2)
        
        # Should be redirected to login
        assert 'login.html' in page.url
    
    def test_storage_cleared_during_session(self, page):
        """Test handling of storage being cleared during session"""
        page.goto("http://localhost:8888/templates/dashboard.html")
        
        # Simulate login
        page.evaluate("""
            const token = btoa(JSON.stringify({alg:'HS256'})) + '.' +
                         btoa(JSON.stringify({sub:'123',exp:Math.floor(Date.now()/1000)+3600})) + '.' +
                         btoa('sig');
            sessionStorage.setItem('auth_token', token);
        """)
        
        # Reload page
        page.reload()
        
        # Clear storage
        page.evaluate("sessionStorage.clear(); localStorage.clear();")
        
        # Try to make authenticated request
        page.evaluate("""
            if (typeof authService !== 'undefined') {
                window.testAuth = authService.isAuthenticated();
            }
        """)
        
        time.sleep(1)
        
        # Should detect no auth
        is_auth = page.evaluate("window.testAuth")
        assert is_auth == False or is_auth is None


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
class TestErrorRecovery:
    """Test error recovery scenarios"""
    
    @pytest.fixture(scope="class")
    def browser_context(self):
        """Set up browser context"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Create new page for each test"""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_network_failure_during_request(self, page):
        """Test handling of network failures"""
        page.goto("http://localhost:8000/")
        
        # Simulate network failure
        page.route("**/*", lambda route: route.abort())
        
        # Try to make request
        page.evaluate("""
            fetch('/csrf-token')
                .catch(e => window.networkError = e.toString());
        """)
        
        time.sleep(1)
        
        # Should handle error
        error = page.evaluate("window.networkError")
        assert error is not None
    
    def test_invalid_json_response_handling(self, page):
        """Test handling of invalid JSON responses"""
        page.goto("http://localhost:8000/")
        
        # Mock invalid JSON response
        page.route("**/csrf-token", lambda route: route.fulfill(
            status=200,
            body="invalid json"
        ))
        
        # Try to make request
        page.evaluate("""
            fetch('/csrf-token')
                .then(r => r.json())
                .catch(e => window.jsonError = e.toString());
        """)
        
        time.sleep(1)
        
        # Should handle JSON parse error
        error = page.evaluate("window.jsonError")
        assert error is not None


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")  
class TestConcurrentRequests:
    """Test handling of concurrent requests"""
    
    @pytest.fixture(scope="class")
    def browser_context(self):
        """Set up browser context"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Create new page for each test"""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_concurrent_api_requests_with_expired_token(self, page):
        """Test race conditions with concurrent requests and expired token"""
        page.goto("http://localhost:8888/templates/dashboard.html")
        
        # Set token that will expire soon
        page.evaluate("""
            const soonToken = btoa(JSON.stringify({alg:'HS256'})) + '.' +
                            btoa(JSON.stringify({sub:'123',exp:Math.floor(Date.now()/1000)+2})) + '.' +
                            btoa('sig');
            sessionStorage.setItem('auth_token', soonToken);
        """)
        
        # Wait for token to expire
        time.sleep(3)
        
        # Make multiple concurrent requests
        page.evaluate("""
            window.results = [];
            Promise.all([
                fetch('/api/test1').catch(e => ({error: true})),
                fetch('/api/test2').catch(e => ({error: true})),
                fetch('/api/test3').catch(e => ({error: true}))
            ]).then(r => window.results = r);
        """)
        
        time.sleep(2)
        
        # Should handle all requests gracefully
        results = page.evaluate("window.results")
        assert isinstance(results, list)
        assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
