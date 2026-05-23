"""
Logging configuration with structured JSON logging.
Supports both console and file output.
"""

import logging
import logging.config
from typing import Optional
import json
from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure logging based on settings."""

    if settings.LOG_FORMAT == "json":
        _setup_json_logging()
    else:
        _setup_text_logging()


def _setup_json_logging() -> None:
    """Setup JSON structured logging."""
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": settings.LOG_LEVEL,
        },
    }

    if settings.LOG_FILE:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "json",
            "level": settings.LOG_LEVEL,
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                },
            },
            "handlers": handlers,
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": list(handlers.keys()),
            },
        }
    )


def _setup_text_logging() -> None:
    """Setup plain text logging."""
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": settings.LOG_LEVEL,
        },
    }

    if settings.LOG_FILE:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "standard",
            "level": settings.LOG_LEVEL,
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    ),
                },
            },
            "handlers": handlers,
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": list(handlers.keys()),
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
