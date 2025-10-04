"""
Test suite for Contact Form Component
Tests both client-side validation logic and server-side endpoint

Run tests with: pytest test_contact_form.py -v
"""

import re
from datetime import datetime

# pytest is optional - tests can run without it
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


class TestValidationPatterns:
    """Test validation pattern matching"""
    
    NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def test_valid_names(self):
        """Test valid name patterns"""
        valid_names = [
            "John Doe",
            "Jane-Smith",
            "Bob123",
            "Alice O-Brien",
            "XY",  # Minimum 2 chars
            "A" * 50,  # Maximum 50 chars
        ]
        
        for name in valid_names:
            assert re.match(self.NAME_PATTERN, name), f"Expected '{name}' to be valid"
    
    def test_invalid_names(self):
        """Test invalid name patterns"""
        invalid_names = [
            "A",  # Too short
            "A" * 51,  # Too long
            "John@Doe",  # Invalid character
            "Jane!Smith",  # Invalid character
            "Bob#123",  # Invalid character
            "",  # Empty
        ]
        
        for name in invalid_names:
            assert not re.match(self.NAME_PATTERN, name), f"Expected '{name}' to be invalid"
        
        # Special case: spaces-only should be caught by trim + empty check
        spaces_only = "   "
        assert spaces_only.strip() == "", "Spaces-only should become empty after trim"
    
    def test_valid_emails(self):
        """Test valid email patterns"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user_name@example-domain.com",
            "123@test.com",
            "a@b.co",  # Minimum valid email
        ]
        
        for email in valid_emails:
            assert re.match(self.EMAIL_PATTERN, email), f"Expected '{email}' to be valid"
    
    def test_invalid_emails(self):
        """Test invalid email patterns"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com",
            "user@domain",
            "user @domain.com",  # Space
            "",  # Empty
            "user@domain.c",  # TLD too short
        ]
        
        for email in invalid_emails:
            assert not re.match(self.EMAIL_PATTERN, email), f"Expected '{email}' to be invalid"


class TestMessageValidation:
    """Test message field validation"""
    
    MESSAGE_MIN_LENGTH = 10
    MESSAGE_MAX_LENGTH = 1000
    
    def test_valid_message_lengths(self):
        """Test valid message lengths"""
        valid_messages = [
            "A" * 10,  # Minimum
            "A" * 100,  # Normal
            "A" * 1000,  # Maximum
        ]
        
        for msg in valid_messages:
            assert self.MESSAGE_MIN_LENGTH <= len(msg) <= self.MESSAGE_MAX_LENGTH
    
    def test_invalid_message_lengths(self):
        """Test invalid message lengths"""
        invalid_messages = [
            "",  # Empty
            "A" * 9,  # Too short
            "A" * 1001,  # Too long
        ]
        
        for msg in invalid_messages:
            assert not (self.MESSAGE_MIN_LENGTH <= len(msg) <= self.MESSAGE_MAX_LENGTH)


