"""
Application factory for creating FastAPI application instances.

This is the main entry point for creating the FastAPI app.
The actual implementation is split into separate modules for maintainability:
- lifespan.py: Application lifespan (startup/shutdown)
- registrations.py: CQRS and Event handler registrations
- middleware.py: Middleware configuration
- exception_handlers.py: Exception handler setup
- endpoints.py: Health check and custom endpoints
"""

from fastapi import FastAPI

from bootstrapper.containers import ApplicationContainer
from bootstrapper.endpoints import (
    add_custom_openapi,
    add_docs_endpoints,
    add_health_check,
    load_modules,
)
from bootstrapper.exception_handlers import add_exception_handlers
from bootstrapper.lifespan import lifespan
from bootstrapper.middleware import add_middlewares
from bootstrapper.registrations import register_error_codes
from shared.application.ports import IConfigService
from shared.bootstrap import create_config_service, create_logger

logger = create_logger()


def create_app() -> FastAPI:
    """
    Application factory function.
    Creates and configures a FastAPI application instance.

    Returns:
        Configured FastAPI application
    """
    config_service = create_config_service()
    base_config = config_service.base
    api_config = config_service.api

    # Swagger / OpenAPI availability
    if api_config.docs_enabled:
        openapi_url = "/api/openapi.json"
    else:
        openapi_url = None

    # Create FastAPI app
    app = FastAPI(
        title=base_config.APP_NAME,
        version=base_config.APP_VERSION,
        description="Clean Architecture",
        docs_url=None,
        redoc_url=None,
        openapi_url=openapi_url,
        lifespan=lifespan,
        debug=base_config.DEBUG,
    )

    # Initialize DI container
    container = _setup_container(config_service)
    app.state.container = container

    # Add middlewares
    add_middlewares(app, config_service)

    # Add exception handlers
    add_exception_handlers(app)

    # Add health check endpoint
    add_health_check(app, config_service)

    # Load modules and routes
    load_modules(app, config_service)

    if api_config.docs_enabled:
        # Add custom endpoint
        add_docs_endpoints(app)

        # Add custom openapi security schemes
        add_custom_openapi(app)

    return app


def _setup_container(config_service: IConfigService) -> ApplicationContainer:
    """
    Setup and configure the DI container.

    Args:
        config_service: IConfigService instance

    Returns:
        Configured ApplicationContainer

    Note:
        Event handlers are registered in lifespan (async context)
        because event_bus is async.
    """
    container = ApplicationContainer()

    # Configure container with config_service
    db_config = config_service.database
    base_config = config_service.base
    container.config.from_dict(
        {
            "database": {
                "url": db_config.DATABASE_URL,
                "echo": db_config.DB_ECHO,
            },
            "app": {
                "name": base_config.APP_NAME,
                "version": base_config.APP_VERSION,
                "debug": base_config.DEBUG,
            },
        }
    )

    # Register error codes (needs container for logger)
    register_error_codes(container)

    # Note: CQRS handlers are registered in lifespan after async services init
    # because handlers depend on session_factory which requires database to be initialized

    # Wire container to context controllers
    container.wire(
        modules=[
            "presentation.http.contexts.user_management.controllers.user_controller",
            "presentation.http.contexts.file_management.controllers.file_controller",
        ]
    )

    logger.info("✓ DI Container configured and wired")

    return container
