"""
Comprehensive tests for the contact form functionality.
Tests validation, security, rate limiting, and database operations.
"""

import pytest
from fastapi.testclient import TestClient
import sqlite3
import os
from pathlib import Path
import time

# Import the main app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from src.database import Database, db
from src.contact_validation import ContactValidator, ValidationError
from src.contact_routes import generate_csrf_token, validate_csrf_token


class TestContactValidation:
    """Test contact form validation logic."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = ContactValidator()
    
    def test_validate_full_name_valid(self):
        """Test valid full name validation."""
        valid_names = [
            "John Doe",
            "Mary-Jane Smith",
            "O'Connor",
            "José García",
            "Anne-Marie St. Pierre"
        ]
        
        for name in valid_names:
            is_valid, error = self.validator.validate_full_name(name)
            assert is_valid, f"Expected {name} to be valid, got error: {error}"
            assert error is None
    
    def test_validate_full_name_invalid(self):
        """Test invalid full name validation."""
        invalid_names = [
            ("", "Full name is required"),
            ("J", "Name must be at least 2 characters long"),
            ("a" * 101, "Name must be less than 100 characters"),
            ("John123456", "Name contains invalid character sequences"),
            ("<script>alert('xss')</script>", "Name can only contain letters"),
        ]
        
        for name, expected_error_type in invalid_names:
            is_valid, error = self.validator.validate_full_name(name)
            assert not is_valid, f"Expected {name} to be invalid"
            assert error is not None
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user+label@domain.co.uk",
            "first.last@sub.domain.com",
            "a@b.c",
            "test_email@example-domain.com"
        ]
        
        for email in valid_emails:
            is_valid, error = self.validator.validate_email(email)
            assert is_valid, f"Expected {email} to be valid, got error: {error}"
            assert error is None
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "test@",
            "test..double@example.com",
            "test@domain",
            "a" * 255 + "@example.com",
            "test@" + "a" * 250 + ".com"
        ]
        
        for email in invalid_emails:
            is_valid, error = self.validator.validate_email(email)
            assert not is_valid, f"Expected {email} to be invalid"
            assert error is not None
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test basic trimming
        assert self.validator.sanitize_input("  test  ") == "test"
        assert self.validator.sanitize_input("Normal text") == "Normal text"
        assert self.validator.sanitize_input("  spaces  everywhere  ") == "spaces  everywhere"
        
        # Test HTML escaping (apostrophes may be escaped as &#x27; or &apos;)
        result = self.validator.sanitize_input("<script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        assert "alert" in result
    
    def test_validate_contact_form_success(self):
        """Test successful form validation."""
        result = self.validator.validate_contact_form(
            "John Doe",
            "john@example.com"
        )
        
        assert result['fullName'] == "John Doe"
        assert result['email'] == "john@example.com"
    
    def test_validate_contact_form_failure(self):
        """Test form validation with errors."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_contact_form("", "invalid-email")
        
        errors = exc_info.value.errors
        assert 'fullName' in errors
        assert 'email' in errors
    
    def test_email_normalization(self):
        """Test that emails are normalized to lowercase."""
        result = self.validator.validate_contact_form(
            "John Doe",
            "John@EXAMPLE.COM"
        )
        
        assert result['email'] == "john@example.com"


class TestDatabase:
    """Test database operations."""
    
    def setup_method(self):
        """Setup test database."""
        # Use a test database
        self.test_db_path = Path("test_contacts.db")
        
        # Clean up if exists
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        
        Database._db_path = self.test_db_path
        Database._local = type('obj', (object,), {})()  # Reset local storage
        self.db = Database()
    
    def teardown_method(self):
        """Clean up test database."""
        if self.test_db_path.exists():
            # Close all connections
            if hasattr(Database._local, 'connection'):
                Database._local.connection.close()
                delattr(Database._local, 'connection')
            
            # Remove test database
            try:
                self.test_db_path.unlink()
            except:
                pass
    
    def test_insert_contact(self):
        """Test inserting a contact."""
        contact_id = self.db.insert_contact(
            full_name="Test User",
            email="test@example.com",
            ip_address="127.0.0.1",
            user_agent="Test Agent"
        )
        
        assert contact_id > 0
    
    def test_get_contacts(self):
        """Test retrieving contacts."""
        # Insert test contacts
        self.db.insert_contact("User 1", "user1@example.com")
        self.db.insert_contact("User 2", "user2@example.com")
        
        contacts = self.db.get_contacts(limit=10)
        
        assert len(contacts) == 2
        assert contacts[0]['full_name'] == "User 2"  # Most recent first
        assert contacts[1]['full_name'] == "User 1"
    
    def test_get_contacts_pagination(self):
        """Test contact pagination."""
        # Insert multiple contacts
        for i in range(5):
            self.db.insert_contact(f"User {i}", f"user{i}@example.com")
        
        # Get first page
        page1 = self.db.get_contacts(limit=2, offset=0)
        assert len(page1) == 2
        
        # Get second page
        page2 = self.db.get_contacts(limit=2, offset=2)
        assert len(page2) == 2
        
        # Ensure different contacts
        assert page1[0]['id'] != page2[0]['id']
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        ip = "192.168.1.1"
        
        # First 5 requests should be allowed
        for i in range(5):
            allowed, remaining = self.db.check_rate_limit(ip, max_requests=5)
            assert allowed, f"Request {i+1} should be allowed"
            assert remaining == 5 - i - 1
        
        # 6th request should be blocked
        allowed, remaining = self.db.check_rate_limit(ip, max_requests=5)
        assert not allowed, "6th request should be blocked"
        assert remaining == 0
    
    def test_rate_limiting_window_reset(self):
        """Test that rate limiting resets after time window."""
        ip = "192.168.1.2"
        
        # Make max requests
        for _ in range(5):
            self.db.check_rate_limit(ip, max_requests=5, window_minutes=0.01)
        
        # Wait for window to expire
        time.sleep(1)
        
        # Should be allowed again
        allowed, remaining = self.db.check_rate_limit(ip, max_requests=5, window_minutes=0.01)
        assert allowed, "Request should be allowed after window reset"
    
    def test_rate_limiting_per_ip(self):
        """Test that rate limiting is per IP address."""
        ip1 = "192.168.1.10"
        ip2 = "192.168.1.20"
        
        # Use up limit for IP1
        for _ in range(5):
            self.db.check_rate_limit(ip1, max_requests=5)
        
        # IP1 should be blocked
        allowed1, _ = self.db.check_rate_limit(ip1, max_requests=5)
        assert not allowed1
        
        # IP2 should still be allowed
        allowed2, _ = self.db.check_rate_limit(ip2, max_requests=5)
        assert allowed2


