"""
Shared error handling for Clean Architecture.

Provides both:
- Result Pattern (preferred for expected errors)
- Exception classes (for unexpected errors and framework integration)
"""

from .error_codes import ErrorCode
from .exceptions import (
    BadRequestException,
    BaseException,
    ConflictException,
    DomainException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)

__all__ = [
    "ErrorCode",
    "BaseException",
    "DomainException",
    "NotFoundException",
    "ValidationException",
    "ConflictException",
    "UnauthorizedException",
    "ForbiddenException",
    "BadRequestException",
    "InternalServerException",
]
