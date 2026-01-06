"""
Standard Logger Adapter.

Implements ILogger using Python's standard logging library.
Supports structured logging with JSON and colored console output.

This adapter only implements - it receives config from factory.
"""

import logging
from contextvars import ContextVar
from typing import Any, Dict, Optional

from config.logging import StandardLoggerConfig
from infrastructure.logging.adapters.formatters import setup_logging

# Context variable for storing log context
_log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})


class StandardLoggerAdapter:
    """
    Standard Python logger adapter implementing ILogger.

    Uses Python's built-in logging library with custom formatters.
    Supports context propagation across async calls using ContextVar.

    Responsibilities:
    - Receive StandardLoggerConfig from factory
    - Initialize handlers and formatters
    - Provide logging methods (debug, info, warning, error, critical)
    - Support context propagation
    - Health check

    NOT responsible for:
    - Loading config (factory does this)

    Example:
        # Created by factory
        adapter = StandardLoggerAdapter(config=adapter_config, name="app")
        adapter.initialize()

        # Usage
        adapter.set_context(request_id="123", user_id="456")
        adapter.info("Processing request")
        adapter.clear_context()
    """

    def __init__(
        self,
        config: StandardLoggerConfig,
        name: str = "app",
    ):
        """
        Initialize standard logger adapter.

        Args:
            config: StandardLoggerConfig instance (from factory)
            name: Logger name
        """
        self._config = config
        self._name = name
        self._logger: Optional[logging.Logger] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the logger with handlers and formatters."""
        if self._initialized:
            return

        # Setup logging configuration
        setup_logging(
            level=self._config.level,
            format_type=self._config.format,
            log_dir=self._config.log_dir,
            max_bytes=self._config.max_bytes,
            backup_count=self._config.backup_count,
            retention_days=self._config.retention_days,
            separate_error_log=True,
            use_daily_rotation=self._config.use_daily_rotation,
        )

        self._logger = logging.getLogger(self._name)
        self._initialized = True

    def close(self) -> None:
        """Close the logger and flush handlers."""
        if self._logger:
            for handler in self._logger.handlers:
                handler.flush()
                handler.close()

    def health_check(self) -> bool:
        """Check if logger is healthy."""
        return self._initialized and self._logger is not None

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log(logging.ERROR, message, *args, **kwargs)

    def set_context(self, **kwargs: Any) -> None:
        """Set context for subsequent log messages."""
        current = _log_context.get().copy()
        current.update(kwargs)
        _log_context.set(current)

    def clear_context(self) -> None:
        """Clear all context."""
        _log_context.set({})

    def get_child(self, name: str) -> "StandardLoggerAdapter":
        """Get a child logger with the given name."""
        child = StandardLoggerAdapter(
            config=self._config,
            name=f"{self._name}.{name}",
        )
        child._logger = self._logger.getChild(name) if self._logger else None
        child._initialized = self._initialized
        return child

    def _log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        """Internal logging method."""
        if not self._logger:
            return

        # Get context
        context = _log_context.get()
        extra = kwargs.pop("extra", {})
        extra.update(context)

        self._logger.log(level, message, *args, extra=extra, **kwargs)
