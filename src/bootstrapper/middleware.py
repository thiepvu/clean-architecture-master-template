"""
Middleware configuration for FastAPI application.

Handles:
- CORS configuration
- GZip compression
- Request logging
- Request context (request ID)
"""

from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from shared.application.ports import IConfigService
from shared.bootstrap import create_logger
from shared.presentation.middleware import RequestContextMiddleware, RequestLoggingMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = create_logger()


def add_middlewares(app: "FastAPI", config_service: IConfigService) -> None:
    """
    Add middleware to the application.

    Note: Middleware are executed in reverse order of addition.
    The last middleware added is executed first on request,
    and last on response.

    Order of execution (request → response):
    1. RequestContextMiddleware (sets request ID)
    2. RequestLoggingMiddleware (logs request/response)
    3. GZipMiddleware (compresses response)
    4. CORSMiddleware (handles CORS)
    """
    cors_config = config_service.cors

    # CORS middleware (executed first on response, last on request)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.CORS_ORIGINS,
        allow_credentials=cors_config.CORS_CREDENTIALS,
        allow_methods=cors_config.CORS_METHODS,
        allow_headers=cors_config.CORS_HEADERS,
    )
    logger.info("✓ CORS middleware added")

    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✓ GZip middleware added")

    # Request logging middleware (logs request/response with timing)
    app.add_middleware(RequestLoggingMiddleware, logger=logger)
    logger.info("✓ Request logging middleware added")

    # Request context middleware (sets request ID - must be first on request)
    app.add_middleware(RequestContextMiddleware)
    logger.info("✓ Request context middleware added")
