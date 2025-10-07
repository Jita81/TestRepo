"""
Logging configuration for the POS Pipeline system.
"""
import logging
import logging.config
from pathlib import Path
from pythonjsonlogger import jsonlogger
from config.settings import settings


# Ensure log directory exists
log_dir = Path(settings.log_file).parent
log_dir.mkdir(parents=True, exist_ok=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": settings.log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(Path(settings.log_file).parent / "pipeline.json.log"),
            "maxBytes": 10485760,
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(Path(settings.log_file).parent / "errors.log"),
            "maxBytes": 10485760,
            "backupCount": 5
        }
    },
    "loggers": {
        "pos_pipeline": {
            "level": settings.log_level,
            "handlers": ["console", "file", "json_file", "error_file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["console", "file", "error_file"]
    }
}


def setup_logging():
    """Initialize logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("pos_pipeline")
    logger.info("Logging initialized")
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"pos_pipeline.{name}")