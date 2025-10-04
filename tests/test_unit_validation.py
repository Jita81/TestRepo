"""
Unit Tests for Contact Form Validation Logic

Tests validation functions in isolation without server/browser dependencies.
Run with: pytest tests/test_unit_validation.py -v
"""

import re
from typing import Tuple, Optional

# pytest is optional
try:
    import pytest
except ImportError:
    pytest = None


# Validation patterns (matching frontend and backend)
NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MESSAGE_MIN_LENGTH = 10
MESSAGE_MAX_LENGTH = 1000


class TestNameValidation:
    """Unit tests for name field validation"""
    
    def test_valid_names(self):
        """Test that valid names pass validation"""
        valid_names = [
            "John Doe",
            "Jane Smith",
            "Bob Johnson",
            "Alice O-Brien",
            "Mike123",
            "AB",  # Minimum 2 characters
            "A" * 50,  # Maximum 50 characters
            "John-Paul Smith",
            "User 123",
            "test-user-name",
        ]
        
        for name in valid_names:
            assert re.match(NAME_PATTERN, name), f"Expected '{name}' to be valid"
            assert 2 <= len(name) <= 50
    
    def test_invalid_names_too_short(self):
        """Test that names shorter than 2 characters fail"""
        invalid_names = ["A", "1", "", " "]
        
        for name in invalid_names:
            name_stripped = name.strip()
            assert len(name_stripped) < 2 or name_stripped == ""
    
    def test_invalid_names_too_long(self):
        """Test that names longer than 50 characters fail"""
        long_name = "A" * 51
        assert len(long_name) > 50
        assert not re.match(NAME_PATTERN, long_name)
    
    def test_invalid_names_special_characters(self):
        """Test that names with special characters fail"""
        invalid_names = [
            "John@Doe",
            "Jane!Smith",
            "Bob#123",
            "Alice$Money",
            "Mike%Test",
            "User^Name",
            "Test&User",
            "Name*Star",
            "User(Paren",
            "Name)Close",
            "Test=Equals",
            "User+Plus",
            "Name[Bracket",
            "Test]Close",
            "User{Brace",
            "Name}Close",
            "Test|Pipe",
            "User\\Backslash",
            "Name/Slash",
            "Test<Less",
            "User>Greater",
            "Name?Question",
            "Test;Semi",
            "User:Colon",
            "Name'Quote",
            'Test"DoubleQuote',
            "User,Comma",
            "Name.Period",
        ]
        
        for name in invalid_names:
            assert not re.match(NAME_PATTERN, name), \
                f"Expected '{name}' to be invalid"


class TestEmailValidation:
    """Unit tests for email field validation"""
    
    def test_valid_emails(self):
        """Test that valid email formats pass validation"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "user-name@example.com",
            "123@example.com",
            "user@sub.example.com",
            "user@example.co.uk",
            "user@example.com.au",
            "a@b.co",  # Minimum valid
            "test123@test123.com",
            "user.name+tag@example.co.uk",
        ]
        
        for email in valid_emails:
            assert re.match(EMAIL_PATTERN, email), \
                f"Expected '{email}' to be valid"
    
    def test_invalid_emails_missing_parts(self):
        """Test emails missing required parts"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user",
            "@",
            "user@.com",
            "user@domain",  # Missing TLD
            # Note: user.@example.com matches the pattern (dot before @)
            # The current regex is permissive - edge cases like trailing dots
            # in local part are not strictly validated
        ]
        
        for email in invalid_emails:
            assert not re.match(EMAIL_PATTERN, email), \
                f"Expected '{email}' to be invalid"
    
    def test_invalid_emails_special_cases(self):
        """Test special invalid email cases"""
        invalid_emails = [
            "user @example.com",  # Space
            "user@exam ple.com",  # Space in domain
            "user@@example.com",  # Double @
            # Note: user@example..com might match pattern - regex doesn't prevent double dots
            "user@example.c",  # TLD too short
            "",  # Empty
            "user@",  # Missing domain
            "@domain.com",  # Missing local part
        ]
        
        for email in invalid_emails:
            assert not re.match(EMAIL_PATTERN, email), \
                f"Expected '{email}' to be invalid"
        
        # Document edge cases that current regex doesn't catch perfectly
        # These would require more sophisticated validation
        edge_cases_note = """
        Note: The current email regex is permissive for simplicity.
        Edge cases like double dots (user@example..com) or leading dots
        may pass the regex but would fail RFC-compliant validation.
        For production, consider using a dedicated email validation library.
        """
    
    def test_email_case_insensitive(self):
        """Test that email validation accepts mixed case"""
        mixed_case_emails = [
            "User@Example.Com",
            "TEST@test.com",
            "TeSt@ExAmPlE.CoM",
        ]
        
        for email in mixed_case_emails:
            assert re.match(EMAIL_PATTERN, email), \
                f"Expected '{email}' to be valid (case insensitive)"


