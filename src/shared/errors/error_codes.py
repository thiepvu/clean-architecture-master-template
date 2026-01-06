"""Error code enumeration and registry"""

from enum import Enum
from typing import Dict, Optional, Tuple


class HttpStatus(int, Enum):
    """
    HTTP Status Codes.

    Provides type-safe HTTP status codes with semantic naming.
    """

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 3xx Redirection
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308

    # 4xx Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    GONE = 410
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

    def is_success(self) -> bool:
        """Check if status code indicates success (2xx)."""
        return 200 <= self.value < 300

    def is_redirect(self) -> bool:
        """Check if status code indicates redirect (3xx)."""
        return 300 <= self.value < 400

    def is_client_error(self) -> bool:
        """Check if status code indicates client error (4xx)."""
        return 400 <= self.value < 500

    def is_server_error(self) -> bool:
        """Check if status code indicates server error (5xx)."""
        return 500 <= self.value < 600


class ErrorCode(str, Enum):
    """
    Standard error codes used throughout the application.
    Provides consistent error identification.

    Error codes follow the pattern: CATEGORY_SPECIFIC_ERROR
    """

    # Client errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Server errors (5xx)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # Domain errors
    DOMAIN_VALIDATION_ERROR = "DOMAIN_VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"

    # Infrastructure errors
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"

    def __str__(self) -> str:
        """String representation"""
        return self.value


class ErrorCodeRegistry:
    """
    Centralized registry for mapping error codes to HTTP status codes.

    Example:
        registry = ErrorCodeRegistry()
        registry.register("USER_NOT_FOUND", 404, "User not found")
        registry.register("INVALID_EMAIL", 422, "Invalid email format")

        status, message = registry.get("USER_NOT_FOUND")
    """

    _instance: Optional["ErrorCodeRegistry"] = None
    _registry: Dict[str, Tuple[int, str]] = {}

    def __new__(cls) -> "ErrorCodeRegistry":
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_defaults()
        return cls._instance

    def _init_defaults(self) -> None:
        """Initialize default error code mappings"""
        defaults = {
            # Client errors
            ErrorCode.BAD_REQUEST: (400, "Bad request"),
            ErrorCode.UNAUTHORIZED: (401, "Unauthorized"),
            ErrorCode.FORBIDDEN: (403, "Forbidden"),
            ErrorCode.NOT_FOUND: (404, "Not found"),
            ErrorCode.CONFLICT: (409, "Conflict"),
            ErrorCode.VALIDATION_ERROR: (422, "Validation error"),
            ErrorCode.UNPROCESSABLE_ENTITY: (422, "Unprocessable entity"),
            # Server errors
            ErrorCode.INTERNAL_SERVER_ERROR: (500, "Internal server error"),
            ErrorCode.SERVICE_UNAVAILABLE: (503, "Service unavailable"),
            # Domain errors
            ErrorCode.DOMAIN_VALIDATION_ERROR: (422, "Domain validation error"),
            ErrorCode.BUSINESS_RULE_VIOLATION: (422, "Business rule violation"),
            # Infrastructure errors
            ErrorCode.DATABASE_ERROR: (500, "Database error"),
            ErrorCode.EXTERNAL_SERVICE_ERROR: (502, "External service error"),
            ErrorCode.CACHE_ERROR: (500, "Cache error"),
        }

        for code, (status, message) in defaults.items():
            self._registry[code.value] = (status, message)

    def register(
        self,
        code: str,
        http_status: int,
        default_message: str,
    ) -> None:
        """
        Register an error code mapping.

        Args:
            code: Error code string
            http_status: HTTP status code
            default_message: Default error message
        """
        self._registry[code] = (http_status, default_message)

    def get(self, code: str) -> Tuple[int, str]:
        """
        Get HTTP status and message for an error code.

        Args:
            code: Error code string

        Returns:
            Tuple of (http_status, default_message)
        """
        return self._registry.get(code, (500, "Unknown error"))

    def get_status(self, code: str) -> int:
        """Get HTTP status for an error code."""
        return self.get(code)[0]

    def get_message(self, code: str) -> str:
        """Get default message for an error code."""
        return self.get(code)[1]
