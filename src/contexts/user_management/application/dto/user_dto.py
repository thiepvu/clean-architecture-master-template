"""User Data Transfer Objects"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from shared.application.dto import DTO


class UserCreateDTO(DTO):
    """User creation DTO"""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username (3-50 characters)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()


class UserUpdateDTO(DTO):
    """User update DTO"""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")


class UserEmailUpdateDTO(DTO):
    """User email update DTO"""

    email: EmailStr = Field(..., description="New email address")


class UserResponseDTO(DTO):
    """User response DTO"""

    id: UUID = Field(..., description="User UUID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    full_name: str = Field(..., description="Full name")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserListResponseDTO(DTO):
    """User list item DTO (minimal info)"""

    id: UUID
    username: str
    full_name: str
    email: str
    is_active: bool
