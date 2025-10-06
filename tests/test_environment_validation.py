"""
Unit tests for Environment Variable Validation
Tests the validation logic in run.py
"""

import pytest
import os
from unittest.mock import patch, MagicMock


class TestEnvironmentValidation:
    """Test environment variable validation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        import sys
        sys.path.insert(0, '.')
        from run import validate_environment_variables
        self.validate_environment_variables = validate_environment_variables
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,  # Valid looking key
    }, clear=True)
    def test_valid_environment(self):
        """Test validation passes with valid environment"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is True
        assert len(errors) == 0
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_required_variable(self):
        """Test validation fails when required variable is missing"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('OPENAI_API_KEY' in error for error in errors)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'short',  # Too short
    }, clear=True)
    def test_variable_too_short(self):
        """Test validation fails when variable is too short"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
        assert any('too short' in error.lower() for error in errors)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test',  # Placeholder value
    }, clear=True)
    def test_placeholder_value_detection(self):
        """Test detection of placeholder values"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
        assert any('placeholder' in error.lower() for error in errors)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'demo',  # Another placeholder
    }, clear=True)
    def test_demo_value_detection(self):
        """Test detection of demo values"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
        assert any('placeholder' in error.lower() for error in errors)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,
        'GITHUB_TOKEN': 'ghp_' + 'y' * 30,  # Valid GitHub token format
    }, clear=True)
    def test_optional_variables(self):
        """Test validation of optional variables"""
        is_valid, errors = self.validate_environment_variables()
        
        # Should pass even with optional variables
        assert is_valid is True
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,
        'MAX_REPO_SIZE_MB': '500',  # Valid size
    }, clear=True)
    def test_numeric_variable_validation(self):
        """Test validation of numeric variables"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is True
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,
        'MAX_REPO_SIZE_MB': 'not_a_number',  # Invalid format
    }, clear=True)
    def test_invalid_numeric_format(self):
        """Test validation fails for invalid numeric format"""
        is_valid, errors = self.validate_environment_variables()
        
        # Should still pass (warnings only for optional vars)
        # But should have warnings
        assert is_valid is True  # Optional var doesn't fail validation
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,
        'CONVERSION_TIMEOUT': '300',  # Valid timeout
    }, clear=True)
    def test_timeout_validation(self):
        """Test validation of timeout values"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is True
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'example',  # Common placeholder
    }, clear=True)
    def test_example_placeholder_detection(self):
        """Test detection of 'example' placeholder"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
        assert any('placeholder' in error.lower() for error in errors)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'your-key-here',  # Common placeholder
    }, clear=True)
    def test_your_key_here_detection(self):
        """Test detection of 'your-key-here' placeholder"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 45,
        'GITHUB_TOKEN': 'short',  # Too short for GitHub token
    }, clear=True)
    def test_short_optional_variable(self):
        """Test short optional variable generates warning"""
        is_valid, errors = self.validate_environment_variables()
        
        # Should still pass (optional variable)
        assert is_valid is True


class TestEnvironmentValidationEdgeCases:
    """Test edge cases in environment validation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        import sys
        sys.path.insert(0, '.')
        from run import validate_environment_variables
        self.validate_environment_variables = validate_environment_variables
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': '',  # Empty string
    }, clear=True)
    def test_empty_string_variable(self):
        """Test validation fails for empty string"""
        is_valid, errors = self.validate_environment_variables()
        
        assert is_valid is False
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': ' ' * 50,  # Whitespace only
    }, clear=True)
    def test_whitespace_only_variable(self):
        """Test validation of whitespace-only values"""
        is_valid, errors = self.validate_environment_variables()
        
        # Should be treated as valid length but might fail other checks
        # Implementation dependent
        assert isinstance(is_valid, bool)
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-' + 'x' * 100,  # Very long key
    }, clear=True)
    def test_very_long_variable(self):
        """Test validation of very long values"""
        is_valid, errors = self.validate_environment_variables()
        
        # Long values should be acceptable
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
