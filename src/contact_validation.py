"""
Input validation and sanitization for contact form.
Implements comprehensive validation rules and security measures.
"""

import re
from typing import Dict, List, Optional
from html import escape


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(str(errors))


class ContactValidator:
    """Validates and sanitizes contact form inputs."""
    
    # Email regex pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@'
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    # Name pattern - allows letters, spaces, hyphens, apostrophes, and Unicode letters
    NAME_PATTERN = re.compile(r"^[\w\s'\-\.]+$", re.UNICODE)
    
    # Maximum lengths
    MAX_NAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 254
    
    @staticmethod
    def sanitize_input(value: str, max_length: Optional[int] = None, escape_html: bool = True) -> str:
        """
        Sanitize input by trimming whitespace and optionally escaping HTML.
        
        Args:
            value: Input string to sanitize
            max_length: Optional maximum length to truncate to
            escape_html: Whether to escape HTML characters (default True)
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        # Trim whitespace
        sanitized = value.strip()
        
        # Escape HTML special characters to prevent XSS (only < and > are dangerous)
        if escape_html:
            # Only escape < and > which are the dangerous characters for XSS
            # Keep apostrophes and quotes as-is since they're validated by patterns
            sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;")
        
        # Truncate if max_length specified
        if max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @classmethod
    def validate_full_name(cls, name: str) -> tuple[bool, Optional[str]]:
        """
        Validate full name field.
        
        Args:
            name: Name to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Full name is required"
        
        if len(name) > cls.MAX_NAME_LENGTH:
            return False, f"Name must be less than {cls.MAX_NAME_LENGTH} characters"
        
        if len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        # Check for valid characters
        if not cls.NAME_PATTERN.match(name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for suspicious patterns (numbers in name might be suspicious)
        if re.search(r'\d{3,}', name):
            return False, "Name contains invalid character sequences"
        
        return True, None
    
    @classmethod
    def validate_email(cls, email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email address.
        
        Args:
            email: Email address to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email address is required"
        
        if len(email) > cls.MAX_EMAIL_LENGTH:
            return False, f"Email must be less than {cls.MAX_EMAIL_LENGTH} characters"
        
        # Check email format
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        # Additional checks
        if email.count('@') != 1:
            return False, "Invalid email format"
        
        local_part, domain = email.split('@')
        
        # Check local part length
        if len(local_part) > 64:
            return False, "Email local part is too long"
        
        # Check domain has at least one dot and valid TLD
        if '.' not in domain:
            return False, "Invalid email domain"
        
        # Check for consecutive dots
        if '..' in email:
            return False, "Invalid email format"
        
        return True, None
    
    @classmethod
    def validate_contact_form(
        cls,
        full_name: str,
        email: str
    ) -> Dict[str, str]:
        """
        Validate entire contact form.
        
        Args:
            full_name: Full name input
            email: Email input
        
        Returns:
            Dictionary of field errors (empty if valid)
        
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Sanitize inputs first
        full_name = cls.sanitize_input(full_name, cls.MAX_NAME_LENGTH)
        email = cls.sanitize_input(email, cls.MAX_EMAIL_LENGTH)
        
        # Validate name
        name_valid, name_error = cls.validate_full_name(full_name)
        if not name_valid:
            errors['fullName'] = name_error
        
        # Validate email
        email_valid, email_error = cls.validate_email(email)
        if not email_valid:
            errors['email'] = email_error
        
        if errors:
            raise ValidationError(errors)
        
        return {
            'fullName': full_name,
            'email': email.lower()  # Normalize email to lowercase
        }


# Global validator instance
validator = ContactValidator()