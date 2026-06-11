"""Logging configuration for AegisPy."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
    format_str: str | None = None,
) -> logging.Logger:
    """Configure and return the root logger.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for file logging
        format_str: Optional custom log format string
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("aegispy")
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_str or LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(format_str or LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logger.info("File logging enabled: %s", log_file)
        except OSError as e:
            logger.warning("Failed to setup file logging: %s", e)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to log messages.
    
    Example:
        with LogContext(module="sandbox", script="test.py"):
            logger.info("Executing code")
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize log context.
        
        Args:
            **kwargs: Key-value pairs to add to log context
        """
        self.context = kwargs
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self) -> "LogContext":
        """Enter context and add extra information to logs."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Exit context."""
        pass
    
    def log(self, level: int, msg: str, **kwargs: Any) -> None:
        """Log message with context.
        
        Args:
            level: Logging level
            msg: Log message
            **kwargs: Additional log keyword arguments
        """
        extra = {**self.context, **kwargs}
        self.logger.log(level, msg, extra=extra)
