"""
User Management Composition Root Exports.

This module defines what the context needs for DI wiring.
Bootstrapper imports from here instead of knowing internal implementation details.

Clean Architecture:
───────────────────
- Context defines WHAT it needs (handlers, dependencies)
- Bootstrapper decides HOW to wire them (infrastructure adapters)
- Single source of truth for handler registrations (CQRS only)

Usage:
──────
from contexts.user_management.composition import UserManagementComposition

# Get handler mappings
for cmd_type, handler_type in UserManagementComposition.COMMAND_HANDLERS.items():
    command_bus.register(cmd_type, container.resolve(handler_type))
"""

from typing import Any, Dict, List, Type

# Commands & Handlers
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

# Queries & Handlers
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


class UserManagementComposition:
    """
    Composition metadata for User Management bounded context.

    Bootstrapper uses this to wire dependencies without knowing
    implementation details of each handler.

    Currently follows CQRS pattern only (Commands & Queries).

    Benefits:
    - Single source of truth for registrations
    - Easy to add/remove handlers
    - Bootstrapper doesn't need to know internal imports
    - Testable (can mock composition for testing)
    """

    # =========================================================================
    # Context Identifier
    # =========================================================================
    CONTEXT_NAME = "user_management"

    # =========================================================================
    # Command Handlers Mapping
    # Command Type -> Handler Type
    # =========================================================================
    COMMAND_HANDLERS: Dict[Type, Type[Any]] = {
        CreateUserCommand: CreateUserHandler,
        UpdateUserCommand: UpdateUserHandler,
        DeleteUserCommand: DeleteUserHandler,
        ActivateUserCommand: ActivateUserHandler,
        DeactivateUserCommand: DeactivateUserHandler,
    }

    # =========================================================================
    # Query Handlers Mapping
    # Query Type -> Handler Type
    # =========================================================================
    QUERY_HANDLERS: Dict[Type, Type[Any]] = {
        GetUserByIdQuery: GetUserByIdHandler,
        GetUserByEmailQuery: GetUserByEmailHandler,
        GetUserByUsernameQuery: GetUserByUsernameHandler,
        ListUsersQuery: ListUsersHandler,
    }

    # =========================================================================
    # Handler Provider Names (for container access)
    # Maps handler type to container provider name
    # =========================================================================
    HANDLER_PROVIDERS: Dict[Type, str] = {
        # Command Handlers
        CreateUserHandler: "create_user_handler",
        UpdateUserHandler: "update_user_handler",
        DeleteUserHandler: "delete_user_handler",
        ActivateUserHandler: "activate_user_handler",
        DeactivateUserHandler: "deactivate_user_handler",
        # Query Handlers
        GetUserByIdHandler: "get_user_by_id_handler",
        GetUserByEmailHandler: "get_user_by_email_handler",
        GetUserByUsernameHandler: "get_user_by_username_handler",
        ListUsersHandler: "list_users_handler",
    }

    @classmethod
    def get_handler_provider_name(cls, handler_type: Type) -> str:
        """Get container provider name for a handler type."""
        return cls.HANDLER_PROVIDERS.get(handler_type, "")

    @classmethod
    def get_all_command_types(cls) -> List[Type]:
        """Get all command types for this context."""
        return list(cls.COMMAND_HANDLERS.keys())

    @classmethod
    def get_all_query_types(cls) -> List[Type]:
        """Get all query types for this context."""
        return list(cls.QUERY_HANDLERS.keys())
