"""
Main Application DI Container.

Wires together infrastructure and bounded context containers.
Context containers are defined in bootstrapper/containers/contexts/ (Composition Root).

Architecture:
─────────────
ApplicationContainer (this file)
├── InfrastructureContainer (bootstrapper/containers/)
├── UserManagementContainer (bootstrapper/containers/contexts/)
└── FileManagementContainer (bootstrapper/containers/contexts/)

Clean Architecture:
───────────────────
Bootstrapper is the Composition Root - the ONLY place allowed to import
from all layers (Domain, Application, Infrastructure) to wire dependencies.
Presentation layer receives pre-wired containers without knowing Infrastructure.
"""

from dependency_injector import containers, providers

from .contexts import FileManagementContainer, UserManagementContainer
from .infrastructure_container import InfrastructureContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Main application container.
    Wires together infrastructure, CQRS buses, and all bounded context containers.

    CQRS Flow:
    - Commands → CommandBus → CommandHandler → Write Repository → Domain Events
    - Queries → QueryBus → QueryHandler → Read Repository → Read Models

    Usage:
        container = ApplicationContainer()
        container.config.from_pydantic(settings)

        # Access buses
        command_bus = container.infrastructure.command_bus()
        query_bus = container.infrastructure.query_bus()

        # Dispatch command
        await command_bus.dispatch(CreateUserCommand(...))

        # Dispatch query
        result = await query_bus.dispatch(GetUserByIdQuery(...))
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            # User Management Presentation
            "presentation.http.contexts.user_management.dependencies",
            "presentation.http.contexts.user_management.routes",
            "presentation.http.contexts.user_management.controllers.user_controller",
            # File Management Presentation
            "presentation.http.contexts.file_management.dependencies",
            "presentation.http.contexts.file_management.routes",
            "presentation.http.contexts.file_management.controllers.file_controller",
        ]
    )

    # Configuration
    config = providers.Configuration()

    # Infrastructure container (includes buses)
    infrastructure = providers.Container(InfrastructureContainer)

    # Bounded Context containers
    # Note: UoW factories are context-specific and created within each container
    # Uses resolved dependencies (set in lifespan after async services init)
    user_management = providers.Container(
        UserManagementContainer,
        session_factory=infrastructure.session_factory,  # For Read Repositories & UoW
        event_bus=infrastructure.event_bus_resolved,  # Use resolved event_bus
        cache_service=infrastructure.cache_service,  # For query caching
        logger=infrastructure.logger,  # For UoW logging
    )

    file_management = providers.Container(
        FileManagementContainer,
        session_factory=infrastructure.session_factory,  # For Read Repositories & UoW
        event_bus=infrastructure.event_bus_resolved,  # Use resolved event_bus
        logger=infrastructure.logger,  # For UoW logging
        storage_service=infrastructure.storage_service_resolved,  # For file storage
    )
