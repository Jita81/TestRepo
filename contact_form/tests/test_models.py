"""
Unit tests for contact form data models.

Tests validation logic for ContactFormRequest, ContactFormResponse,
and ErrorResponse models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from ..models import ContactFormRequest, ContactFormResponse, ErrorResponse


class TestContactFormRequest:
    """Test suite for ContactFormRequest model validation."""
    
    def test_valid_contact_form(self):
        """Test that valid data creates a ContactFormRequest successfully."""
        data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "message": "This is a valid message with sufficient length."
        }
        form = ContactFormRequest(**data)
        
        assert form.name == "John Doe"
        assert form.email == "john.doe@example.com"
        assert form.message == "This is a valid message with sufficient length."
    
    def test_name_too_short(self):
        """Test that names shorter than 2 characters are rejected."""
        data = {
            "name": "A",
            "email": "test@example.com",
            "message": "Valid message here"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContactFormRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
    
    def test_name_too_long(self):
        """Test that names longer than 100 characters are rejected."""
        data = {
            "name": "A" * 101,
            "email": "test@example.com",
            "message": "Valid message here"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContactFormRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
    
    def test_name_invalid_characters(self):
        """Test that names with invalid characters are rejected."""
        invalid_names = [
            "John123",
            "John@Doe",
            "John_Doe",
            "John.Doe",
            "John&Doe"
        ]
        
        for invalid_name in invalid_names:
            data = {
                "name": invalid_name,
                "email": "test@example.com",
                "message": "Valid message here"
            }
            
            with pytest.raises(ValidationError) as exc_info:
                ContactFormRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(
                error['loc'] == ('name',) and 
                'must contain only letters' in error['msg'].lower()
                for error in errors
            ), f"Expected validation error for name: {invalid_name}"
    
    def test_name_valid_special_characters(self):
        """Test that names with valid special characters are accepted."""
        valid_names = [
            "Mary-Jane Watson",
            "O'Brien",
            "Jean-Pierre O'Connor",
            "Mary Jane"
        ]
        
        for valid_name in valid_names:
            data = {
                "name": valid_name,
                "email": "test@example.com",
                "message": "Valid message here"
            }
            form = ContactFormRequest(**data)
            assert form.name == valid_name
    
    def test_name_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed from name."""
        data = {
            "name": "  John Doe  ",
            "email": "test@example.com",
            "message": "Valid message here"
        }
        form = ContactFormRequest(**data)
        assert form.name == "John Doe"
    
    def test_invalid_email_format(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "double@@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            data = {
                "name": "John Doe",
                "email": invalid_email,
                "message": "Valid message here"
            }
            
            with pytest.raises(ValidationError) as exc_info:
                ContactFormRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error['loc'] == ('email',) for error in errors), \
                f"Expected validation error for email: {invalid_email}"
    
    def test_valid_email_formats(self):
        """Test that various valid email formats are accepted."""
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "123@numbers.com"
        ]
        
        for valid_email in valid_emails:
            data = {
                "name": "John Doe",
                "email": valid_email,
                "message": "Valid message here"
            }
            form = ContactFormRequest(**data)
            assert form.email == valid_email
    
    def test_message_too_short(self):
        """Test that messages shorter than 10 characters are rejected."""
        data = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "Too short"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContactFormRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('message',) for error in errors)
    
    def test_message_too_long(self):
        """Test that messages longer than 2000 characters are rejected."""
        data = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "A" * 2001
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContactFormRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('message',) for error in errors)
    
    def test_message_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed from message."""
        data = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "   Valid message with whitespace   "
        }
        form = ContactFormRequest(**data)
        assert form.message == "Valid message with whitespace"
    
    def test_message_whitespace_only_rejected(self):
        """Test that messages with only whitespace are rejected."""
        data = {
            "name": "John Doe",
            "email": "test@example.com",
            "message": "          "  # Only spaces
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContactFormRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(
            error['loc'] == ('message',) and 
            'at least 10 characters' in error['msg'].lower()
            for error in errors
        )
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        # Missing name
        with pytest.raises(ValidationError):
            ContactFormRequest(
                email="test@example.com",
                message="Valid message here"
            )
        
        # Missing email
        with pytest.raises(ValidationError):
            ContactFormRequest(
                name="John Doe",
                message="Valid message here"
            )
        
        # Missing message
        with pytest.raises(ValidationError):
            ContactFormRequest(
                name="John Doe",
                email="test@example.com"
            )


class TestContactFormResponse:
    """Test suite for ContactFormResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid ContactFormResponse."""
        response = ContactFormResponse(
            submission_id="abc123",
            timestamp=datetime.now()
        )
        
        assert response.success is True
        assert "received" in response.message.lower()
        assert response.submission_id == "abc123"
        assert isinstance(response.timestamp, datetime)
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        response = ContactFormResponse(
            submission_id="test123",
            timestamp=datetime.now()
        )
        
        assert response.success is True
        assert len(response.message) > 0


class TestErrorResponse:
    """Test suite for ErrorResponse model."""
    
    def test_basic_error_response(self):
        """Test creating a basic ErrorResponse."""
        error = ErrorResponse(
            message="Something went wrong"
        )
        
        assert error.success is False
        assert error.message == "Something went wrong"
        assert error.errors is None
        assert error.error_code is None
    
    def test_detailed_error_response(self):
        """Test creating an ErrorResponse with detailed errors."""
        error = ErrorResponse(
            message="Validation failed",
            errors={"email": ["Invalid email format"]},
            error_code="VALIDATION_ERROR"
        )
        
        assert error.success is False
        assert error.message == "Validation failed"
        assert error.errors == {"email": ["Invalid email format"]}
        assert error.error_code == "VALIDATION_ERROR"