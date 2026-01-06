"""
Infrastructure DI Container.

Contains all infrastructure dependencies with factory pattern.
Uses adapter pattern for swappable implementations.

Architecture:
─────────────
DI Container is the SOLE owner of singleton lifecycle.
Modules (ConfigModule, LoggingModule) are pure composers - they create instances
but do NOT manage singletons. DI Container registers and manages all singletons.

Flow:
1. ConfigModule.create_service() → DI registers as Singleton
2. LoggingModule.create_logger(config_service) → DI registers as Singleton
3. All other factories receive dependencies via DI injection

Note: Context-specific UoW factories are created in their respective containers.
This container only provides shared infrastructure services.
"""

from dependency_injector import containers, providers

from infrastructure.buses import BusesModule
from infrastructure.cache import CacheModule
from infrastructure.config import ConfigModule
from infrastructure.database import DatabaseModule
from infrastructure.events import EventsModule
from infrastructure.jobs import JobsModule
from infrastructure.logging import LoggingModule
from infrastructure.notification import NotificationModule
from infrastructure.outbox.processor import OutboxProcessorConfig
from infrastructure.storage import StorageModule


class InfrastructureContainer(containers.DeclarativeContainer):
    """
    Infrastructure layer DI container.

    Uses factory pattern to create adapters based on configuration.
    All infrastructure services are singletons managed by DI.

    Components:
    - ConfigService: Configuration access (created by ConfigModule)
    - Logger: Logging service (created by LoggingModule)
    - Cache: Caching service (Redis or In-Memory)
    - Storage: File storage service (Local or S3)
    - Database: Database connection (PostgreSQL)
    - Event Bus: Domain event publishing (In-Memory)
    - CQRS Buses: Command and Query routing

    Note: UoW factories are context-specific and created in bounded context containers.
    Each context has its own UoW that exposes its repositories.

    Example:
        container = InfrastructureContainer()

        # Get config service
        config_service = container.config_service()
        db_config = config_service.database

        # Get services
        logger = container.logger()
        cache = await container.cache_service()
        database = await container.database()
        event_bus = await container.event_bus()
    """

    # =========================================================================
    # Core Services (DI manages singleton lifecycle)
    # =========================================================================

    # Configuration Service (Singleton)
    config_service = providers.Singleton(ConfigModule.create_service)

    # Logger (Singleton)
    logger = providers.Singleton(
        LoggingModule.create_logger,
        config_service=config_service,
    )

    # =========================================================================
    # Infrastructure Services (Async)
    # =========================================================================

    # Cache Service (async) - CacheModule reads adapter type from config
    cache_service = providers.Singleton(
        CacheModule.create_cache,
        config_service=config_service,
        logger=logger,
    )

    # Database (async) - DatabaseModule reads adapter type from config
    database = providers.Singleton(
        DatabaseModule.create_database,
        config_service=config_service,
        logger=logger,
    )

    # Event Bus (async) - EventsModule reads adapter type from config
    event_bus = providers.Singleton(
        EventsModule.create_event_bus,
        config_service=config_service,
        logger=logger,
    )

    # Session Factory - will be set after database initialization in lifespan
    # This is a Dependency because async database must be awaited first
    session_factory = providers.Dependency()

    # Event Bus (resolved) - will be set after event_bus initialization in lifespan
    # Context containers should use this instead of event_bus directly
    event_bus_resolved = providers.Dependency()

    # =========================================================================
    # Background Jobs
    # =========================================================================

    # Job Service - JobsModule reads adapter type from config
    job_service = providers.Singleton(
        JobsModule.create_jobs,
        config_service=config_service,
        logger=logger,
    )

    # Job Service (resolved) - will be set after job_service initialization in lifespan
    job_service_resolved = providers.Dependency()

    # Outbox Processor Configuration
    outbox_processor_config = providers.Singleton(
        OutboxProcessorConfig,
        batch_size=100,
        poll_interval_seconds=5.0,
        retry_backoff_seconds=60,
        max_retries=5,
        cleanup_interval_seconds=3600.0,  # 1 hour
        cleanup_older_than_days=7,
    )

    # Outbox Processor - will be set after async services init in lifespan
    # This is a Dependency because it depends on session_factory and event_bus (async)
    outbox_processor = providers.Dependency()

    # =========================================================================
    # Storage Service
    # =========================================================================

    # Storage Service (async) - StorageModule reads adapter type from config
    storage_service = providers.Singleton(
        StorageModule.create_storage,
        config_service=config_service,
        logger=logger,
    )

    # Storage Service (resolved) - will be set after storage_service initialization in lifespan
    storage_service_resolved = providers.Dependency()

    # =========================================================================
    # Notification Service
    # =========================================================================

    # Notification Service (async) - NotificationModule reads adapter type from config
    notification_service = providers.Singleton(
        NotificationModule.create_notification,
        logger=logger,
    )

    # Notification Service (resolved) - will be set after notification_service initialization in lifespan
    notification_service_resolved = providers.Dependency()

    # =========================================================================
    # CQRS Buses (BusesModule reads adapter type from config)
    # =========================================================================

    command_bus = providers.Singleton(
        BusesModule.create_command_bus,
        config_service=config_service,
        logger=logger,
    )

    query_bus = providers.Singleton(
        BusesModule.create_query_bus,
        config_service=config_service,
        logger=logger,
    )
