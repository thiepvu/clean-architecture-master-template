"""
Centralized Error Handlers.

Provides consistent error handling across the application.
All error responses include:
- Standardized error structure
- Request ID for tracking
- Appropriate HTTP status codes
- Structured logging
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from shared.domain.result import Result
from shared.errors.error_codes import ErrorCode, ErrorCodeRegistry
from shared.errors.exceptions import BaseException as AppBaseException

if TYPE_CHECKING:
    from shared.application.ports import ILogger

# Module-level logger reference (set via configure_logger)
_logger: Optional["ILogger"] = None


def configure_logger(logger: "ILogger") -> None:
    """Configure the module-level logger (called during app startup)."""
    global _logger
    _logger = logger


def _get_request_id(request: Request) -> str:
    """Extract request ID from request context or headers."""
    # Try to get from middleware-set context
    try:
        from shared.presentation.middleware import get_request_id

        request_id = get_request_id()
        if request_id:
            return request_id
    except ImportError:
        pass

    # Fallback to header
    return request.headers.get("X-Request-ID", "unknown")


def _build_error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: str,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Build standardized error response with request ID."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
        headers={"X-Request-ID": request_id},
    )


async def app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    """
    Handle application exceptions.

    Args:
        request: FastAPI request
        exc: Application exception

    Returns:
        JSON response with error details
    """
    request_id = _get_request_id(request)

    if _logger:
        _logger.error(
            f"Application error: {exc.message}",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
            },
        )

    return _build_error_response(
        code=str(exc.error_code),
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id,
        details=exc.details,
    )


def result_error_to_response(result: Result, request: Optional[Request] = None) -> JSONResponse:
    """
    Convert Result error to JSON response.

    Args:
        result: Failed Result object
        request: Optional FastAPI request for logging

    Returns:
        JSON response with error details
    """
    if result.is_success:
        raise ValueError("Cannot convert successful result to error response")

    request_id = _get_request_id(request) if request else "unknown"
    registry = ErrorCodeRegistry()
    http_status = registry.get_status(result.error_code)

    if request and _logger:
        _logger.error(
            f"Result error: {result.error_message}",
            extra={
                "request_id": request_id,
                "error_code": result.error_code,
                "path": request.url.path,
                "method": request.method,
            },
        )

    return _build_error_response(
        code=result.error_code,
        message=result.error_message,
        status_code=http_status,
        request_id=request_id,
        details=result.error.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation exceptions.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSON response with validation errors
    """
    request_id = _get_request_id(request)

    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else "body"
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    if _logger:
        _logger.warning(
            f"Validation error: {len(errors)} field(s) failed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_count": len(errors),
            },
        )

    return _build_error_response(
        code=ErrorCode.VALIDATION_ERROR.value,
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id,
        details={"errors": errors},
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database exceptions.

    Args:
        request: FastAPI request
        exc: SQLAlchemy exception

    Returns:
        JSON response with database error
    """
    request_id = _get_request_id(request)

    if _logger:
        _logger.error(
            f"Database error: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=True,
        )

    return _build_error_response(
        code=ErrorCode.DATABASE_ERROR.value,
        message="A database error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic/unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Generic exception

    Returns:
        JSON response with generic error
    """
    request_id = _get_request_id(request)

    if _logger:
        _logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )

    return _build_error_response(
        code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle FastAPI HTTPException.

    Args:
        request: FastAPI request
        exc: HTTPException

    Returns:
        JSON response with error details
    """
    from fastapi import HTTPException

    if not isinstance(exc, HTTPException):
        return await generic_exception_handler(request, exc)

    request_id = _get_request_id(request)

    # Log error for status codes >= 400
    if _logger and exc.status_code >= 400:
        error_info = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
        error_code = (
            error_info.get("error", {}).get("code", "UNKNOWN")
            if isinstance(error_info, dict)
            else "UNKNOWN"
        )
        error_message = (
            error_info.get("error", {}).get("message", str(exc.detail))
            if isinstance(error_info, dict)
            else str(exc.detail)
        )

        log_method = _logger.warning if exc.status_code < 500 else _logger.error
        log_method(
            f"HTTP {exc.status_code}: [{error_code}] {error_message}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": exc.status_code,
                "error_code": error_code,
            },
        )

    # If detail is already a dict (from our error raising), use it
    if isinstance(exc.detail, dict):
        content = exc.detail.copy()
        content["request_id"] = request_id
        content["timestamp"] = datetime.utcnow().isoformat()
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers={"X-Request-ID": request_id},
        )

    # Otherwise, wrap the message
    return _build_error_response(
        code=_status_to_error_code(exc.status_code),
        message=str(exc.detail),
        status_code=exc.status_code,
        request_id=request_id,
    )


def _status_to_error_code(status_code: int) -> str:
    """Map HTTP status code to error code."""
    mapping = {
        400: ErrorCode.BAD_REQUEST.value,
        401: ErrorCode.UNAUTHORIZED.value,
        403: ErrorCode.FORBIDDEN.value,
        404: ErrorCode.NOT_FOUND.value,
        409: ErrorCode.CONFLICT.value,
        422: ErrorCode.VALIDATION_ERROR.value,
        500: ErrorCode.INTERNAL_SERVER_ERROR.value,
        503: ErrorCode.SERVICE_UNAVAILABLE.value,
    }
    return mapping.get(status_code, ErrorCode.INTERNAL_SERVER_ERROR.value)
