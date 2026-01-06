"""
File Management context registrations.

All registrations for the File Management bounded context:
- Commands: Command handlers for CQRS
- Queries: Query handlers for CQRS
- Outbox Events: Domain events for Outbox reconstruction
- Event Subscriptions: Event handlers for Event Bus

When this file grows too large, convert to a folder:
file_management/
├── __init__.py
├── commands.py
├── queries.py
├── outbox_events.py
└── event_subscriptions.py
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shared.application.ports import ICommandBus, IEventBus, ILogger, IQueryBus


# =============================================================================
# Commands Registration
# =============================================================================


def register_commands(
    command_bus: "ICommandBus",
    container: Any,
    logger: "ILogger",
) -> None:
    """
    Register command handlers for File Management.

    Uses Composition metadata for handler mappings (single source of truth).
    """
    from contexts.file_management.composition import FileManagementComposition

    for command_type, handler_type in FileManagementComposition.COMMAND_HANDLERS.items():
        provider_name = FileManagementComposition.get_handler_provider_name(handler_type)
        handler = getattr(container.file_management, provider_name)()
        command_bus.register(command_type, handler)

    logger.debug(
        f"File Management: {len(FileManagementComposition.COMMAND_HANDLERS)} commands registered"
    )


# =============================================================================
# Queries Registration
# =============================================================================


def register_queries(
    query_bus: "IQueryBus",
    container: Any,
    logger: "ILogger",
) -> None:
    """
    Register query handlers for File Management.

    Uses Composition metadata for handler mappings (single source of truth).
    """
    from contexts.file_management.composition import FileManagementComposition

    for query_type, handler_type in FileManagementComposition.QUERY_HANDLERS.items():
        provider_name = FileManagementComposition.get_handler_provider_name(handler_type)
        handler = getattr(container.file_management, provider_name)()
        query_bus.register(query_type, handler)

    logger.debug(
        f"File Management: {len(FileManagementComposition.QUERY_HANDLERS)} queries registered"
    )


# =============================================================================
# Outbox Events Registration (for reconstruction)
# =============================================================================


def register_outbox_events(logger: "ILogger") -> None:
    """
    Register domain events with DomainEventFactory for Outbox reconstruction.

    These are the event types that can be stored in the outbox table
    and need to be reconstructed when publishing.
    """
    from contexts.file_management.domain import (
        FileDeletedEvent,
        FileDownloadedEvent,
        FileSharedEvent,
        FileUpdatedEvent,
        FileUploadedEvent,
    )
    from infrastructure.outbox import DomainEventFactory

    events = [
        FileUploadedEvent,
        FileUpdatedEvent,
        FileDeletedEvent,
        FileSharedEvent,
        FileDownloadedEvent,
    ]

    DomainEventFactory.register_many(events)

    logger.debug(f"File Management: {len(events)} outbox events registered")


# =============================================================================
# Event Subscriptions (Event Bus handlers)
# =============================================================================


def register_event_subscriptions(
    event_bus: "IEventBus",
    container: Any,
    logger: "ILogger",
) -> None:
    """
    Subscribe event handlers to the Event Bus.

    These handlers are invoked when domain events are published.

    Cross-Context Integration:
    - UserCreatedEvent (from User Management) -> CreateUserStorageHandler
      This creates default storage quota when a new user is created.
      Uses IStorageService to create user's folder structure.
    """
    from contexts.file_management.application.event_handlers import CreateUserStorageHandler
    from contexts.user_management.domain import UserCreatedEvent

    # Get storage service from container
    storage_service = container.infrastructure.storage_service_resolved()

    # Cross-context integration: Listen to User Management events
    # When a user is created, allocate default storage for them
    create_user_storage_handler = CreateUserStorageHandler(
        storage_service=storage_service,
        logger=logger,
    )
    event_bus.subscribe(UserCreatedEvent, create_user_storage_handler)

    logger.debug("File Management: 1 event subscription registered (cross-context)")


# =============================================================================
# Main Entry Point
# =============================================================================


def register_all(
    container: Any,
    command_bus: "ICommandBus",
    query_bus: "IQueryBus",
    event_bus: "IEventBus",
    logger: "ILogger",
) -> None:
    """
    Register all handlers and events for File Management context.

    This is the main entry point called from bootstrapper/registrations.
    """
    register_commands(command_bus, container, logger)
    register_queries(query_bus, container, logger)
    register_outbox_events(logger)
    register_event_subscriptions(event_bus, container, logger)
