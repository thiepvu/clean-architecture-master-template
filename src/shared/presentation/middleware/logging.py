"""
Request Logging Middleware.

Provides structured logging for HTTP requests and responses.
"""

import time
from typing import TYPE_CHECKING, Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from .request_context import get_request_context

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Features:
    - Logs request start with method, path, and request ID
    - Logs response with status code and duration
    - Excludes health check endpoints to reduce noise
    - Includes request context (request_id, correlation_id)

    Usage:
        app.add_middleware(RequestLoggingMiddleware, logger=logger_instance)
    """

    # Paths to exclude from logging (reduce noise)
    EXCLUDED_PATHS = {"/health", "/metrics", "/favicon.ico"}

    def __init__(self, app, logger: "ILogger"):
        """
        Initialize middleware with logger.

        Args:
            app: Starlette/FastAPI application
            logger: Logger instance (injected via DI)
        """
        super().__init__(app)
        self._logger = logger

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process and log the request."""
        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Get request context
        ctx = get_request_context()
        request_id = ctx.request_id if ctx else "unknown"

        # Log request start
        self._logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

        # Track timing
        start_time = time.perf_counter()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            log_level = "info" if response.status_code < 400 else "warning"
            log_method = getattr(self._logger, log_level)

            log_method(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

            return response

        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000

            self._logger.error(
                f"Request failed: {request.method} {request.url.path} - {type(e).__name__}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check X-Forwarded-For header (when behind proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"
