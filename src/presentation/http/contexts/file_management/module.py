"""
FileManagement Context Module.

Self-registration module for the File Management bounded context.
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
from presentation.http.contexts.file_management import FileManagementModule

# Register all handlers (logger is optional)
FileManagementModule.register_error_codes(logger)
FileManagementModule.register_cqrs_handlers(command_bus, query_bus, container, logger)
"""

from typing import Any, Optional

from shared.application.ports import ICommandBus, ILogger, IQueryBus


class FileManagementModule:
    """
    File Management Context Module.

    Encapsulates all registration logic for the File Management context.
    Bootstrapper calls these methods to integrate the context.

    Uses Composition metadata for handler registrations,
    ensuring single source of truth.
    """

    # =========================================================================
    # Error Codes Registration (Domain Layer)
    # =========================================================================

    @staticmethod
    def register_error_codes(logger: Optional[ILogger] = None) -> None:
        """Register File Management error codes with global registry."""
        from contexts.file_management.domain import register_file_error_codes

        register_file_error_codes()
        if logger:
            logger.debug("File Management error codes registered")

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
        Register Command and Query handlers for File Management.

        Uses Composition metadata for handler mappings (single source of truth).

        Args:
            command_bus: Command bus instance
            query_bus: Query bus instance
            container: DI container for resolving handlers
            logger: Optional logger for debug output
        """
        # Import composition metadata (single source of truth)
        from contexts.file_management.composition import FileManagementComposition

        # Register Command Handlers from composition
        for command_type, handler_type in FileManagementComposition.COMMAND_HANDLERS.items():
            provider_name = FileManagementComposition.get_handler_provider_name(handler_type)
            handler = getattr(container.file_management, provider_name)()
            command_bus.register(command_type, handler)

        # Register Query Handlers from composition
        for query_type, handler_type in FileManagementComposition.QUERY_HANDLERS.items():
            provider_name = FileManagementComposition.get_handler_provider_name(handler_type)
            handler = getattr(container.file_management, provider_name)()
            query_bus.register(query_type, handler)

        if logger:
            logger.debug(
                f"File Management CQRS handlers registered: "
                f"{len(FileManagementComposition.COMMAND_HANDLERS)} commands, "
                f"{len(FileManagementComposition.QUERY_HANDLERS)} queries"
            )