class TestContactAPI:
    """Test contact form API endpoints."""
    
    def setup_method(self):
        """Setup test client and database."""
        self.client = TestClient(app)
        
        # Use test database
        self.test_db_path = Path("test_contacts_api.db")
        
        # Clean up if exists
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        
        Database._db_path = self.test_db_path
        Database._local = type('obj', (object,), {})()  # Reset local storage
        
        # Initialize new database
        self.test_db = Database()
    
    def teardown_method(self):
        """Clean up."""
        if self.test_db_path.exists():
            if hasattr(Database._local, 'connection'):
                try:
                    Database._local.connection.close()
                except:
                    pass
                delattr(Database._local, 'connection')
            
            try:
                self.test_db_path.unlink()
            except:
                pass
    
    def test_get_csrf_token(self):
        """Test CSRF token generation."""
        response = self.client.get("/api/csrf-token")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'csrf_token' in data
        assert len(data['csrf_token']) > 0
    
    def test_submit_contact_form_success(self):
        """Test successful form submission."""
        # Get CSRF token
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Submit form
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "Test User",
                "email": "test@example.com",
                "csrf_token": csrf_token
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'message' in data
        assert 'contact_id' in data
    
    def test_submit_contact_form_invalid_csrf(self):
        """Test form submission with invalid CSRF token."""
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "Test User",
                "email": "test@example.com",
                "csrf_token": "invalid_token"
            }
        )
        
        assert response.status_code == 403
    
    def test_submit_contact_form_validation_error(self):
        """Test form submission with validation errors."""
        # Get CSRF token
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Submit with invalid data
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "",
                "email": "invalid-email",
                "csrf_token": csrf_token
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'errors' in data
    
    def test_submit_contact_form_rate_limiting(self):
        """Test rate limiting on form submission."""
        # Get CSRF token
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Make 5 successful requests
        for i in range(5):
            # Get fresh token for each request
            token_response = self.client.get("/api/csrf-token")
            csrf_token = token_response.json()['csrf_token']
            
            response = self.client.post(
                "/api/contact",
                data={
                    "fullName": f"User {i}",
                    "email": f"user{i}@example.com",
                    "csrf_token": csrf_token
                }
            )
            assert response.status_code == 200
        
        # 6th request should be rate limited
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "User 6",
                "email": "user6@example.com",
                "csrf_token": csrf_token
            }
        )
        
        assert response.status_code == 429
    
    def test_get_contacts_endpoint(self):
        """Test getting contacts from API."""
        response = self.client.get("/api/contacts")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'contacts' in data
        assert isinstance(data['contacts'], list)
    
    def test_contact_page_loads(self):
        """Test that contact page loads successfully."""
        response = self.client.get("/contact")
        
        assert response.status_code == 200
        assert b"Contact" in response.content or b"contact" in response.content
    
    def test_special_characters_in_name(self):
        """Test handling of special characters in name."""
        # Get CSRF token
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Submit with special characters
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "José María O'Connor-Smith",
                "email": "jose@example.com",
                "csrf_token": csrf_token
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    def test_xss_attempt_blocked(self):
        """Test that XSS attempts are sanitized."""
        # Get CSRF token
        token_response = self.client.get("/api/csrf-token")
        csrf_token = token_response.json()['csrf_token']
        
        # Attempt XSS in name
        response = self.client.post(
            "/api/contact",
            data={
                "fullName": "<script>alert('xss')</script>",
                "email": "test@example.com",
                "csrf_token": csrf_token
            }
        )
        
        # Should be rejected by validation
        assert response.status_code == 400


class TestSecurityFeatures:
    """Test security features of the contact form."""
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation."""
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        
        assert token1 != token2
        assert len(token1) > 20
        assert validate_csrf_token(token1)
        assert validate_csrf_token(token2)
    
    def test_csrf_token_validation_invalid(self):
        """Test CSRF token validation with invalid token."""
        assert not validate_csrf_token("invalid_token")
        assert not validate_csrf_token("")
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection is prevented."""
        test_db_path = Path("test_sql_injection.db")
        Database._db_path = test_db_path
        db = Database()
        
        try:
            # Attempt SQL injection in name
            malicious_name = "'; DROP TABLE contacts; --"
            
            # Should not raise exception or drop table
            contact_id = db.insert_contact(
                full_name=malicious_name,
                email="test@example.com"
            )
            
            assert contact_id > 0
            
            # Verify table still exists
            contacts = db.get_contacts()
            assert isinstance(contacts, list)
        finally:
            if hasattr(Database._local, 'connection'):
                Database._local.connection.close()
                delattr(Database._local, 'connection')
            if test_db_path.exists():
                test_db_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])