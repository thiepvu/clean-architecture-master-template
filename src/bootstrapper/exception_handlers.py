"""
Exception handlers for FastAPI application.

Provides consistent error responses with:
- Request ID for tracking
- Timestamp
- Consistent error structure
"""

from typing import TYPE_CHECKING

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from shared.bootstrap import create_logger
from shared.errors.exceptions import BaseException as AppBaseException
from shared.presentation.error_handler import (
    app_exception_handler,
    configure_logger,
    database_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = create_logger()


def add_exception_handlers(app: "FastAPI") -> None:
    """
    Add exception handlers to the application.

    Order matters - more specific exceptions should be registered first.
    All error responses include:
    - Consistent error structure
    - Request ID for tracking
    - Timestamp
    """
    # Configure logger for error handlers
    configure_logger(logger)

    # Application-specific exceptions (highest priority)
    app.add_exception_handler(AppBaseException, app_exception_handler)

    # Validation errors (FastAPI's request validation)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # HTTP exceptions (FastAPI's HTTPException)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Database exceptions (SQLAlchemy)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)

    # Generic catch-all (lowest priority)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("✓ Exception handlers registered")
