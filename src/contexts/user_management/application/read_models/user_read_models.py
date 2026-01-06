"""
User Read Models.

These are DTOs specifically designed for read operations (queries).
They are separate from domain entities and optimized for display.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserReadModel(BaseModel):
    """
    Standard User read model for single user responses.

    This is the primary read model returned by GetUserByIdQuery.
    Contains all user information needed for display.
    """

    id: UUID = Field(..., description="User UUID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    full_name: str = Field(..., description="Full name (computed)")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        frozen = True  # Immutable
        from_attributes = True  # Allow ORM mode


class UserListItemReadModel(BaseModel):
    """
    Lightweight User read model for list views.

    Optimized for listing multiple users - contains only
    essential fields needed for list/table display.
    """

    id: UUID
    username: str
    full_name: str
    email: str
    is_active: bool

    class Config:
        frozen = True
        from_attributes = True


class UserDetailReadModel(BaseModel):
    """
    Detailed User read model with extended information.

    Used when more context is needed, such as admin views
    or user profile pages.
    """

    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    # Extended fields for detailed views
    # These could be populated from related data or computed
    # file_count: Optional[int] = None
    # last_login_at: Optional[datetime] = None

    class Config:
        frozen = True
        from_attributes = True


class PaginatedUsersReadModel(BaseModel):
    """
    Paginated list of users read model.

    Used for list queries with pagination support.
    Contains both the data and pagination metadata.
    """

    users: List[UserListItemReadModel] = Field(..., description="List of users")
    total: int = Field(..., description="Total count of users matching criteria")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    has_more: bool = Field(..., description="Whether there are more records")

    class Config:
        frozen = True

    @classmethod
    def create(
        cls,
        users: List[UserListItemReadModel],
        total: int,
        skip: int,
        limit: int,
    ) -> "PaginatedUsersReadModel":
        """
        Factory method to create paginated result.

        Args:
            users: List of user read models
            total: Total count
            skip: Records skipped
            limit: Max records

        Returns:
            PaginatedUsersReadModel instance
        """
        return cls(
            users=users,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(users)) < total,
        )
