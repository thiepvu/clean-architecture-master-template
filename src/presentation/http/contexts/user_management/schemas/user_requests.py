"""
User Management API Request Schemas (v1).

These schemas define the API contract for incoming requests.
They are separate from Application DTOs to allow:
- Independent API versioning (v1, v2, etc.)
- Different validation rules per API version
- API-specific field naming conventions
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUserRequest(BaseModel):
    """
    Request schema for creating a new user.

    API Contract:
        POST /api/v1/users

    Example:
        {
            "email": "john@example.com",
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User email address",
        json_schema_extra={"example": "john@example.com"},
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric with underscores/hyphens)",
        json_schema_extra={"example": "johndoe"},
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's first name",
        json_schema_extra={"example": "John"},
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's last name",
        json_schema_extra={"example": "Doe"},
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and normalize to lowercase."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john@example.com",
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                }
            ]
        }
    }


class UpdateUserRequest(BaseModel):
    """
    Request schema for updating user profile.

    API Contract:
        PUT /api/v1/users/{user_id}

    Note:
        All fields are optional. Only provided fields will be updated.

    Example:
        {
            "first_name": "Johnny",
            "last_name": "Doe"
        }
    """

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's first name",
        json_schema_extra={"example": "Johnny"},
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's last name",
        json_schema_extra={"example": "Doe"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Johnny",
                    "last_name": "Doe",
                }
            ]
        }
    }


class UpdateUserEmailRequest(BaseModel):
    """
    Request schema for updating user email.

    API Contract:
        PATCH /api/v1/users/{user_id}/email

    Example:
        {
            "email": "newemail@example.com"
        }
    """

    email: EmailStr = Field(
        ...,
        description="New email address",
        json_schema_extra={"example": "newemail@example.com"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newemail@example.com",
                }
            ]
        }
    }
