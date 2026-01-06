"""
User Management API Schemas (v1).

Presentation layer schemas for API request/response validation.
These are separate from Application DTOs to allow independent API versioning.

Structure:
- Request schemas: Validate incoming API requests
- Response schemas: Define API response structure (uses Read Models)
"""

from .user_requests import CreateUserRequest, UpdateUserEmailRequest, UpdateUserRequest

__all__ = [
    # Request schemas
    "CreateUserRequest",
    "UpdateUserRequest",
    "UpdateUserEmailRequest",
]
