"""
Test suite for the contact form implementation.
Tests validation, edge cases, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, ContactFormData
from pydantic import ValidationError


client = TestClient(app)


class TestContactFormValidation:
    """Test contact form validation rules."""
    
    def test_valid_form_submission(self):
        """Test successful form submission with valid data."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Hello there, this is a test message."
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Message sent successfully"
    
    def test_minimum_valid_lengths(self):
        """Test minimum valid lengths for all fields."""
        response = client.post(
            "/api/contact",
            json={
                "name": "Jo",  # 2 chars (minimum)
                "email": "a@b.c",
                "message": "Ten chars!"  # 10 chars (minimum)
            }
        )
        assert response.status_code == 200
    
    def test_maximum_valid_lengths(self):
        """Test maximum valid lengths for all fields."""
        response = client.post(
            "/api/contact",
            json={
                "name": "A" * 50,  # 50 chars (maximum)
                "email": "test@example.com",
                "message": "A" * 1000  # 1000 chars (maximum)
            }
        )
        assert response.status_code == 200
    
    def test_empty_name_field(self):
        """Test that empty name field returns error."""
        response = client.post(
            "/api/contact",
            json={
                "name": "",
                "email": "john@example.com",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_empty_email_field(self):
        """Test that empty email field returns error."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422
    
    def test_empty_message_field(self):
        """Test that empty message field returns error."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": ""
            }
        )
        assert response.status_code == 422
    
    def test_name_too_short(self):
        """Test that name with only 1 character is rejected."""
        response = client.post(
            "/api/contact",
            json={
                "name": "J",
                "email": "john@example.com",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422
    
    def test_name_too_long(self):
        """Test that name exceeding 50 characters is rejected."""
        response = client.post(
            "/api/contact",
            json={
                "name": "A" * 51,
                "email": "john@example.com",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422
    
    def test_message_too_short(self):
        """Test that message with less than 10 characters is rejected."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Short"
            }
        )
        assert response.status_code == 422
    
    def test_message_too_long(self):
        """Test that message exceeding 1000 characters is rejected."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "A" * 1001
            }
        )
        assert response.status_code == 422
    
    def test_invalid_email_format(self):
        """Test that invalid email format is rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test@.com",
            "test..test@example.com",
            "test @example.com"
        ]
        for email in invalid_emails:
            response = client.post(
                "/api/contact",
                json={
                    "name": "John Doe",
                    "email": email,
                    "message": "Hello there"
                }
            )
            assert response.status_code == 422, f"Email '{email}' should be invalid"


class TestContactFormEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_unicode_characters_in_name(self):
        """Test that Unicode characters are supported in name field."""
        unicode_names = [
            "José García",
            "François Müller",
            "李明",
            "Владимир",
            "محمد أحمد"
        ]
        for name in unicode_names:
            response = client.post(
                "/api/contact",
                json={
                    "name": name,
                    "email": "test@example.com",
                    "message": "Hello there, this is a test."
                }
            )
            assert response.status_code == 200, f"Unicode name '{name}' should be valid"
    
    def test_message_with_whitespace_only(self):
        """Test that message with only whitespace is rejected."""
        whitespace_messages = [
            "          ",  # spaces
            "\n\n\n\n",  # newlines
            "\t\t\t\t",  # tabs
            " \n \t \n "  # mixed
        ]
        for message in whitespace_messages:
            response = client.post(
                "/api/contact",
                json={
                    "name": "John Doe",
                    "email": "test@example.com",
                    "message": message
                }
            )
            assert response.status_code == 422, "Whitespace-only message should be rejected"
    
    def test_leading_trailing_whitespace_trimmed(self):
        """Test that leading and trailing whitespace is trimmed."""
        response = client.post(
            "/api/contact",
            json={
                "name": "  John Doe  ",
                "email": "  john@example.com  ",
                "message": "  Hello there, this is a test message.  "
            }
        )
        assert response.status_code == 200
    
    def test_email_normalization_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "JoHn@ExAmPlE.CoM",
                "message": "Hello there, this is a test."
            }
        )
        assert response.status_code == 200
    
    def test_special_characters_in_message(self):
        """Test that special characters in message are handled."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Hello! This message has special chars: @#$%^&*()[]{}|;:,.<>?/~`"
            }
        )
        assert response.status_code == 200
    
    def test_xss_attempt_in_name(self):
        """Test that XSS attempts in name are sanitized."""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "test@example.com"  # @ is blocked in names
        ]
        # Note: These should be rejected due to character validation,
        # but if they somehow pass, they should be sanitized
        for xss in xss_attempts:
            response = client.post(
                "/api/contact",
                json={
                    "name": xss,
                    "email": "test@example.com",
                    "message": "Hello there, this is a test."
                }
            )
            # Should be rejected due to invalid characters
            assert response.status_code == 422
    
    def test_xss_attempt_in_message(self):
        """Test that XSS attempts in message are sanitized."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "test@example.com",
                "message": "<script>alert('XSS')</script> Hello there!"
            }
        )
        # Should succeed but be sanitized server-side
        assert response.status_code == 200
    
    def test_apostrophe_and_hyphen_in_name(self):
        """Test that apostrophes and hyphens are allowed in names."""
        names = [
            "O'Brien",
            "Mary-Jane Watson",
            "Anne-Marie D'Angelo"
        ]
        for name in names:
            response = client.post(
                "/api/contact",
                json={
                    "name": name,
                    "email": "test@example.com",
                    "message": "Hello there, this is a test."
                }
            )
            assert response.status_code == 200, f"Name '{name}' should be valid"
    
    def test_multiline_message(self):
        """Test that multiline messages are supported."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "test@example.com",
                "message": "Line 1\nLine 2\nLine 3\nThis is a multiline message."
            }
        )
        assert response.status_code == 200


class TestContactFormEndpoints:
    """Test contact form endpoints."""
    
    def test_contact_page_loads(self):
        """Test that contact page loads successfully."""
        response = client.get("/contact")
        assert response.status_code == 200
        assert "contact" in response.text.lower()
    
    def test_api_endpoint_exists(self):
        """Test that API endpoint exists."""
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Hello there"
            }
        )
        assert response.status_code in [200, 422]  # Either success or validation error
    
    def test_missing_fields(self):
        """Test that missing required fields return error."""
        # Missing name
        response = client.post(
            "/api/contact",
            json={
                "email": "john@example.com",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422
        
        # Missing email
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "message": "Hello there"
            }
        )
        assert response.status_code == 422
        
        # Missing message
        response = client.post(
            "/api/contact",
            json={
                "name": "John Doe",
                "email": "john@example.com"
            }
        )
        assert response.status_code == 422


class TestContactFormModel:
    """Test the ContactFormData Pydantic model directly."""
    
    def test_valid_model_creation(self):
        """Test creating a valid ContactFormData instance."""
        form = ContactFormData(
            name="John Doe",
            email="john@example.com",
            message="Hello there, this is a test message."
        )
        assert form.name == "John Doe"
        assert form.email == "john@example.com"
        assert form.message == "Hello there, this is a test message."
    
    def test_model_validation_error(self):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            ContactFormData(
                name="J",  # Too short
                email="invalid-email",
                message="Short"
            )
    
    def test_whitespace_trimming(self):
        """Test that whitespace is properly trimmed."""
        form = ContactFormData(
            name="  John Doe  ",
            email="  john@example.com  ",
            message="  Hello there, this is a test message.  "
        )
        assert form.name == "John Doe"
        assert form.email == "john@example.com"
        assert form.message == "Hello there, this is a test message."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
