"""
Standard API Response Models.

Provides consistent response structures for all API endpoints.
All responses include:
- Success status
- Request ID for tracking
- Timestamp
- Data or error information
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.

    Usage:
        # Success response
        return ApiResponse.ok(data=user, message="User created")

        # With request ID (from middleware)
        return ApiResponse.ok(data=user).with_request_id(request_id)

        # Paginated response
        return ApiResponse.paginated(items=users, total=100, skip=0, limit=10)
    """

    success: bool = Field(default=True, description="Request success status")
    data: Optional[T] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Response message")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> "ApiResponse[T]":
        """Create a success response."""
        return cls(success=True, data=data, message=message, request_id=request_id)

    @classmethod
    def created(
        cls,
        data: T,
        message: str = "Resource created successfully",
        request_id: Optional[str] = None,
    ) -> "ApiResponse[T]":
        """Create a 201 Created response."""
        return cls(success=True, data=data, message=message, request_id=request_id)

    @classmethod
    def no_content(
        cls,
        message: str = "Operation completed successfully",
        request_id: Optional[str] = None,
    ) -> "ApiResponse[Any]":
        """Create a success response with no data (for DELETE operations)."""
        return cls(success=True, data=None, message=message, request_id=request_id)

    def with_request_id(self, request_id: str) -> "ApiResponse[T]":
        """Add request ID to response."""
        self.request_id = request_id
        return self


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated API response.

    Usage:
        return PaginatedResponse.create(
            items=users,
            total=100,
            skip=0,
            limit=10,
            request_id=request_id
        )
    """

    success: bool = Field(default=True, description="Request success status")
    data: List[T] = Field(default_factory=list, description="List of items")
    pagination: Dict[str, int] = Field(..., description="Pagination metadata")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int,
        request_id: Optional[str] = None,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        return cls(
            success=True,
            data=items,
            pagination={
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + len(items) < total,
            },
            request_id=request_id,
        )

    def with_request_id(self, request_id: str) -> "PaginatedResponse[T]":
        """Add request ID to response."""
        self.request_id = request_id
        return self


class ErrorDetail(BaseModel):
    """Error detail model for field-level errors."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """
    Standard error response.

    Usage:
        return ErrorResponse.from_error(
            code="USER_NOT_FOUND",
            message="User not found",
            status_code=404,
            request_id=request_id
        )
    """

    success: bool = Field(default=False, description="Always false for errors")
    error: Dict[str, Any] = Field(..., description="Error information")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @classmethod
    def from_error(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "ErrorResponse":
        """Create an error response."""
        return cls(
            success=False,
            error={
                "code": code,
                "message": message,
                "details": details or {},
            },
            request_id=request_id,
        )

    @classmethod
    def validation_error(
        cls,
        errors: List[ErrorDetail],
        request_id: Optional[str] = None,
    ) -> "ErrorResponse":
        """Create a validation error response."""
        return cls(
            success=False,
            error={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": [e.model_dump() for e in errors]},
            },
            request_id=request_id,
        )

    def with_request_id(self, request_id: str) -> "ErrorResponse":
        """Add request ID to response."""
        self.request_id = request_id
        return self
