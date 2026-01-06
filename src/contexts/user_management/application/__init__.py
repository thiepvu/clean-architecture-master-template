"""
User Management Application Layer.

Contains:
- commands/ - Command handlers (write operations)
- queries/ - Query handlers (read operations)
- dto/ - Data transfer objects
- read_models/ - Read models for queries
- ports/ - Port interfaces
"""

from .commands import (
    ActivateUserCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from .dto import UserCreateDTO, UserListResponseDTO, UserResponseDTO, UserUpdateDTO
from .ports import (
    IUserManagementUoW,
    IUserManagementUoWFactory,
    IUserReadRepository,
    IUserRepository,
)
from .queries import GetUserByEmailQuery, GetUserByIdQuery, GetUserByUsernameQuery, ListUsersQuery
from .read_models import (
    PaginatedUsersReadModel,
    UserDetailReadModel,
    UserListItemReadModel,
    UserReadModel,
)

__all__ = [
    # Commands
    "CreateUserCommand",
    "UpdateUserCommand",
    "DeleteUserCommand",
    "ActivateUserCommand",
    "DeactivateUserCommand",
    # Queries
    "GetUserByIdQuery",
    "GetUserByEmailQuery",
    "GetUserByUsernameQuery",
    "ListUsersQuery",
    # DTOs
    "UserCreateDTO",
    "UserUpdateDTO",
    "UserResponseDTO",
    "UserListResponseDTO",
    # Read Models
    "UserReadModel",
    "UserListItemReadModel",
    "UserDetailReadModel",
    "PaginatedUsersReadModel",
    # Ports
    "IUserRepository",
    "IUserReadRepository",
    "IUserManagementUoW",
    "IUserManagementUoWFactory",
]
