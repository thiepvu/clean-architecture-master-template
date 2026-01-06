"""
Result Pattern for functional error handling.
Provides a way to handle errors without exceptions.
"""

from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Error:
    """
    Error value object representing a failure.

    Attributes:
        code: Machine-readable error code (e.g., "USER_NOT_FOUND")
        message: Human-readable error message
        details: Additional error context
    """

    code: str
    message: str
    details: Optional[dict] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class Result(Generic[T]):
    """
    Result monad for functional error handling.

    Represents either a success with a value or a failure with an error.
    Use this instead of raising exceptions for expected error cases.

    Example:
        def divide(a: int, b: int) -> Result[float]:
            if b == 0:
                return Result.fail("DIVISION_BY_ZERO", "Cannot divide by zero")
            return Result.ok(a / b)

        result = divide(10, 2)
        if result.is_success:
            print(f"Result: {result.value}")
        else:
            print(f"Error: {result.error}")
    """

    def __init__(
        self,
        value: Optional[T] = None,
        error: Optional[Error] = None,
        is_success: bool = True,
    ):
        """
        Initialize Result. Use factory methods ok() and fail() instead.
        """
        self._value = value
        self._error = error
        self._is_success = is_success

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """
        Create a successful result.

        Args:
            value: The success value

        Returns:
            Result containing the success value
        """
        return cls(value=value, is_success=True)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None,
    ) -> "Result[T]":
        """
        Create a failed result.

        Args:
            code: Machine-readable error code
            message: Human-readable error message
            details: Additional error context

        Returns:
            Result containing the error
        """
        error = Error(code=code, message=message, details=details)
        return cls(error=error, is_success=False)

    @classmethod
    def from_error(cls, error: Error) -> "Result[T]":
        """
        Create a failed result from an Error object.

        Args:
            error: The Error object

        Returns:
            Result containing the error
        """
        return cls(error=error, is_success=False)

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        code: str,
        details: Optional[dict] = None,
    ) -> "Result[T]":
        """
        Create a failed result from an exception.

        Useful for converting domain exceptions to Result pattern.

        Args:
            exc: The exception to convert
            code: Error code for the result
            details: Optional additional details (if not provided,
                     will try to get from exc.details if available)

        Returns:
            Result containing the error

        Example:
            try:
                file = File.create(...)
            except FileSizeLimitExceededException as e:
                return Result.from_exception(e, FileErrorCode.FILE_SIZE_EXCEEDED.value)
        """
        # Try to get details from exception if not provided
        if details is None:
            details = getattr(exc, "details", None)

        return cls.fail(code=code, message=str(exc), details=details)

    @property
    def is_success(self) -> bool:
        """Check if result is successful"""
        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure"""
        return not self._is_success

    @property
    def value(self) -> T:
        """
        Get the success value.

        Raises:
            ValueError: If result is a failure
        """
        if not self._is_success:
            raise ValueError(f"Cannot get value from failed result: {self._error}")
        return self._value  # type: ignore

    @property
    def error(self) -> Error:
        """
        Get the error.

        Raises:
            ValueError: If result is successful
        """
        if self._is_success:
            raise ValueError("Cannot get error from successful result")
        return self._error  # type: ignore

    @property
    def error_code(self) -> Optional[str]:
        """Get error code if failed, None otherwise"""
        return self._error.code if self._error else None

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if failed, None otherwise"""
        return self._error.message if self._error else None

    def value_or(self, default: T) -> T:
        """
        Get value or return default if failed.

        Args:
            default: Default value to return if failed

        Returns:
            The success value or the default
        """
        return self._value if self._is_success else default  # type: ignore

    def value_or_raise(self, exception_class: type = ValueError) -> T:
        """
        Get value or raise exception if failed.

        Args:
            exception_class: Exception class to raise

        Returns:
            The success value

        Raises:
            exception_class: If result is a failure
        """
        if not self._is_success:
            raise exception_class(str(self._error))
        return self._value  # type: ignore

    def map(self, func: Callable[[T], U]) -> "Result[U]":
        """
        Transform the success value.

        Args:
            func: Function to apply to the value

        Returns:
            New Result with transformed value or same error
        """
        if self._is_success:
            return Result.ok(func(self._value))  # type: ignore
        return Result.from_error(self._error)  # type: ignore

    def flat_map(self, func: Callable[[T], "Result[U]"]) -> "Result[U]":
        """
        Chain Result-returning operations.

        Args:
            func: Function that returns a Result

        Returns:
            Result from the function or same error
        """
        if self._is_success:
            return func(self._value)  # type: ignore
        return Result.from_error(self._error)  # type: ignore

    def on_success(self, func: Callable[[T], None]) -> "Result[T]":
        """
        Execute function if successful (for side effects).

        Args:
            func: Function to execute on success

        Returns:
            Self for chaining
        """
        if self._is_success:
            func(self._value)  # type: ignore
        return self

    def on_failure(self, func: Callable[[Error], None]) -> "Result[T]":
        """
        Execute function if failed (for side effects).

        Args:
            func: Function to execute on failure

        Returns:
            Self for chaining
        """
        if not self._is_success:
            func(self._error)  # type: ignore
        return self

    def __repr__(self) -> str:
        if self._is_success:
            return f"Result.ok({self._value!r})"
        return f"Result.fail({self._error!r})"

    def __bool__(self) -> bool:
        """Allow using Result in boolean context"""
        return self._is_success


def combine_results(*results: Result) -> Result[tuple]:
    """
    Combine multiple Results into one.

    If all succeed, returns Result with tuple of values.
    If any fails, returns first failure.

    Args:
        *results: Results to combine

    Returns:
        Combined Result
    """
    values = []
    for result in results:
        if result.is_failure:
            return Result.from_error(result.error)
        values.append(result.value)
    return Result.ok(tuple(values))
