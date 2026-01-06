"""
UserManagement Context Module.

Self-registration module for the User Management bounded context.
This is the single entry point for bootstrapper to integrate this context.

Responsibilities:
- Register error codes (domain layer)
- Register CQRS handlers (application layer)

Architecture:
─────────────
Bootstrapper only needs to know about this module.
All internal details (commands, queries, handlers) are encapsulated.

Clean Architecture:
───────────────────
- Uses Composition metadata from context (single source of truth)
- Logger is passed as parameter (DI) instead of imported from bootstrap
- Follows CQRS pattern only (Commands & Queries)

Usage:
──────
from presentation.http.contexts.user_management import UserManagementModule

# Register all handlers (logger is optional)
UserManagementModule.register_error_codes(logger)
UserManagementModule.register_cqrs_handlers(command_bus, query_bus, container, logger)
"""

from typing import Any, Optional

from shared.application.ports import ICommandBus, ILogger, IQueryBus


class UserManagementModule:
    """
    User Management Context Module.

    Encapsulates all registration logic for the User Management context.
    Bootstrapper calls these methods to integrate the context.

    Uses Composition metadata for handler registrations,
    ensuring single source of truth.
    """

    # =========================================================================
    # Error Codes Registration (Domain Layer)
    # =========================================================================

    @staticmethod
    def register_error_codes(logger: Optional[ILogger] = None) -> None:
        """Register User Management error codes with global registry."""
        from contexts.user_management.domain import register_user_error_codes

        register_user_error_codes()
        if logger:
            logger.debug("User Management error codes registered")

    # =========================================================================
    # CQRS Handlers Registration (Application Layer)
    # =========================================================================

    @staticmethod
    def register_cqrs_handlers(
        command_bus: ICommandBus,
        query_bus: IQueryBus,
        container: Any,
        logger: Optional[ILogger] = None,
    ) -> None:
        """
        Register Command and Query handlers for User Management.

        Uses Composition metadata for handler mappings (single source of truth).

        Args:
            command_bus: Command bus instance
            query_bus: Query bus instance
            container: DI container for resolving handlers
            logger: Optional logger for debug output
        """
        # Import composition metadata (single source of truth)
        from contexts.user_management.composition import UserManagementComposition

        # Register Command Handlers from composition
        for command_type, handler_type in UserManagementComposition.COMMAND_HANDLERS.items():
            provider_name = UserManagementComposition.get_handler_provider_name(handler_type)
            handler = getattr(container.user_management, provider_name)()
            command_bus.register(command_type, handler)

        # Register Query Handlers from composition
        for query_type, handler_type in UserManagementComposition.QUERY_HANDLERS.items():
            provider_name = UserManagementComposition.get_handler_provider_name(handler_type)
            handler = getattr(container.user_management, provider_name)()
            query_bus.register(query_type, handler)

        if logger:
            logger.debug(
                f"User Management CQRS handlers registered: "
                f"{len(UserManagementComposition.COMMAND_HANDLERS)} commands, "
                f"{len(UserManagementComposition.QUERY_HANDLERS)} queries"
            )
