"""
Exception classes for unexpected errors.

Note: For expected business errors, prefer using the Result Pattern
from shared.domain.result. These exceptions are for:
- Truly unexpected errors
- Framework integration (FastAPI exception handlers)
- Infrastructure failures
"""

from typing import Any, Dict, Optional

from .error_codes import ErrorCode


class BaseException(Exception):
    """
    Base application exception.
    All custom exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            error_code: Error code enum
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class DomainException(BaseException):
    """
    Domain layer exception.
    Used for business rule violations.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DOMAIN_VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class NotFoundException(BaseException):
    """Resource not found exception"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ValidationException(BaseException):
    """Validation exception"""

    def __init__(self, message: str, errors: Dict[str, Any]):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details={"errors": errors},
        )


class ConflictException(BaseException):
    """Conflict exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code=ErrorCode.CONFLICT, status_code=409, details=details
        )


class UnauthorizedException(BaseException):
    """Unauthorized exception"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message=message, error_code=ErrorCode.UNAUTHORIZED, status_code=401)


class ForbiddenException(BaseException):
    """Forbidden exception"""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message=message, error_code=ErrorCode.FORBIDDEN, status_code=403)


class BadRequestException(BaseException):
    """Bad request exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code=ErrorCode.BAD_REQUEST, status_code=400, details=details
        )


class InternalServerException(BaseException):
    """Internal server error exception"""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            message=message, error_code=ErrorCode.INTERNAL_SERVER_ERROR, status_code=500
        )
