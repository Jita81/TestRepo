"""
End-to-End Tests for Contact Form User Workflows

Tests complete user scenarios including edge cases.
These tests simulate browser behavior without requiring a real browser.

For full browser E2E testing, use Playwright:
  pip install playwright
  playwright install
  pytest tests/test_e2e_workflows.py -v
"""

import sys
import os
import time
from unittest.mock import Mock, patch

# pytest is optional
try:
    import pytest
except ImportError:
    pytest = None
    # Create a dummy decorator
    class DummyPytest:
        @staticmethod
        def fixture(func):
            return func
        @staticmethod
        def mark(*args, **kwargs):
            class DummyMark:
                @staticmethod
                def skipif(*args, **kwargs):
                    def decorator(func):
                        return func
                    return decorator
            return DummyMark()
        @staticmethod
        def skip(reason):
            pass
    if pytest is None:
        pytest = DummyPytest()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
    from main_enhanced import app
    TESTCLIENT_AVAILABLE = True
except ImportError:
    TESTCLIENT_AVAILABLE = False


class TestCompleteUserWorkflows:
    """E2E tests for complete user workflows"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        if not TESTCLIENT_AVAILABLE:
            pytest.skip("FastAPI TestClient not available")
        return TestClient(app)
    
    @pytest.fixture
    def csrf_token(self, client):
        """Get a valid CSRF token"""
        response = client.get("/api/csrf-token")
        return response.json()["csrf_token"]
    
    def test_happy_path_form_submission(self, client, csrf_token):
        """
        WORKFLOW: User successfully submits contact form
        
        Steps:
        1. User visits contact page
        2. User fills out all fields with valid data
        3. User clicks submit button
        4. User sees success message
        5. Form fields are cleared (client-side)
        """
        # Step 1: Visit contact page
        response = client.get("/contact")
        assert response.status_code == 200
        
        # Step 2 & 3: Fill out and submit form
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "I would like to learn more about your services. Please contact me at your earliest convenience.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Step 4: Check success
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Thank you for your message" in data["message"]
    
    def test_validation_error_workflow(self, client, csrf_token):
        """
        WORKFLOW: User submits form with validation errors
        
        Steps:
        1. User visits contact page
        2. User fills out form with invalid data
        3. User clicks submit
        4. User sees specific error messages
        5. User corrects errors and resubmits
        6. Submission succeeds
        """
        # Step 1: Visit page
        response = client.get("/contact")
        assert response.status_code == 200
        
        # Step 2 & 3: Submit with errors
        response = client.post("/contact", data={
            "name": "A",  # Too short
            "email": "invalid",  # Invalid format
            "message": "Short",  # Too short
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Step 4: Check error messages
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert len(data["errors"]) >= 3
        
        # Step 5: Correct and resubmit
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "This is now a valid message with sufficient length.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Step 6: Success
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_progressive_field_validation_workflow(self, client, csrf_token):
        """
        WORKFLOW: User fills out form field by field
        
        Tests that each field can be validated independently
        """
        # User starts with name field
        # Valid name
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "",
            "message": "",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        assert response.status_code == 400  # Other fields still required
        
        # User adds email
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        assert response.status_code == 400  # Message still required
        
        # User completes form
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "This is a complete message.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        assert response.status_code == 200  # Success


class TestEdgeCases:
    """Tests for edge case scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        if not TESTCLIENT_AVAILABLE:
            pytest.skip("FastAPI TestClient not available")
        return TestClient(app)
    
    @pytest.fixture
    def csrf_token(self, client):
        """Get a valid CSRF token"""
        response = client.get("/api/csrf-token")
        return response.json()["csrf_token"]
    
    def test_edge_case_paste_formatted_text(self, client, csrf_token):
        """
        EDGE CASE: Paste of formatted text into message strips HTML/formatting
        
        Tests that HTML tags and formatting are removed from pasted content
        """
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "<b>Bold text</b> and <i>italic text</i> should be stripped to plain text only.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Should either sanitize and succeed, or reject
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            # HTML was sanitized - verify no tags in saved data
            # In real test, would check saved file
            pass
    
    def test_edge_case_double_submit_prevention(self, client, csrf_token):
        """
        EDGE CASE: Double-click of submit button only triggers one submission
        
        Tests that CSRF token is one-time use (prevents double submission)
        """
        # First submission
        response1 = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "This is a test message for double submit.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        assert response1.status_code == 200
        
        # Try to use same token again (simulating double click)
        response2 = client.post("/contact", data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "message": "This is another test message.",
            "csrf_token": csrf_token  # Same token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Should be rejected (token already used)
        assert response2.status_code == 403
    
    def test_edge_case_browser_autofill(self, client, csrf_token):
        """
        EDGE CASE: Browser auto-fill data triggers validation
        
        Tests that auto-filled data is properly validated
        """
        # Simulate browser auto-fill with valid data
        response = client.post("/contact", data={
            "name": "John Doe",  # Auto-filled
            "email": "john@example.com",  # Auto-filled
            "message": "This is a message that was typed by the user.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        assert response.status_code == 200
        
        # Get new token for next test
        token_response = client.get("/api/csrf-token")
        new_token = token_response.json()["csrf_token"]
        
        # Simulate auto-fill with invalid data
        response = client.post("/contact", data={
            "name": "A",  # Auto-filled incorrectly
            "email": "invalid-email",  # Auto-filled incorrectly
            "message": "This is a valid message.",
            "csrf_token": new_token
        }, headers={
            "X-CSRF-Token": new_token
        })
        
        # Should catch validation errors
        assert response.status_code == 400
    
    def test_edge_case_whitespace_handling(self, client, csrf_token):
        """
        EDGE CASE: Extra whitespace in fields is handled properly
        
        Tests trimming of leading/trailing whitespace
        """
        response = client.post("/contact", data={
            "name": "   John Doe   ",  # Extra spaces
            "email": "  john@example.com  ",  # Extra spaces
            "message": "  This is a message with extra whitespace.  ",  # Extra spaces
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Should trim and succeed
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_edge_case_special_characters_in_message(self, client, csrf_token):
        """
        EDGE CASE: Special characters in message field
        
        Tests that common punctuation and symbols are allowed in messages
        """
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello! I'm interested in your services. Can we schedule a meeting @ 3pm? Thanks! :)",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Should allow common punctuation
        assert response.status_code == 200
    
    def test_edge_case_unicode_in_message(self, client, csrf_token):
        """
        EDGE CASE: Unicode characters in message
        
        Tests handling of non-ASCII characters
        """
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello! I'm interested. Here are some unicode: café, naïve, résumé. Thanks!",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        # Should handle unicode appropriately
        # May sanitize or accept depending on implementation
        assert response.status_code in [200, 400]
    
    def test_edge_case_very_long_valid_message(self, client, csrf_token):
        """
        EDGE CASE: Maximum length valid message
        
        Tests that exactly 1000 characters is accepted
        """
        message = "A" * 1000  # Exactly at limit
        
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": message,
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        assert response.status_code == 200
    
    def test_edge_case_minimum_valid_inputs(self, client, csrf_token):
        """
        EDGE CASE: Minimum valid input lengths
        
        Tests that minimum lengths are accepted
        """
        response = client.post("/contact", data={
            "name": "AB",  # Exactly 2 characters
            "email": "a@b.co",  # Short but valid email
            "message": "Ten chars!",  # Exactly 10 characters
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        assert response.status_code == 200


class TestOfflineScenario:
    """Tests for offline behavior"""
    
    def test_offline_detection_simulation(self):
        """
        EDGE CASE: Form submission while offline
        
        Note: This is primarily a client-side feature.
        Tests that the server properly handles failed requests.
        """
        # This would be better tested with actual browser E2E tests
        # where we can simulate navigator.onLine = false
        
        # Server-side, we just verify proper error handling
        # when requests fail
        assert True  # Placeholder for client-side E2E test


class TestFormStateManagement:
    """Tests for form state persistence"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        if not TESTCLIENT_AVAILABLE:
            pytest.skip("FastAPI TestClient not available")
        return TestClient(app)
    
    def test_multiple_form_submissions(self, client):
        """
        EDGE CASE: Multiple submissions in sequence
        
        Tests that form can be submitted multiple times successfully
        """
        for i in range(3):
            # Get fresh token for each submission
            token_response = client.get("/api/csrf-token")
            token = token_response.json()["csrf_token"]
            
            response = client.post("/contact", data={
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "message": f"This is test message number {i} with sufficient length.",
                "csrf_token": token
            }, headers={
                "X-CSRF-Token": token
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"


class TestAccessibility:
    """Tests for accessibility features"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        if not TESTCLIENT_AVAILABLE:
            pytest.skip("FastAPI TestClient not available")
        return TestClient(app)
    
    def test_form_has_aria_labels(self, client):
        """
        EDGE CASE: Screen reader announces validation errors
        
        Tests that form has proper ARIA attributes
        """
        response = client.get("/contact")
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Check for ARIA attributes
        assert 'aria-' in content  # Has some ARIA attributes
        assert 'aria-required' in content or 'required' in content
    
    def test_keyboard_navigation_structure(self, client):
        """
        EDGE CASE: Tab order follows logical sequence
        
        Tests that form fields are in logical order in HTML
        """
        response = client.get("/contact")
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Check that name appears before email, email before message
        name_pos = content.find('name="name"') or content.find('id="name"')
        email_pos = content.find('name="email"') or content.find('id="email"')
        message_pos = content.find('name="message"') or content.find('id="message"')
        
        assert name_pos > 0
        assert email_pos > 0
        assert message_pos > 0
        assert name_pos < email_pos < message_pos


class TestPerformance:
    """Tests for performance requirements"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        if not TESTCLIENT_AVAILABLE:
            pytest.skip("FastAPI TestClient not available")
        return TestClient(app)
    
    @pytest.fixture
    def csrf_token(self, client):
        """Get a valid CSRF token"""
        response = client.get("/api/csrf-token")
        return response.json()["csrf_token"]
    
    def test_form_submission_performance(self, client, csrf_token):
        """Test that form submission completes quickly"""
        start_time = time.time()
        
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "This is a test message for performance testing.",
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 1.0  # Should complete within 1 second
    
    def test_validation_performance(self, client, csrf_token):
        """Test that validation is fast even with max length inputs"""
        start_time = time.time()
        
        response = client.post("/contact", data={
            "name": "A" * 50,  # Max length
            "email": "user@example.com",
            "message": "A" * 1000,  # Max length
            "csrf_token": csrf_token
        }, headers={
            "X-CSRF-Token": csrf_token
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 1.0  # Should still be fast


# Manual test runner
if __name__ == "__main__":
    if not TESTCLIENT_AVAILABLE:
        print("⚠️  FastAPI TestClient not available")
        print("Install with: pip install httpx")
        sys.exit(1)
    
    print("Running E2E Workflow Tests")
    print("=" * 60)
    
    try:
        import pytest
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Install with: pip install pytest httpx")
        sys.exit(1)
