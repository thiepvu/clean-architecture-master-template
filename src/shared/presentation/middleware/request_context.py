"""
Request Context Middleware.

Provides request tracking with unique IDs and context storage.
Uses ContextVar for async-safe access across the request lifecycle.
"""

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Header names
REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"


@dataclass
class RequestContext:
    """
    Request context data.

    Stores information about the current request that can be accessed
    anywhere in the request lifecycle.
    """

    request_id: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    path: str = ""
    method: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Calculate request duration in milliseconds."""
        delta = datetime.utcnow() - self.started_at
        return delta.total_seconds() * 1000


# ContextVar for storing request context
_request_context: ContextVar[Optional[RequestContext]] = ContextVar("request_context", default=None)


def get_request_context() -> Optional[RequestContext]:
    """
    Get the current request context.

    Returns:
        RequestContext if inside a request, None otherwise
    """
    return _request_context.get()


def get_request_id() -> Optional[str]:
    """
    Get the current request ID.

    Returns:
        Request ID string if inside a request, None otherwise
    """
    ctx = _request_context.get()
    return ctx.request_id if ctx else None


def set_request_context(context: RequestContext) -> None:
    """Set the request context."""
    _request_context.set(context)


def clear_request_context() -> None:
    """Clear the request context."""
    _request_context.set(None)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that creates and manages request context.

    Features:
    - Generates unique request ID for each request
    - Accepts external correlation ID for distributed tracing
    - Stores context in ContextVar for async-safe access
    - Adds request ID to response headers

    Usage:
        app.add_middleware(RequestContextMiddleware)

        # Access anywhere in request lifecycle:
        from shared.presentation.middleware import get_request_id
        request_id = get_request_id()
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request with context tracking."""
        # Generate or extract request ID
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Extract correlation ID (for distributed tracing)
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)

        # Create request context
        context = RequestContext(
            request_id=request_id,
            correlation_id=correlation_id,
            path=str(request.url.path),
            method=request.method,
        )

        # Store in ContextVar
        token = _request_context.set(context)

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers[REQUEST_ID_HEADER] = request_id
            if correlation_id:
                response.headers[CORRELATION_ID_HEADER] = correlation_id

            return response

        finally:
            # Clear context
            _request_context.reset(token)
