"""Structured logging module for JSON-formatted logs."""
import json
import logging
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """
    Provides structured JSON logging for consistent log formatting.

    All log entries include:
    - timestamp: ISO format timestamp
    - level: Log level (INFO, DEBUG, WARNING, ERROR)
    - message: The log message
    - Additional context from kwargs
    """

    def __init__(self, name: str = "workflow-analyzer"):
        """
        Initialize the structured logger.

        Args:
            name: Logger name for identification
        """
        self.name = name
        self.logger = logging.getLogger(name)

    def _format_log(self, level: str, message: str, **kwargs) -> str:
        """
        Format a log entry as JSON.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context

        Returns:
            JSON-formatted log string
        """
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "logger": self.name,
        }
        # Add any additional context
        log_entry.update(kwargs)
        return json.dumps(log_entry)

    def info(self, msg: str, **kwargs) -> None:
        """
        Log an info level message.

        Args:
            msg: The log message
            **kwargs: Additional context to include in the log
        """
        formatted = self._format_log("INFO", msg, **kwargs)
        self.logger.info(formatted)

    def debug(self, msg: str, **kwargs) -> None:
        """
        Log a debug level message.

        Args:
            msg: The log message
            **kwargs: Additional context to include in the log
        """
        formatted = self._format_log("DEBUG", msg, **kwargs)
        self.logger.debug(formatted)

    def warning(self, msg: str, **kwargs) -> None:
        """
        Log a warning level message.

        Args:
            msg: The log message
            **kwargs: Additional context to include in the log
        """
        formatted = self._format_log("WARNING", msg, **kwargs)
        self.logger.warning(formatted)

    def error(self, msg: str, **kwargs) -> None:
        """
        Log an error level message.

        Args:
            msg: The log message
            **kwargs: Additional context to include in the log
        """
        formatted = self._format_log("ERROR", msg, **kwargs)
        self.logger.error(formatted)
