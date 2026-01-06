"""
User Management Bounded Context.

Public API for the User Management context.
Other layers should import from here, not from internal modules.

This module provides a clean public API following the Barrel Export pattern:
- Commands & Queries (CQRS operations)
- Read Models (query results)
- DTOs (data transfer objects)
- Domain entities, value objects, events, exceptions
- Ports (interfaces for repositories/services)
- Facades (anti-corruption layer for cross-BC communication)
- Composition metadata (for DI wiring)

Usage:
──────
# Basic usage (commands, queries, read models)
from contexts.user_management import (
    CreateUserCommand,
    GetUserByIdQuery,
    UserReadModel,
)

# Domain layer access
from contexts.user_management.domain import User, Email, UserCreatedEvent

# Application layer access
from contexts.user_management.application import (
    IUserRepository,
    UserManagementFacade,
)

# Composition metadata (for bootstrapper)
from contexts.user_management.composition import UserManagementComposition
"""

# =============================================================================
# Commands (Public API)
# =============================================================================
from .application.commands import (
    ActivateUserCommand,
    ActivateUserHandler,
    CreateUserCommand,
    CreateUserHandler,
    DeactivateUserCommand,
    DeactivateUserHandler,
    DeleteUserCommand,
    DeleteUserHandler,
    UpdateUserCommand,
    UpdateUserHandler,
)

# =============================================================================
# DTOs (Public API)
# =============================================================================
from .application.dto import UserCreateDTO, UserListResponseDTO, UserResponseDTO, UserUpdateDTO

# =============================================================================
# Ports (Interfaces)
# =============================================================================
from .application.ports import (
    IUserManagementUoW,
    IUserManagementUoWFactory,
    IUserReadRepository,
    IUserRepository,
)

# =============================================================================
# Queries (Public API)
# =============================================================================
from .application.queries import (
    GetUserByEmailHandler,
    GetUserByEmailQuery,
    GetUserByIdHandler,
    GetUserByIdQuery,
    GetUserByUsernameHandler,
    GetUserByUsernameQuery,
    ListUsersHandler,
    ListUsersQuery,
)

# =============================================================================
# Read Models (Public API)
# =============================================================================
from .application.read_models import (
    PaginatedUsersReadModel,
    UserDetailReadModel,
    UserListItemReadModel,
    UserReadModel,
)

# =============================================================================
# Composition Metadata (for DI wiring)
# =============================================================================
from .composition import UserManagementComposition

# =============================================================================
# Domain Layer (Re-exports for convenience)
# =============================================================================
from .domain import (  # Entity; Value Objects; Events; Errors; Exceptions
    Email,
    InvalidEmailException,
    InvalidUserStateException,
    User,
    UserActivatedEvent,
    UserAlreadyExistsException,
    UserCreatedEvent,
    UserDeactivatedEvent,
    UserErrorCode,
    UserUpdatedEvent,
    register_user_error_codes,
)

__all__ = [
    # =========================================================================
    # Commands
    # =========================================================================
    "CreateUserCommand",
    "UpdateUserCommand",
    "DeleteUserCommand",
    "ActivateUserCommand",
    "DeactivateUserCommand",
    # =========================================================================
    # Command Handlers
    # =========================================================================
    "CreateUserHandler",
    "UpdateUserHandler",
    "DeleteUserHandler",
    "ActivateUserHandler",
    "DeactivateUserHandler",
    # =========================================================================
    # Queries
    # =========================================================================
    "GetUserByIdQuery",
    "GetUserByEmailQuery",
    "GetUserByUsernameQuery",
    "ListUsersQuery",
    # =========================================================================
    # Query Handlers
    # =========================================================================
    "GetUserByIdHandler",
    "GetUserByEmailHandler",
    "GetUserByUsernameHandler",
    "ListUsersHandler",
    # =========================================================================
    # Read Models
    # =========================================================================
    "UserReadModel",
    "UserListItemReadModel",
    "UserDetailReadModel",
    "PaginatedUsersReadModel",
    # =========================================================================
    # DTOs
    # =========================================================================
    "UserCreateDTO",
    "UserUpdateDTO",
    "UserResponseDTO",
    "UserListResponseDTO",
    # =========================================================================
    # Ports
    # =========================================================================
    "IUserRepository",
    "IUserReadRepository",
    "IUserManagementUoW",
    "IUserManagementUoWFactory",
    # =========================================================================
    # Composition Metadata
    # =========================================================================
    "UserManagementComposition",
    # =========================================================================
    # Domain - Entity
    # =========================================================================
    "User",
    # =========================================================================
    # Domain - Value Objects
    # =========================================================================
    "Email",
    # =========================================================================
    # Domain - Events
    # =========================================================================
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserActivatedEvent",
    "UserDeactivatedEvent",
    # =========================================================================
    # Domain - Errors
    # =========================================================================
    "UserErrorCode",
    "register_user_error_codes",
    # =========================================================================
    # Domain - Exceptions
    # =========================================================================
    "InvalidEmailException",
    "InvalidUserStateException",
    "UserAlreadyExistsException",
]