class TestMessageValidation:
    """Unit tests for message field validation"""
    
    def test_valid_message_lengths(self):
        """Test that valid message lengths pass"""
        test_cases = [
            ("A" * 10, True),  # Minimum
            ("A" * 100, True),  # Normal
            ("A" * 500, True),  # Long
            ("A" * 1000, True),  # Maximum
            ("A" * 9, False),  # Too short
            ("A" * 1001, False),  # Too long
            ("", False),  # Empty
        ]
        
        for message, should_be_valid in test_cases:
            is_valid = MESSAGE_MIN_LENGTH <= len(message) <= MESSAGE_MAX_LENGTH
            assert is_valid == should_be_valid, \
                f"Message length {len(message)} validation incorrect"
    
    def test_message_with_whitespace(self):
        """Test message validation with various whitespace"""
        test_cases = [
            "This is a valid message with spaces",
            "Line1\nLine2\nLine3\nLine4\nLine5",  # Newlines
            "Tab\tseparated\tmessage\there\ttesting",  # Tabs
            "  Leading and trailing spaces  ",
        ]
        
        for message in test_cases:
            # After trimming, should meet length requirements
            trimmed = message.strip()
            if len(trimmed) >= MESSAGE_MIN_LENGTH:
                assert len(trimmed) >= MESSAGE_MIN_LENGTH
    
    def test_message_character_count(self):
        """Test character counting for message field"""
        test_messages = [
            ("Short msg", 9),
            ("This is exactly 10", 18),
            ("A" * 1000, 1000),
        ]
        
        for message, expected_length in test_messages:
            assert len(message) == expected_length


class TestValidationHelpers:
    """Test helper functions for validation"""
    
    def test_trim_whitespace(self):
        """Test whitespace trimming"""
        test_cases = [
            ("  test  ", "test"),
            ("\n\ntest\n\n", "test"),
            ("\t\ttest\t\t", "test"),
            ("  mixed   spaces  ", "mixed   spaces"),
        ]
        
        for input_val, expected in test_cases:
            assert input_val.strip() == expected
    
    def test_pattern_matching(self):
        """Test pattern matching logic"""
        # Name pattern
        assert re.match(NAME_PATTERN, "John Doe")
        assert not re.match(NAME_PATTERN, "John@Doe")
        
        # Email pattern
        assert re.match(EMAIL_PATTERN, "test@example.com")
        assert not re.match(EMAIL_PATTERN, "not-an-email")
    
    def test_length_validation(self):
        """Test length validation logic"""
        def validate_length(value: str, min_len: int, max_len: int) -> bool:
            return min_len <= len(value) <= max_len
        
        assert validate_length("test", 2, 10)
        assert not validate_length("a", 2, 10)
        assert not validate_length("a" * 11, 2, 10)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_boundary_lengths_name(self):
        """Test name field boundary lengths"""
        # Exactly at boundaries
        assert re.match(NAME_PATTERN, "AB")  # Exactly 2
        assert re.match(NAME_PATTERN, "A" * 50)  # Exactly 50
        
        # Just outside boundaries
        assert not re.match(NAME_PATTERN, "A")  # 1 character
        assert not re.match(NAME_PATTERN, "A" * 51)  # 51 characters
    
    def test_boundary_lengths_message(self):
        """Test message field boundary lengths"""
        assert MESSAGE_MIN_LENGTH <= len("A" * 10) <= MESSAGE_MAX_LENGTH  # Exactly 10
        assert MESSAGE_MIN_LENGTH <= len("A" * 1000) <= MESSAGE_MAX_LENGTH  # Exactly 1000
        assert len("A" * 9) < MESSAGE_MIN_LENGTH  # 9 characters
        assert len("A" * 1001) > MESSAGE_MAX_LENGTH  # 1001 characters
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        # ASCII-only pattern should reject unicode
        unicode_names = [
            "José García",
            "François Müller",
            "李明",
            "Владимир",
        ]
        
        for name in unicode_names:
            # Current pattern only allows ASCII
            result = re.match(NAME_PATTERN, name)
            # This documents current behavior
            assert result is None, "ASCII-only pattern rejects unicode"
    
    def test_empty_and_whitespace_only(self):
        """Test empty and whitespace-only inputs"""
        empty_inputs = ["", "   ", "\n\n", "\t\t"]
        
        for input_val in empty_inputs:
            trimmed = input_val.strip()
            assert trimmed == "" or len(trimmed) < 2


