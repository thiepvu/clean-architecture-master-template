"""
Custom endpoints for FastAPI application.

Handles:
- Health check endpoints
- Custom OpenAPI/Swagger/ReDoc endpoints
"""

from typing import TYPE_CHECKING

from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from bootstrapper.module_loader import ModuleLoader
from shared.application.ports import IConfigService
from shared.bootstrap import create_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

    from bootstrapper.containers import ApplicationContainer

logger = create_logger()


def load_modules(app: "FastAPI", config_service: IConfigService) -> None:
    """Load modules and their routes."""
    api_config = config_service.api

    module_loader = ModuleLoader()

    # Load v1 routes
    v1_routers = module_loader.load_all_routes("v1")
    for module_name, router in v1_routers:
        app.include_router(router, prefix=api_config.API_V1_PREFIX)
        logger.debug(f"✓ Included {module_name} v1 routes")

    # Load v2 routes (if any)
    # v2_routers = module_loader.load_all_routes("v2")
    # for module_name, router in v2_routers:
    #     app.include_router(router, prefix=settings.API_V2_PREFIX)
    #     logger.debug(f"✓ Included {module_name} v2 routes")

    # Store loaded contexts in app state
    app.state.loaded_contexts = module_loader.loaded_modules
    app.state.failed_contexts = module_loader.failed_modules


def add_docs_endpoints(app: "FastAPI") -> None:
    """Add custom ReDoc and Swagger UI endpoints if docs are enabled."""

    @app.get("/api/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
        )

    logger.info("✓ ReDoc endpoint added")

    @app.get("/api/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

    logger.info("✓ Swagger UI endpoint added")


def add_custom_openapi(app: "FastAPI") -> None:
    """Add custom OpenAPI schema with security schemes."""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}

        openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your Bearer token in the format: your-token-here",
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    logger.info("✓ Custom OpenAPI schema configured")


def add_health_check(app: "FastAPI", config_service: IConfigService) -> None:
    """Add health check endpoints."""
    base_config = config_service.base
    cache_config = config_service.cache
    db_config = config_service.database
    events_config = config_service.events

    @app.get("/health", tags=["Health"], summary="Basic health check")
    async def health_check():
        """
        Basic health check endpoint.
        Returns application status and version.
        """
        return {
            "status": "healthy",
            "version": base_config.APP_VERSION,
            "environment": base_config.ENVIRONMENT,
        }

    @app.get("/health/detailed", tags=["Health"], summary="Detailed health check")
    async def detailed_health_check():
        """
        Detailed health check with infrastructure service status.
        Returns status of each infrastructure component.
        """
        from bootstrapper.containers import ApplicationContainer

        container: ApplicationContainer = getattr(app.state, "container", None)
        services_status = {}
        overall_healthy = True

        if container:
            infra = container.infrastructure

            # Check Cache
            try:
                cache = await infra.cache_service()
                cache_healthy = await cache.health_check()
                services_status["cache"] = {
                    "status": "healthy" if cache_healthy else "unhealthy",
                    "adapter": cache_config.CACHE_ADAPTER,
                }
                if not cache_healthy:
                    overall_healthy = False
            except Exception as e:
                services_status["cache"] = {"status": "error", "message": str(e)}
                overall_healthy = False

            # Check Database
            try:
                database = await infra.database()
                db_healthy = await database.health_check()
                services_status["database"] = {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "adapter": db_config.DATABASE_ADAPTER,
                }
                if not db_healthy:
                    overall_healthy = False
            except Exception as e:
                services_status["database"] = {"status": "error", "message": str(e)}
                overall_healthy = False

            # Check Event Bus
            try:
                event_bus = await infra.event_bus()
                eb_healthy = await event_bus.health_check()
                services_status["event_bus"] = {
                    "status": "healthy" if eb_healthy else "unhealthy",
                    "adapter": events_config.EVENT_BUS_ADAPTER,
                }
                if not eb_healthy:
                    overall_healthy = False
            except Exception as e:
                services_status["event_bus"] = {"status": "error", "message": str(e)}
                overall_healthy = False

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "version": base_config.APP_VERSION,
            "environment": base_config.ENVIRONMENT,
            "debug": base_config.DEBUG,
            "services": services_status,
            "contexts": {
                "loaded": getattr(app.state, "loaded_contexts", []),
                "failed": getattr(app.state, "failed_contexts", []),
            },
        }

    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root():
        """Root endpoint redirecting to docs."""
        return {
            "message": f"Welcome to {base_config.APP_NAME}",
            "version": base_config.APP_VERSION,
            "docs": "/api/docs",
        }

    logger.info("✓ Health check endpoints added")
