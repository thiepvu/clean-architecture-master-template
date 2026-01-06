"""
User Management Read Models.

Read Models are DTOs optimized for queries (read operations).
They are separate from Write Models (domain entities) and are
designed for efficient data display and API responses.

Key differences from Write Models:
- Denormalized for efficient reading
- No business logic
- May include computed/aggregated fields
- Optimized for specific UI/API needs
"""

from .user_read_models import (
    PaginatedUsersReadModel,
    UserDetailReadModel,
    UserListItemReadModel,
    UserReadModel,
)

__all__ = [
    "UserReadModel",
    "UserListItemReadModel",
    "UserDetailReadModel",
    "PaginatedUsersReadModel",
]
