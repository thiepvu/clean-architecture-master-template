"""
User Management context registrations.

All registrations for the User Management bounded context:
- Commands: Command handlers for CQRS
- Queries: Query handlers for CQRS
- Outbox Events: Domain events for Outbox reconstruction
- Event Subscriptions: Event handlers for Event Bus

When this file grows too large, convert to a folder:
user_management/
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
    Register command handlers for User Management.

    Uses Composition metadata for handler mappings (single source of truth).
    """
    from contexts.user_management.composition import UserManagementComposition

    for command_type, handler_type in UserManagementComposition.COMMAND_HANDLERS.items():
        provider_name = UserManagementComposition.get_handler_provider_name(handler_type)
        handler = getattr(container.user_management, provider_name)()
        command_bus.register(command_type, handler)

    logger.debug(
        f"User Management: {len(UserManagementComposition.COMMAND_HANDLERS)} commands registered"
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
    Register query handlers for User Management.

    Uses Composition metadata for handler mappings (single source of truth).
    """
    from contexts.user_management.composition import UserManagementComposition

    for query_type, handler_type in UserManagementComposition.QUERY_HANDLERS.items():
        provider_name = UserManagementComposition.get_handler_provider_name(handler_type)
        handler = getattr(container.user_management, provider_name)()
        query_bus.register(query_type, handler)

    logger.debug(
        f"User Management: {len(UserManagementComposition.QUERY_HANDLERS)} queries registered"
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
    from contexts.user_management.domain import (
        UserActivatedEvent,
        UserCreatedEvent,
        UserDeactivatedEvent,
        UserProfileCreatedEvent,
        UserProfilePhotoUpdatedEvent,
        UserProfileSettingsUpdatedEvent,
        UserProfileUpdatedEvent,
        UserUpdatedEvent,
    )
    from infrastructure.outbox import DomainEventFactory

    events = [
        # User events
        UserCreatedEvent,
        UserUpdatedEvent,
        UserActivatedEvent,
        UserDeactivatedEvent,
        # UserProfile events
        UserProfileCreatedEvent,
        UserProfileUpdatedEvent,
        UserProfilePhotoUpdatedEvent,
        UserProfileSettingsUpdatedEvent,
    ]

    DomainEventFactory.register_many(events)

    logger.debug(f"User Management: {len(events)} outbox events registered")


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

    Subscriptions:
    - UserCreatedEvent -> SendWelcomeEmailHandler (uses NotificationService)
    - UserProfilePhotoUpdatedEvent -> ProcessAvatarHandler (uses StorageService, JobService)
    """
    from contexts.user_management.application.event_handlers import (
        ProcessAvatarHandler,
        SendWelcomeEmailHandler,
    )
    from contexts.user_management.domain import UserCreatedEvent, UserProfilePhotoUpdatedEvent

    # Get services from container
    notification_service = container.infrastructure.notification_service_resolved()
    storage_service = container.infrastructure.storage_service_resolved()
    job_service = container.infrastructure.job_service_resolved()

    # Create handlers with dependencies
    send_welcome_email_handler = SendWelcomeEmailHandler(
        notification_service=notification_service,
        logger=logger,
    )
    process_avatar_handler = ProcessAvatarHandler(
        storage_service=storage_service,
        job_service=job_service,
        logger=logger,
    )

    # Subscribe handlers to events
    event_bus.subscribe(UserCreatedEvent, send_welcome_email_handler)
    event_bus.subscribe(UserProfilePhotoUpdatedEvent, process_avatar_handler)

    logger.debug("User Management: 2 event subscriptions registered")


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
    Register all handlers and events for User Management context.

    This is the main entry point called from bootstrapper/registrations.
    """
    register_commands(command_bus, container, logger)
    register_queries(query_bus, container, logger)
    register_outbox_events(logger)
    register_event_subscriptions(event_bus, container, logger)
