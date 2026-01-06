"""
Application lifespan management.

Handles startup and shutdown tasks including:
- Infrastructure initialization
- Health verification
- Graceful shutdown
"""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

from dependency_injector import providers

from shared.bootstrap import create_config_service, create_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

    from bootstrapper.containers import ApplicationContainer

logger = create_logger()


@asynccontextmanager
async def lifespan(app: "FastAPI") -> AsyncGenerator:
    """
    Application lifespan events.
    Handles startup and shutdown tasks.

    Args:
        app: FastAPI application instance
    """
    # Startup
    config_service = create_config_service()
    base_config = config_service.base
    container: "ApplicationContainer" = getattr(app.state, "container", None)

    logger.info(f"🚀 Starting {base_config.APP_NAME} v{base_config.APP_VERSION}")
    logger.info(f"Environment: {base_config.ENVIRONMENT}")
    logger.info(f"Server running: {base_config.SERVER_URL}")

    if container:
        # Initialize async infrastructure services
        await _initialize_infrastructure(container)

        # Register all handlers and events (after async services are initialized)
        # This must be done AFTER database init because handlers depend on session_factory
        from bootstrapper.registrations import register_all

        register_all(container, logger)

        # Verify all services are healthy
        await _verify_infrastructure_health(container)

        logger.info("✓ DI Container initialized")

    # Log loaded contexts
    if hasattr(app.state, "loaded_contexts"):
        logger.info(f"✓ Loaded contexts: {', '.join(app.state.loaded_contexts)}")

    logger.info(f"✅ {base_config.APP_NAME} started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    if container:
        # Close infrastructure services
        await _shutdown_infrastructure(container)

    logger.info("👋 Application shutdown complete")


async def _initialize_infrastructure(container: "ApplicationContainer") -> None:
    """
    Initialize all async infrastructure services.

    The factory pattern handles initialization internally,
    but we need to await the coroutines for async services.
    """
    # Get infrastructure container
    infra = container.infrastructure

    # Initialize async services (factories handle actual initialization)
    # These are awaited to ensure they're ready before app starts
    await infra.cache_service()
    logger.info("✓ Cache service initialized")

    database = await infra.database()
    # Set session_factory dependency after database is initialized
    infra.session_factory.override(providers.Object(database.session_factory))
    logger.info("✓ Database initialized")

    event_bus = await infra.event_bus()
    # Set event_bus_resolved dependency after event_bus is initialized
    infra.event_bus_resolved.override(providers.Object(event_bus))
    logger.info("✓ Event bus initialized")

    # Initialize job service (async)
    job_service = await infra.job_service()
    # Set job_service_resolved dependency after job_service is initialized
    infra.job_service_resolved.override(providers.Object(job_service))
    logger.info("✓ Job service initialized")

    # Initialize storage service (async)
    storage_service = await infra.storage_service()
    # Set storage_service_resolved dependency after storage_service is initialized
    infra.storage_service_resolved.override(providers.Object(storage_service))
    logger.info("✓ Storage service initialized")

    # Initialize notification service (async)
    notification_service = await infra.notification_service()
    # Set notification_service_resolved dependency after notification_service is initialized
    infra.notification_service_resolved.override(providers.Object(notification_service))
    logger.info("✓ Notification service initialized")

    # Start outbox processor for reliable event delivery
    await _start_outbox_processor(container)


async def _verify_infrastructure_health(container: "ApplicationContainer") -> None:
    """
    Verify all infrastructure services are healthy.

    Implements fail-fast pattern - if any service is unhealthy,
    the application will not start.
    """
    infra = container.infrastructure

    # Verify Cache
    cache = await infra.cache_service()
    if not await cache.health_check():
        raise RuntimeError("Cache service health check failed")
    logger.info("✓ Cache service verified")

    # Verify Database
    database = await infra.database()
    if not await database.health_check():
        raise RuntimeError("Database health check failed")
    logger.info("✓ Database verified")

    # Verify Event Bus
    event_bus = await infra.event_bus()
    if not await event_bus.health_check():
        raise RuntimeError("Event bus health check failed")
    logger.info("✓ Event bus verified")

    # Verify Storage Service
    storage_service = await infra.storage_service()
    if not await storage_service.health_check():
        raise RuntimeError("Storage service health check failed")
    logger.info("✓ Storage service verified")

    # Verify Notification Service
    notification_service = await infra.notification_service()
    if not await notification_service.health_check():
        raise RuntimeError("Notification service health check failed")
    logger.info("✓ Notification service verified")


async def _start_outbox_processor(container: "ApplicationContainer") -> None:
    """
    Start the outbox processor for reliable event delivery.

    The processor runs as a background task, polling the outbox table
    and publishing events to the event bus.
    """
    from infrastructure.outbox.processor import OutboxProcessor

    config_service = create_config_service()

    # Only start in non-test environments
    if config_service.base.ENVIRONMENT == "test":
        logger.info("⏭ Outbox processor skipped (test environment)")
        return

    try:
        infra = container.infrastructure

        # Create outbox processor with resolved async dependencies
        session_factory = infra.session_factory()
        event_bus = await infra.event_bus()
        job_service = await infra.job_service()  # Singleton, returns same instance
        logger_instance = infra.logger()
        config = infra.outbox_processor_config()

        processor = OutboxProcessor(
            session_factory=session_factory,
            event_bus=event_bus,
            job_service=job_service,
            logger=logger_instance,
            config=config,
        )

        # Set the processor dependency for later use (stop)
        infra.outbox_processor.override(providers.Object(processor))

        await processor.start()
        logger.info("✓ Outbox processor started")
    except Exception as e:
        logger.warning(f"Failed to start outbox processor: {e}")


async def _stop_outbox_processor(container: "ApplicationContainer") -> None:
    """
    Stop the outbox processor gracefully.
    """
    try:
        infra = container.infrastructure
        # Check if outbox_processor was set (may not be in test environment)
        try:
            processor = infra.outbox_processor()
            if processor:
                await processor.stop()
                logger.info("✓ Outbox processor stopped")
        except Exception:
            # Processor was never started (e.g., test environment)
            pass
    except Exception as e:
        logger.warning(f"Error stopping outbox processor: {e}")


async def _shutdown_infrastructure(container: "ApplicationContainer") -> None:
    """
    Gracefully shutdown all infrastructure services.
    """
    infra = container.infrastructure

    # Stop outbox processor first
    try:
        await _stop_outbox_processor(container)
    except Exception as e:
        logger.warning(f"Error stopping outbox processor: {e}")

    try:
        # Close cache service
        cache = await infra.cache_service()
        await cache.close()
        logger.info("✓ Cache service closed")
    except Exception as e:
        logger.warning(f"Error closing cache service: {e}")

    try:
        # Close database
        database = await infra.database()
        await database.close()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.warning(f"Error closing database: {e}")

    try:
        # Close event bus
        event_bus = await infra.event_bus()
        await event_bus.close()
        logger.info("✓ Event bus closed")
    except Exception as e:
        logger.warning(f"Error closing event bus: {e}")

    try:
        # Stop job service (async singleton)
        job_service = await infra.job_service()
        await job_service.shutdown()
        logger.info("✓ Job service stopped")
    except Exception as e:
        logger.warning(f"Error stopping job service: {e}")

    try:
        # Close storage service (async singleton)
        storage_service = await infra.storage_service()
        await storage_service.close()
        logger.info("✓ Storage service closed")
    except Exception as e:
        logger.warning(f"Error closing storage service: {e}")

    try:
        # Close notification service (async singleton)
        notification_service = await infra.notification_service()
        await notification_service.close()
        logger.info("✓ Notification service closed")
    except Exception as e:
        logger.warning(f"Error closing notification service: {e}")
