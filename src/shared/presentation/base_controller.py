"""Base controller with common response methods"""

from typing import Any, Dict, List, Optional, TypeVar

from fastapi import HTTPException, status

from shared.domain.result import Result
from shared.errors.error_codes import ErrorCodeRegistry

from .pagination import PaginatedResponse, PaginationParams
from .response import ApiResponse

T = TypeVar("T")


class BaseController:
    """
    Base controller with common response methods.

    Provides utilities for handling Result Pattern responses
    and converting them to HTTP responses.
    """

    @staticmethod
    def success(
        data: Any = None, message: Optional[str] = None, status_code: int = status.HTTP_200_OK
    ) -> ApiResponse:
        """
        Return success response.

        Args:
            data: Response data
            message: Optional success message
            status_code: HTTP status code

        Returns:
            ApiResponse with success=True
        """
        return ApiResponse(success=True, data=data, message=message)

    @staticmethod
    def created(data: Any, message: str = "Resource created successfully") -> ApiResponse:
        """
        Return created response (201).

        Args:
            data: Created resource data
            message: Success message

        Returns:
            ApiResponse with created data
        """
        return ApiResponse(success=True, data=data, message=message)

    @staticmethod
    def no_content(message: str = "Operation completed successfully") -> ApiResponse:
        """
        Return no content response.

        Args:
            message: Success message

        Returns:
            ApiResponse with no data
        """
        return ApiResponse(success=True, data=None, message=message)

    @staticmethod
    def paginated(
        items: List[T], total: int, params: PaginationParams
    ) -> ApiResponse[PaginatedResponse[T]]:
        """
        Return paginated response.

        Args:
            items: List of items for current page
            total: Total number of items
            params: Pagination parameters

        Returns:
            ApiResponse with paginated data
        """
        paginated_data = PaginatedResponse.create(items, total, params)
        return ApiResponse(success=True, data=paginated_data)

    @staticmethod
    def from_result(result: Result[T], success_message: Optional[str] = None) -> ApiResponse[T]:
        """
        Convert Result to ApiResponse.

        Args:
            result: Result from Use Case
            success_message: Optional success message

        Returns:
            ApiResponse with data or raises HTTPException on failure
        """
        if result.is_success:
            return ApiResponse(success=True, data=result.value, message=success_message)

        # Convert Result error to HTTP exception
        registry = ErrorCodeRegistry()
        http_status = registry.get_status(result.error_code)

        raise HTTPException(
            status_code=http_status,
            detail={
                "success": False,
                "error": {
                    "code": result.error_code,
                    "message": result.error_message,
                    "details": result.error.details or {},
                },
            },
        )

    @staticmethod
    def error(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        """
        Return error response.

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application error code
            details: Additional error details

        Returns:
            ApiResponse with error details
        """
        return ApiResponse(
            success=False,
            error={
                "code": error_code or "UNKNOWN_ERROR",
                "message": message,
                "details": details or {},
            },
        )

    @staticmethod
    def handle_error(result: Result) -> None:
        """
        Handle Result failure and raise HTTPException with appropriate status code.

        Maps domain error codes to HTTP status codes using ErrorCodeRegistry.
        Use this method for consistent error handling across all controllers.

        Args:
            result: Failed Result from command/query dispatch

        Raises:
            HTTPException: With appropriate status code and error details

        Example:
            result = await command_bus.dispatch(command)
            if result.is_failure:
                return self.handle_error(result)
        """
        registry = ErrorCodeRegistry()
        http_status, _ = registry.get(result.error.code)

        # Default to 400 if error code not found in registry
        if http_status is None:
            http_status = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=http_status,
            detail={
                "success": False,
                "data": None,
                "message": None,
                "error": {
                    "code": result.error.code,
                    "message": result.error.message,
                    "details": getattr(result.error, "details", None) or {},
                },
            },
        )

    @staticmethod
    def fail(error) -> ApiResponse:
        """
        Alias for handle_error when you have the error object directly.

        Args:
            error: Error object with code and message

        Returns:
            ApiResponse with error details
        """
        return ApiResponse(
            success=False,
            error={
                "code": error.code,
                "message": error.message,
                "details": getattr(error, "details", None) or {},
            },
        )
