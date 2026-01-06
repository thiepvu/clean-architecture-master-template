"""
Registrations - Centralized handler and event registrations.

This module orchestrates all registrations for the application:
- CQRS: Command handlers, Query handlers
- Events: Outbox events (for reconstruction), Event subscriptions (for handling)
- Error codes: Context-specific error codes

Architecture:
─────────────
bootstrapper/registrations/
├── __init__.py              # This file - register_all()
└── contexts/
    ├── __init__.py          # Collect all contexts
    ├── user_management.py   # Single file when small
    └── file_management/     # Folder when large
        ├── __init__.py
        ├── commands.py
        ├── queries.py
        ├── outbox_events.py
        └── event_subscriptions.py

Usage:
──────
from bootstrapper.registrations import register_all
register_all(container)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstrapper.containers import ApplicationContainer
    from shared.application.ports import ILogger


def register_all(container: "ApplicationContainer", logger: "ILogger") -> None:
    """
    Register all handlers and events for the application.

    This is the main entry point called from lifespan.py.
    Delegates to each context's registrations.

    Args:
        container: Application DI container
        logger: Logger instance
    """
    from .contexts import file_management, user_management

    # Get infrastructure dependencies
    infra = container.infrastructure
    command_bus = infra.command_bus()
    query_bus = infra.query_bus()
    event_bus = infra.event_bus_resolved()

    # Register each context
    user_management.register_all(
        container=container,
        command_bus=command_bus,
        query_bus=query_bus,
        event_bus=event_bus,
        logger=logger,
    )

    file_management.register_all(
        container=container,
        command_bus=command_bus,
        query_bus=query_bus,
        event_bus=event_bus,
        logger=logger,
    )

    # Log summary
    logger.info(
        f"✓ Registrations complete: "
        f"{len(command_bus.registered_commands)} commands, "
        f"{len(query_bus.registered_queries)} queries"
    )


def register_error_codes(container: "ApplicationContainer") -> None:
    """
    Register all bounded context error codes with the global registry.

    Args:
        container: Application DI container
    """
    from presentation.http.contexts.file_management import FileManagementModule
    from presentation.http.contexts.user_management import UserManagementModule

    logger = container.infrastructure.logger()

    UserManagementModule.register_error_codes(logger)
    FileManagementModule.register_error_codes(logger)

    logger.info("✓ Error codes registered")
