"""
Shared Presentation Layer Components.

Common utilities for API/HTTP presentation layer.

Contains:
- Base controller class
- FastAPI dependencies (CommandBus, QueryBus)
- Response helpers
- Pagination support
- Exception handlers
- Middleware (logging, request context)
"""

from .base_controller import BaseController
from .dependencies import CommandBusDep, QueryBusDep
from .error_handler import (
    app_exception_handler,
    database_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .middleware import (
    RequestContext,
    RequestContextMiddleware,
    RequestLoggingMiddleware,
    get_request_context,
    get_request_id,
)
from .pagination import PaginatedResponse, PaginationParams
from .response import ApiResponse

__all__ = [
    # Base Controller
    "BaseController",
    # Dependencies
    "CommandBusDep",
    "QueryBusDep",
    # Response
    "ApiResponse",
    # Pagination
    "PaginatedResponse",
    "PaginationParams",
    # Exception Handlers
    "app_exception_handler",
    "validation_exception_handler",
    "http_exception_handler",
    "database_exception_handler",
    "generic_exception_handler",
    # Middleware
    "RequestContextMiddleware",
    "RequestLoggingMiddleware",
    "get_request_id",
    "get_request_context",
    "RequestContext",
]
