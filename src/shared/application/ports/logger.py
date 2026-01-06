"""
Logger Port (Interface).

Defines the contract for logging operations.
Implementations: StandardLoggerAdapter
"""

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class ILogger(Protocol):
    """
    Logger port (interface).

    All logger adapters must implement this protocol.
    Provides structured logging with context support.

    Example:
        class StandardLoggerAdapter:
            def info(self, message: str, *args, **kwargs) -> None:
                self._logger.info(message, *args, **kwargs)
    """

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log debug message.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log info message.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log warning message.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log error message.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log critical message.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log exception with traceback.

        Args:
            message: Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        ...

    def set_context(self, **kwargs: Any) -> None:
        """
        Set context for subsequent log messages.

        Args:
            **kwargs: Context key-value pairs (e.g., request_id, user_id)
        """
        ...

    def clear_context(self) -> None:
        """
        Clear all context.
        """
        ...

    def get_child(self, name: str) -> "ILogger":
        """
        Get a child logger with the given name.

        Args:
            name: Child logger name

        Returns:
            Child logger instance
        """
        ...

    def health_check(self) -> bool:
        """
        Check if logger is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    def initialize(self) -> None:
        """
        Initialize the logger.

        Called during application startup.
        Should configure handlers and formatters.
        """
        ...

    def close(self) -> None:
        """
        Close the logger.

        Called during application shutdown.
        Should flush and cleanup handlers.
        """
        ...
