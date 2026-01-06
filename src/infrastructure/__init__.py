"""
Infrastructure Layer.

Technical concerns and adapter implementations.
All infrastructure modules follow Port & Adapter + Factory pattern.

Usage:
    # Import modules directly
    from infrastructure.cache import CacheModule
    from infrastructure.database import DatabaseModule
    from infrastructure.events import EventsModule
    from infrastructure.jobs import JobsModule
    from infrastructure.storage import StorageModule
    from infrastructure.logging import LoggingModule
    from infrastructure.config import ConfigModule

    # Or import from top-level
    from infrastructure import (
        CacheModule,
        DatabaseModule,
        EventsModule,
        JobsModule,
        StorageModule,
        LoggingModule,
        ConfigModule,
    )
"""

# Modules (primary interface for DI)
from .buses import BusesModule, CommandBusFactory, QueryBusFactory
from .cache import CacheFactory, CacheModule
from .config import ConfigModule, ConfigService
from .database import DatabaseFactory, DatabaseModule
from .events import EventBusFactory, EventsModule
from .jobs import JobsFactory, JobsModule
from .logging import LoggingModule
from .notification import (
    InMemoryNotificationAdapter,
    NotificationFactory,
    NotificationModule,
    NovuNotificationAdapter,
)

# Outbox pattern
from .outbox import (
    DomainEventFactory,
    OutboxEvent,
    OutboxEventPublisher,
    OutboxProcessor,
    OutboxProcessorConfig,
    OutboxProcessorFactory,
)
from .storage import LocalStorageAdapter, S3StorageAdapter, StorageFactory, StorageModule

__all__ = [
    # =========================================================================
    # Modules (primary interface for DI container)
    # =========================================================================
    "BusesModule",
    "CacheModule",
    "DatabaseModule",
    "EventsModule",
    "JobsModule",
    "StorageModule",
    "NotificationModule",
    "LoggingModule",
    "ConfigModule",
    "ConfigService",
    # =========================================================================
    # Factories (for direct creation if needed)
    # Note: AdapterType enums are in config/types, not here
    # =========================================================================
    "CacheFactory",
    "DatabaseFactory",
    "EventBusFactory",
    "JobsFactory",
    "StorageFactory",
    "NotificationFactory",
    "CommandBusFactory",
    "QueryBusFactory",
    # =========================================================================
    # Storage Adapters
    # =========================================================================
    "LocalStorageAdapter",
    "S3StorageAdapter",
    # =========================================================================
    # Notification Adapters
    # =========================================================================
    "InMemoryNotificationAdapter",
    "NovuNotificationAdapter",
    # =========================================================================
    # Outbox Pattern
    # =========================================================================
    "OutboxProcessor",
    "OutboxProcessorConfig",
    "OutboxProcessorFactory",
    "OutboxEvent",
    "OutboxEventPublisher",
    "DomainEventFactory",
]
