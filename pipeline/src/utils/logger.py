"""
Logging utilities for the pipeline.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "stage"):
            log_data["stage"] = record.stage
        if hasattr(record, "execution_id"):
            log_data["execution_id"] = record.execution_id
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class PipelineLogger:
    """
    Centralized logging for the pipeline.
    """
    
    def __init__(
        self,
        name: str = "pipeline",
        level: str = "INFO",
        log_file: Optional[Path] = None,
        use_json: bool = True
    ):
        """
        Initialize pipeline logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logging
            use_json: Use JSON formatting
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if use_json:
            console_handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(JSONFormatter() if use_json else formatter)
            self.logger.addHandler(file_handler)
    
    def log_stage_execution(
        self,
        stage: str,
        execution_id: str,
        status: str,
        duration: Optional[float] = None,
        **kwargs
    ):
        """
        Log stage execution information.
        
        Args:
            stage: Stage name
            execution_id: Execution ID
            status: Stage status
            duration: Optional execution duration
            **kwargs: Additional context
        """
        extra = {
            "stage": stage,
            "execution_id": execution_id,
        }
        if duration is not None:
            extra["duration"] = duration
        
        message = f"Stage {stage} {status}"
        if kwargs:
            message += f" - {kwargs}"
        
        self.logger.info(message, extra=extra)
    
    def log_pipeline_start(self, execution_id: str, input_summary: Dict[str, Any]):
        """Log pipeline execution start."""
        self.logger.info(
            f"Pipeline execution started: {execution_id}",
            extra={"execution_id": execution_id, "input_summary": input_summary}
        )
    
    def log_pipeline_complete(
        self,
        execution_id: str,
        duration: float,
        output_summary: Dict[str, Any]
    ):
        """Log pipeline execution completion."""
        self.logger.info(
            f"Pipeline execution completed: {execution_id}",
            extra={
                "execution_id": execution_id,
                "duration": duration,
                "output_summary": output_summary
            }
        )
    
    def log_error(
        self,
        message: str,
        error: Exception,
        execution_id: Optional[str] = None,
        stage: Optional[str] = None
    ):
        """
        Log error with context.
        
        Args:
            message: Error message
            error: Exception object
            execution_id: Optional execution ID
            stage: Optional stage name
        """
        extra = {}
        if execution_id:
            extra["execution_id"] = execution_id
        if stage:
            extra["stage"] = stage
        
        self.logger.error(
            f"{message}: {str(error)}",
            exc_info=True,
            extra=extra
        )
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
