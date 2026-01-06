"""
User Management DI Container - Composition Root.

Located in bootstrapper layer where it's allowed to import from ALL layers.

Clean Architecture Compliance:
─────────────────────────────
✅ Bootstrapper CAN import from Infrastructure
✅ Uses Composition metadata from context (single source of truth)
✅ Presentation receives pre-wired containers (no Infrastructure knowledge)
✅ Application/Domain layers remain pure

CQRS Pattern:
─────────────
- Commands -> CommandHandlers -> UoW (owns repositories)
- Queries -> QueryHandlers -> Read Repository
"""

from typing import Any

from dependency_injector import containers, providers

# Composition metadata - single source of truth for handlers
from contexts.user_management.composition import UserManagementComposition

# Get handler types from composition (cleaner than direct imports)
_cmd_handlers = UserManagementComposition.COMMAND_HANDLERS
_query_handlers = UserManagementComposition.QUERY_HANDLERS

# Infrastructure Adapters (Composition Root - only bootstrapper imports these)
from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.repositories.user_read_repository import (
    UserReadRepository,
)
from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.unit_of_work import (
    UserManagementUoWFactory,
)


# Helper to get handler type by command/query name
def _get_handler(handlers: dict, name: str):
    """Get handler type from composition by command/query name."""
    for cmd_type, handler_type in handlers.items():
        if cmd_type.__name__ == name:
            return handler_type
    raise KeyError(f"Handler for {name} not found in composition")


class UserManagementContainer(containers.DeclarativeContainer):
    """
    DI Container for User Management bounded context.

    CQRS Structure:
    - Write Side: Commands -> CommandHandlers -> UoW (owns repositories)
    - Read Side: Queries -> QueryHandlers -> Read Repository

    Handler types are obtained from UserManagementComposition,
    keeping this container focused on infrastructure wiring only.
    """

    # =========================================================================
    # Dependencies (injected from ApplicationContainer)
    # =========================================================================
    session_factory: Any = providers.Dependency()
    event_bus: Any = providers.Dependency()
    cache_service: Any = providers.Dependency()  # Optional, for caching queries
    logger: Any = providers.Dependency()

    # =========================================================================
    # Infrastructure Wiring (Bootstrapper's responsibility)
    # =========================================================================

    # Unit of Work Factory (for Commands)
    uow_factory = providers.Singleton(
        UserManagementUoWFactory,
        session_factory=session_factory,
        event_bus=event_bus,
        logger=logger,
    )

    # Read Repository (for Queries)
    user_read_repository = providers.Factory(
        UserReadRepository,
        session_factory=session_factory,
    )

    # =========================================================================
    # Command Handlers (types from Composition)
    # =========================================================================
    create_user_handler = providers.Factory(
        _get_handler(_cmd_handlers, "CreateUserCommand"),
        uow_factory=uow_factory,
    )

    update_user_handler = providers.Factory(
        _get_handler(_cmd_handlers, "UpdateUserCommand"),
        uow_factory=uow_factory,
        cache_service=cache_service,  # For cache invalidation on update
    )

    delete_user_handler = providers.Factory(
        _get_handler(_cmd_handlers, "DeleteUserCommand"),
        uow_factory=uow_factory,
    )

    activate_user_handler = providers.Factory(
        _get_handler(_cmd_handlers, "ActivateUserCommand"),
        uow_factory=uow_factory,
    )

    deactivate_user_handler = providers.Factory(
        _get_handler(_cmd_handlers, "DeactivateUserCommand"),
        uow_factory=uow_factory,
    )

    # =========================================================================
    # Query Handlers (types from Composition)
    # =========================================================================
    get_user_by_id_handler = providers.Factory(
        _get_handler(_query_handlers, "GetUserByIdQuery"),
        read_repository=user_read_repository,
        cache_service=cache_service,  # Optional cache for cache-aside pattern
    )

    get_user_by_email_handler = providers.Factory(
        _get_handler(_query_handlers, "GetUserByEmailQuery"),
        read_repository=user_read_repository,
    )

    get_user_by_username_handler = providers.Factory(
        _get_handler(_query_handlers, "GetUserByUsernameQuery"),
        read_repository=user_read_repository,
    )

    list_users_handler = providers.Factory(
        _get_handler(_query_handlers, "ListUsersQuery"),
        read_repository=user_read_repository,
    )
