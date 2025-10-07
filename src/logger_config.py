"""
Comprehensive Logging Configuration Module
Provides structured logging with rotation, JSON format, and multiple handlers.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import traceback
from contextvars import ContextVar

# Context variable for request tracking
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    """
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread,
            'thread_name': record.threadName,
        }
        
        # Add request context if available
        try:
            ctx = request_context.get()
            if ctx:
                log_data['context'] = ctx
        except LookupError:
            pass
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add stack trace for errors and critical logs
        if record.levelno >= logging.ERROR and not record.exc_info:
            log_data['stack_trace'] = ''.join(traceback.format_stack())
        
        # Add extra fields from the record
        if self.include_extra:
            extra_fields = {
                key: value
                for key, value in record.__dict__.items()
                if key not in [
                    'name', 'msg', 'args', 'created', 'filename', 'funcName',
                    'levelname', 'lineno', 'module', 'msecs', 'message',
                    'pathname', 'process', 'processName', 'relativeCreated',
                    'stack_info', 'thread', 'threadName', 'exc_info', 'exc_text'
                ]
            }
            if extra_fields:
                log_data['extra'] = extra_fields
        
        return json.dumps(log_data, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Formatter for console output with colors and human-readable format.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build log message
        log_parts = [
            f"{color}[{timestamp}]{reset}",
            f"{color}[{record.levelname}]{reset}",
            f"[{record.name}]",
            f"{record.getMessage()}"
        ]
        
        # Add location info for debug and errors
        if record.levelno >= logging.ERROR or record.levelno <= logging.DEBUG:
            log_parts.append(f"({record.filename}:{record.lineno})")
        
        message = " ".join(log_parts)
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class LoggerConfig:
    """
    Central logging configuration manager.
    """
    
    def __init__(
        self,
        app_name: str = "app",
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        console_output: bool = True,
        file_output: bool = True,
        json_format: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        structured_console: bool = False
    ):
        """
        Initialize logging configuration.
        
        Args:
            app_name: Name of the application
            log_dir: Directory for log files
            log_level: Minimum log level
            console_output: Enable console logging
            file_output: Enable file logging
            json_format: Use JSON format for file logs
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            structured_console: Use structured JSON format for console
        """
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.console_output = console_output
        self.file_output = file_output
        self.json_format = json_format
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.structured_console = structured_console
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
    
    def _configure_root_logger(self):
        """Configure the root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            if self.structured_console:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(ColoredConsoleFormatter())
            
            root_logger.addHandler(console_handler)
        
        # Add file handlers
        if self.file_output:
            # General application log
            app_log_file = self.log_dir / f"{self.app_name}.log"
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            app_handler.setLevel(self.log_level)
            
            if self.json_format:
                app_handler.setFormatter(StructuredFormatter())
            else:
                app_handler.setFormatter(
                    logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                )
            
            root_logger.addHandler(app_handler)
            
            # Error log (only ERROR and above)
            error_log_file = self.log_dir / f"{self.app_name}_error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            if self.json_format:
                error_handler.setFormatter(StructuredFormatter())
            else:
                error_handler.setFormatter(
                    logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d'
                    )
                )
            
            root_logger.addHandler(error_handler)
            
            # Access log for HTTP requests
            access_log_file = self.log_dir / f"{self.app_name}_access.log"
            access_handler = logging.handlers.RotatingFileHandler(
                access_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            access_handler.setLevel(logging.INFO)
            access_handler.addFilter(AccessLogFilter())
            
            if self.json_format:
                access_handler.setFormatter(StructuredFormatter())
            else:
                access_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(message)s')
                )
            
            root_logger.addHandler(access_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the given name.
        
        Args:
            name: Name for the logger (typically __name__)
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)
    
    def set_request_context(self, **kwargs):
        """
        Set context information for the current request.
        
        Args:
            **kwargs: Key-value pairs to add to request context
        """
        ctx = request_context.get().copy()
        ctx.update(kwargs)
        request_context.set(ctx)
    
    def clear_request_context(self):
        """Clear the request context."""
        request_context.set({})
    
    def add_file_handler(
        self,
        name: str,
        level: int = logging.INFO,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None
    ) -> logging.Handler:
        """
        Add a custom file handler to the root logger.
        
        Args:
            name: Name for the log file
            level: Log level for this handler
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
            
        Returns:
            The created handler
        """
        log_file = self.log_dir / f"{name}.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes or self.max_bytes,
            backupCount=backup_count or self.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(level)
        
        if self.json_format:
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        
        logging.getLogger().addHandler(handler)
        return handler


class AccessLogFilter(logging.Filter):
    """Filter to identify access log entries."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Only allow records with 'access' in the name or message."""
        return 'access' in record.name.lower() or hasattr(record, 'access_log')


# Singleton instance
_logger_config: Optional[LoggerConfig] = None


def setup_logging(
    app_name: str = "github_to_app",
    log_dir: str = "logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    json_format: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    structured_console: bool = False
) -> LoggerConfig:
    """
    Setup logging configuration for the application.
    
    Args:
        app_name: Name of the application
        log_dir: Directory for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console logging
        file_output: Enable file logging
        json_format: Use JSON format for file logs
        max_bytes: Maximum size of log file before rotation (bytes)
        backup_count: Number of backup files to keep
        structured_console: Use structured JSON format for console
        
    Returns:
        LoggerConfig instance
    """
    global _logger_config
    
    # Convert string log level to int
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    numeric_level = level_map.get(log_level.upper(), logging.INFO)
    
    _logger_config = LoggerConfig(
        app_name=app_name,
        log_dir=log_dir,
        log_level=numeric_level,
        console_output=console_output,
        file_output=file_output,
        json_format=json_format,
        max_bytes=max_bytes,
        backup_count=backup_count,
        structured_console=structured_console
    )
    
    return _logger_config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    if _logger_config is None:
        # Setup with defaults if not configured
        setup_logging()
    
    return logging.getLogger(name)


def set_request_context(**kwargs):
    """
    Set context information for the current request.
    
    Args:
        **kwargs: Key-value pairs to add to request context
    """
    if _logger_config:
        _logger_config.set_request_context(**kwargs)


def clear_request_context():
    """Clear the request context."""
    if _logger_config:
        _logger_config.clear_request_context()