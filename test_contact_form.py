"""
Test script for contact form validation logic.
This script tests the validation rules without requiring pytest.
"""

import re
import html

def sanitize_and_validate_contact_form(name: str, email: str, message: str):
    """
    Validates contact form inputs following the same logic as the server endpoint.
    
    Returns:
        tuple: (is_valid: bool, errors: list, sanitized_data: dict)
    """
    # Sanitize inputs to prevent XSS attacks
    name = html.escape(name.strip())
    email = html.escape(email.strip())
    message = html.escape(message.strip())
    
    # Validation rules
    errors = []
    
    # Validate name (2-50 characters)
    if not name:
        errors.append("Name is required")
    elif len(name) < 2:
        errors.append("Name must be at least 2 characters")
    elif len(name) > 50:
        errors.append("Name must not exceed 50 characters")
    
    # Validate email format using RFC 5322 simplified regex
    email_pattern = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    if not email:
        errors.append("Email is required")
    elif not email_pattern.match(email):
        errors.append("Please enter a valid email address")
    
    # Validate message (10-500 characters)
    if not message:
        errors.append("Message is required")
    elif len(message) < 10:
        errors.append("Message must be at least 10 characters")
    elif len(message) > 500:
        errors.append("Message must not exceed 500 characters")
    
    is_valid = len(errors) == 0
    sanitized_data = {
        "name": name,
        "email": email,
        "message": message
    }
    
    return is_valid, errors, sanitized_data

def run_tests():
    """Run comprehensive tests for contact form validation."""
    print("=" * 60)
    print("CONTACT FORM VALIDATION TESTS")
    print("=" * 60)
    
    test_cases = [
        # Valid submissions
        {
            "name": "Valid: John Doe with proper email",
            "input": ("John Doe", "test@example.com", "This is a valid message with more than 10 chars"),
            "expected_valid": True
        },
        {
            "name": "Valid: Minimum length name and message",
            "input": ("Jo", "user@domain.com", "Ten chars!"),
            "expected_valid": True
        },
        {
            "name": "Valid: Maximum length name (50 chars)",
            "input": ("A" * 50, "user@test.com", "Valid message here"),
            "expected_valid": True
        },
        {
            "name": "Valid: Maximum length message (500 chars)",
            "input": ("John Doe", "test@example.com", "A" * 500),
            "expected_valid": True
        },
        
        # Invalid: Empty fields
        {
            "name": "Invalid: Empty name",
            "input": ("", "test@example.com", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Name is required"
        },
        {
            "name": "Invalid: Empty email",
            "input": ("John Doe", "", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Email is required"
        },
        {
            "name": "Invalid: Empty message",
            "input": ("John Doe", "test@example.com", ""),
            "expected_valid": False,
            "expected_error": "Message is required"
        },
        
        # Invalid: Name validation
        {
            "name": "Invalid: Name too short (1 char)",
            "input": ("J", "test@example.com", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Name must be at least 2 characters"
        },
        {
            "name": "Invalid: Name too long (>50 chars)",
            "input": ("A" * 51, "test@example.com", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Name must not exceed 50 characters"
        },
        
        # Invalid: Email validation
        {
            "name": "Invalid: Email without @",
            "input": ("John Doe", "invalidemail", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Please enter a valid email address"
        },
        {
            "name": "Invalid: Email without domain",
            "input": ("John Doe", "invalid@", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Please enter a valid email address"
        },
        {
            "name": "Invalid: Email with incomplete domain",
            "input": ("John Doe", "invalid@email", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Please enter a valid email address"
        },
        
        # Invalid: Message validation
        {
            "name": "Invalid: Message too short (<10 chars)",
            "input": ("John Doe", "test@example.com", "Short"),
            "expected_valid": False,
            "expected_error": "Message must be at least 10 characters"
        },
        {
            "name": "Invalid: Message too long (>500 chars)",
            "input": ("John Doe", "test@example.com", "A" * 501),
            "expected_valid": False,
            "expected_error": "Message must not exceed 500 characters"
        },
        
        # Special characters and sanitization
        {
            "name": "Valid: Special characters are sanitized",
            "input": ("John <script>alert('xss')</script>", "test@example.com", "Message with <b>HTML</b> tags"),
            "expected_valid": True
        },
        
        # Whitespace handling
        {
            "name": "Valid: Whitespace is trimmed",
            "input": ("  John Doe  ", "  test@example.com  ", "  Valid message here  "),
            "expected_valid": True
        },
        {
            "name": "Invalid: Only whitespace in name",
            "input": ("   ", "test@example.com", "Valid message here"),
            "expected_valid": False,
            "expected_error": "Name is required"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 60)
        
        is_valid, errors, sanitized = sanitize_and_validate_contact_form(*test['input'])
        
        # Check if validation result matches expectation
        if is_valid == test['expected_valid']:
            # If we expect it to be invalid, check if expected error is present
            if not test['expected_valid'] and 'expected_error' in test:
                if any(test['expected_error'] in error for error in errors):
                    print(f"✅ PASSED")
                    print(f"   Expected error found: {test['expected_error']}")
                    passed += 1
                else:
                    print(f"❌ FAILED")
                    print(f"   Expected error: {test['expected_error']}")
                    print(f"   Actual errors: {errors}")
                    failed += 1
            else:
                print(f"✅ PASSED")
                if is_valid:
                    print(f"   Sanitized data: {sanitized}")
                else:
                    print(f"   Errors: {errors}")
                passed += 1
        else:
            print(f"❌ FAILED")
            print(f"   Expected valid: {test['expected_valid']}")
            print(f"   Actual valid: {is_valid}")
            print(f"   Errors: {errors}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