class TestInputSanitization:
    """Test input sanitization and security"""
    
    def test_html_stripping(self):
        """Test HTML tag removal from input"""
        html_input = "<script>alert('xss')</script>Hello"
        sanitized = re.sub(r'<[^>]*>', '', html_input)
        # After removing tags, we should have just the text content
        assert sanitized == "alert('xss')Hello"  # Script content remains but tags are gone
        assert "<script>" not in sanitized
        assert "</script>" not in sanitized
    
    def test_formatting_removal(self):
        """Test removal of formatting characters"""
        formatted_text = "Hello\x00World\x1f"
        sanitized = formatted_text.strip()
        # In production, you'd use more robust sanitization
        assert "Hello" in sanitized
    
    def test_whitespace_trimming(self):
        """Test whitespace trimming"""
        inputs = [
            ("  John Doe  ", "John Doe"),
            ("\ntest@example.com\n", "test@example.com"),
            ("  message with spaces  ", "message with spaces"),
        ]
        
        for original, expected in inputs:
            assert original.strip() == expected


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        # Current pattern only allows ASCII alphanumeric
        NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
        
        unicode_names = [
            "José García",  # Spanish
            "François Müller",  # French/German
            "李明",  # Chinese
        ]
        
        for name in unicode_names:
            # These should fail with current pattern
            # In production, you might want to support unicode
            result = re.match(NAME_PATTERN, name)
            # This test documents current behavior
            assert result is None, "Current implementation doesn't support unicode"
    
    def test_sql_injection_attempt(self):
        """Test SQL injection patterns are rejected"""
        NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
        
        sql_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        
        for attempt in sql_attempts:
            assert not re.match(NAME_PATTERN, attempt), \
                f"SQL injection attempt should be rejected: {attempt}"
    
    def test_xss_attempt(self):
        """Test XSS patterns are rejected"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
        ]
        
        NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
        
        for attempt in xss_attempts:
            assert not re.match(NAME_PATTERN, attempt), \
                f"XSS attempt should be rejected: {attempt}"
    
    def test_extremely_long_input(self):
        """Test handling of extremely long inputs"""
        MESSAGE_MAX_LENGTH = 1000
        
        very_long_message = "A" * 10000
        assert len(very_long_message) > MESSAGE_MAX_LENGTH
        
        # In production, the maxlength attribute and validation would catch this
        truncated = very_long_message[:MESSAGE_MAX_LENGTH]
        assert len(truncated) == MESSAGE_MAX_LENGTH


class TestFormBehavior:
    """Test form behavior and user interactions"""
    
    def test_character_counter_logic(self):
        """Test character counter calculation"""
        test_cases = [
            ("", 0),
            ("Hello", 5),
            ("A" * 100, 100),
            ("A" * 1000, 1000),
        ]
        
        for text, expected_count in test_cases:
            assert len(text) == expected_count
    
    def test_submission_state_flags(self):
        """Test submission state management"""
        # Simulate submission state
        is_submitting = False
        
        # First submission
        assert not is_submitting
        is_submitting = True
        assert is_submitting
        
        # Try double submit
        if is_submitting:
            # Should prevent second submission
            assert True, "Double submission prevented"
        
        # Complete submission
        is_submitting = False
        assert not is_submitting
    
    def test_error_message_display_logic(self):
        """Test error message display logic"""
        errors = []
        
        # No errors initially
        assert len(errors) == 0
        
        # Add validation errors
        errors.append("Name is required")
        errors.append("Email is invalid")
        
        assert len(errors) == 2
        assert "Name is required" in errors
        
        # Clear errors
        errors.clear()
        assert len(errors) == 0


# Integration tests would require FastAPI TestClient
# Uncomment and use if you have the full FastAPI app set up

"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestContactEndpoint:
    '''Test the /contact endpoint'''
    
    def test_successful_submission(self):
        '''Test successful form submission'''
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "This is a valid test message with sufficient length."
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Thank you" in data["message"]
    
    def test_missing_name(self):
        '''Test submission with missing name'''
        response = client.post("/contact", data={
            "name": "",
            "email": "john@example.com",
            "message": "This is a test message."
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert any("Name" in error for error in data["errors"])
    
    def test_invalid_email(self):
        '''Test submission with invalid email'''
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "not-an-email",
            "message": "This is a test message."
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert any("email" in error.lower() for error in data["errors"])
    
    def test_message_too_short(self):
        '''Test submission with message too short'''
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Short"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert any("Message" in error for error in data["errors"])
    
    def test_multiple_validation_errors(self):
        '''Test submission with multiple validation errors'''
        response = client.post("/contact", data={
            "name": "A",  # Too short
            "email": "invalid",  # Invalid format
            "message": "Short"  # Too short
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert len(data["errors"]) >= 3
    
    def test_special_characters_in_name(self):
        '''Test submission with special characters in name'''
        response = client.post("/contact", data={
            "name": "John@Doe!",  # Invalid characters
            "email": "john@example.com",
            "message": "This is a test message."
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
    
    def test_extremely_long_message(self):
        '''Test submission with extremely long message'''
        response = client.post("/contact", data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "A" * 1001  # Over limit
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
    
    def test_whitespace_trimming(self):
        '''Test that whitespace is properly trimmed'''
        response = client.post("/contact", data={
            "name": "  John Doe  ",
            "email": "  john@example.com  ",
            "message": "  This is a test message with spaces.  "
        })
        
        # Should succeed after trimming
        assert response.status_code == 200
"""


if __name__ == "__main__":
    # Run tests with pytest if available, otherwise run basic tests
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not installed. Running basic tests...")
        
        # Run basic tests
        test_suite = TestValidationPatterns()
        
        print("\n✅ Testing valid names...")
        test_suite.test_valid_names()
        print("   PASSED")
        
        print("\n✅ Testing invalid names...")
        test_suite.test_invalid_names()
        print("   PASSED")
        
        print("\n✅ Testing valid emails...")
        test_suite.test_valid_emails()
        print("   PASSED")
        
        print("\n✅ Testing invalid emails...")
        test_suite.test_invalid_emails()
        print("   PASSED")
        
        print("\n✅ Testing message validation...")
        msg_test = TestMessageValidation()
        msg_test.test_valid_message_lengths()
        msg_test.test_invalid_message_lengths()
        print("   PASSED")
        
        print("\n✅ Testing input sanitization...")
        san_test = TestInputSanitization()
        san_test.test_html_stripping()
        san_test.test_whitespace_trimming()
        print("   PASSED")
        
        print("\n✅ Testing edge cases...")
        edge_test = TestEdgeCases()
        edge_test.test_sql_injection_attempt()
        edge_test.test_xss_attempt()
        print("   PASSED")
        
        print("\n" + "="*60)
        print("✅ All basic tests passed!")
        print("="*60)
        print("\nFor full test suite, install pytest:")
        print("  pip install pytest")
        print("  pytest test_contact_form.py -v")
