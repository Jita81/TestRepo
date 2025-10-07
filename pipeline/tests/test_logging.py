"""Tests for logging configuration."""

import pytest
import logging
from common.logging_config import configure_logging, get_logger


class TestConfigureLogging:
    """Tests for configure_logging function."""
    
    def test_configure_with_defaults(self):
        """Test logging configuration with defaults."""
        configure_logging()
        logger = get_logger("test")
        assert logger is not None
    
    def test_configure_with_custom_level(self):
        """Test logging with custom level."""
        configure_logging(log_level="DEBUG")
        logger = get_logger("test.debug")
        assert logger is not None
    
    def test_configure_json_logs(self):
        """Test JSON log output."""
        configure_logging(json_logs=True)
        logger = get_logger("test.json")
        assert logger is not None
    
    def test_configure_console_logs(self):
        """Test console log output."""
        configure_logging(json_logs=False)
        logger = get_logger("test.console")
        assert logger is not None


class TestGetLogger:
    """Tests for get_logger function."""
    
    def test_get_logger_returns_instance(self):
        """Test that get_logger returns a logger."""
        logger = get_logger("test.instance")
        assert logger is not None
    
    def test_get_logger_with_name(self):
        """Test logger with specific name."""
        logger = get_logger(__name__)
        assert logger is not None
    
    def test_logger_can_log(self):
        """Test that logger can actually log."""
        logger = get_logger("test.log")
        # Should not raise an exception
        logger.info("test_message", key="value")
        logger.debug("debug_message")
        logger.warning("warning_message")
        logger.error("error_message")