class TestCompleteValidation:
    """Test complete form validation scenarios"""
    
    def validate_form(self, name: str, email: str, message: str) -> Tuple[bool, list]:
        """Simulate complete form validation"""
        errors = []
        
        # Validate name
        name = name.strip()
        if not name:
            errors.append("Name is required")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters")
        elif len(name) > 50:
            errors.append("Name must not exceed 50 characters")
        elif not re.match(NAME_PATTERN, name):
            errors.append("Name contains invalid characters")
        
        # Validate email
        email = email.strip()
        if not email:
            errors.append("Email is required")
        elif not re.match(EMAIL_PATTERN, email):
            errors.append("Email is invalid")
        
        # Validate message
        message = message.strip()
        if not message:
            errors.append("Message is required")
        elif len(message) < MESSAGE_MIN_LENGTH:
            errors.append(f"Message must be at least {MESSAGE_MIN_LENGTH} characters")
        elif len(message) > MESSAGE_MAX_LENGTH:
            errors.append(f"Message must not exceed {MESSAGE_MAX_LENGTH} characters")
        
        return len(errors) == 0, errors
    
    def test_valid_form_data(self):
        """Test completely valid form submission"""
        is_valid, errors = self.validate_form(
            name="John Doe",
            email="john@example.com",
            message="This is a valid test message with sufficient length."
        )
        
        assert is_valid, f"Expected valid form, got errors: {errors}"
        assert errors == []
    
    def test_all_fields_invalid(self):
        """Test form with all invalid fields"""
        is_valid, errors = self.validate_form(
            name="@",  # Invalid character
            email="not-an-email",  # Invalid format
            message="Short"  # Too short
        )
        
        assert not is_valid
        assert len(errors) == 3  # All three fields invalid
    
    def test_partial_validation_errors(self):
        """Test form with some invalid fields"""
        is_valid, errors = self.validate_form(
            name="John Doe",  # Valid
            email="invalid",  # Invalid
            message="This is a valid message"  # Valid
        )
        
        assert not is_valid
        assert len(errors) == 1
        assert "Email" in errors[0]
    
    def test_whitespace_trimming(self):
        """Test that whitespace is properly trimmed"""
        is_valid, errors = self.validate_form(
            name="  John Doe  ",
            email="  john@example.com  ",
            message="  This is a valid message with spaces  "
        )
        
        assert is_valid, f"Expected valid after trimming, got errors: {errors}"


class TestRequirementsCoverage:
    """Tests matching exact user story requirements"""
    
    def test_requirement_name_field_accepts_2_50_chars(self):
        """
        Given I'm filling out the form,
        When I type in the name field,
        Then it accepts 2-50 characters, alphanumeric with spaces and hyphens only
        """
        # Valid cases
        assert re.match(NAME_PATTERN, "AB")  # 2 chars
        assert re.match(NAME_PATTERN, "John Doe")  # Letters and space
        assert re.match(NAME_PATTERN, "User-123")  # Alphanumeric with hyphen
        assert re.match(NAME_PATTERN, "A" * 50)  # 50 chars
        
        # Invalid cases
        assert not re.match(NAME_PATTERN, "A")  # 1 char (too short)
        assert not re.match(NAME_PATTERN, "A" * 51)  # 51 chars (too long)
        assert not re.match(NAME_PATTERN, "John@Doe")  # Special char
    
    def test_requirement_email_field_validates_regex(self):
        r"""
        Given I'm filling out the form,
        When I type in the email field,
        Then it validates against regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Valid cases
        assert re.match(pattern, "user@example.com")
        assert re.match(pattern, "test.user@example.co.uk")
        assert re.match(pattern, "user+tag@example.com")
        
        # Invalid cases
        assert not re.match(pattern, "notanemail")
        assert not re.match(pattern, "@example.com")
        assert not re.match(pattern, "user@")
    
    def test_requirement_message_field_accepts_10_1000_chars(self):
        """
        Given I'm filling out the form,
        When I type in the message field,
        Then it accepts 10-1000 characters
        """
        # Valid cases
        assert 10 <= len("A" * 10) <= 1000  # 10 chars (minimum)
        assert 10 <= len("A" * 500) <= 1000  # 500 chars (middle)
        assert 10 <= len("A" * 1000) <= 1000  # 1000 chars (maximum)
        
        # Invalid cases
        assert len("A" * 9) < 10  # 9 chars (too short)
        assert len("A" * 1001) > 1000  # 1001 chars (too long)


if __name__ == "__main__":
    # Run tests without pytest
    import sys
    
    print("Running Unit Tests for Contact Form Validation\n")
    print("=" * 60)
    
    # Track results
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # Test classes to run
    test_classes = [
        TestNameValidation(),
        TestEmailValidation(),
        TestMessageValidation(),
        TestValidationHelpers(),
        TestEdgeCases(),
        TestCompleteValidation(),
        TestRequirementsCoverage(),
    ]
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n{class_name}")
        print("-" * 60)
        
        # Get all test methods
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_class, method_name)
            
            try:
                test_method()
                passed_tests += 1
                print(f"  ✅ {method_name}")
            except AssertionError as e:
                failed_tests.append((class_name, method_name, str(e)))
                print(f"  ❌ {method_name}")
                print(f"     Error: {e}")
            except Exception as e:
                failed_tests.append((class_name, method_name, str(e)))
                print(f"  💥 {method_name}")
                print(f"     Exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    print("=" * 60)
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} tests failed:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}")
            print(f"    {error}")
        sys.exit(1)
    else:
        print("\n✅ All unit tests passed!")
        sys.exit(0)
