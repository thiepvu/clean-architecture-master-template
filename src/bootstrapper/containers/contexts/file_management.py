"""
File Management DI Container - Composition Root.

Located in bootstrapper layer where it's allowed to import from ALL layers.

Clean Architecture Compliance:
─────────────────────────────
✅ Bootstrapper CAN import from Infrastructure
✅ Uses Composition metadata from context (single source of truth)
✅ Presentation receives pre-wired containers (no Infrastructure knowledge)
✅ Application/Domain layers remain pure

CQRS Pattern:
─────────────
- Commands -> CommandHandlers -> UoW (owns repositories)
- Queries -> QueryHandlers -> Read Repository
"""

from typing import Any

from dependency_injector import containers, providers

# Composition metadata - single source of truth for handlers
from contexts.file_management.composition import FileManagementComposition

# Get handler types from composition (cleaner than direct imports)
_cmd_handlers = FileManagementComposition.COMMAND_HANDLERS
_query_handlers = FileManagementComposition.QUERY_HANDLERS

from infrastructure.database.orm.adapters.sqlalchemy.contexts.file_management.repositories.file_read_repository import (
    FileReadRepository,
)
from infrastructure.database.orm.adapters.sqlalchemy.contexts.file_management.unit_of_work import (
    FileManagementUoWFactory,
)


# Helper to get handler type by command/query name
def _get_handler(handlers: dict, name: str):
    """Get handler type from composition by command/query name."""
    for cmd_type, handler_type in handlers.items():
        if cmd_type.__name__ == name:
            return handler_type
    raise KeyError(f"Handler for {name} not found in composition")


class FileManagementContainer(containers.DeclarativeContainer):
    """
    DI Container for File Management bounded context.

    CQRS Structure:
    - Write Side: Commands -> CommandHandlers -> UoW (owns repositories)
    - Read Side: Queries -> QueryHandlers -> Read Repository

    Handler types are obtained from FileManagementComposition,
    keeping this container focused on infrastructure wiring only.
    """

    # =========================================================================
    # Dependencies (injected from ApplicationContainer)
    # =========================================================================
    session_factory: Any = providers.Dependency()
    event_bus: Any = providers.Dependency()
    logger: Any = providers.Dependency()
    storage_service: Any = providers.Dependency()  # IStorageService from InfrastructureContainer

    # =========================================================================
    # Infrastructure Wiring (Bootstrapper's responsibility)
    # =========================================================================

    # Unit of Work Factory (for Commands)
    uow_factory = providers.Singleton(
        FileManagementUoWFactory,
        session_factory=session_factory,
        event_bus=event_bus,
        logger=logger,
    )

    # Read Repository (for Queries)
    file_read_repository = providers.Factory(
        FileReadRepository,
        session_factory=session_factory,
    )

    # =========================================================================
    # Command Handlers (types from Composition)
    # =========================================================================
    upload_file_handler = providers.Factory(
        _get_handler(_cmd_handlers, "UploadFileCommand"),
        uow_factory=uow_factory,
        storage_service=storage_service,
    )

    update_file_handler = providers.Factory(
        _get_handler(_cmd_handlers, "UpdateFileCommand"),
        uow_factory=uow_factory,
    )

    delete_file_handler = providers.Factory(
        _get_handler(_cmd_handlers, "DeleteFileCommand"),
        uow_factory=uow_factory,
        storage_service=storage_service,
        logger=logger,
    )

    share_file_handler = providers.Factory(
        _get_handler(_cmd_handlers, "ShareFileCommand"),
        uow_factory=uow_factory,
    )

    # =========================================================================
    # Query Handlers (types from Composition)
    # =========================================================================
    get_file_by_id_handler = providers.Factory(
        _get_handler(_query_handlers, "GetFileByIdQuery"),
        read_repository=file_read_repository,
    )

    list_files_handler = providers.Factory(
        _get_handler(_query_handlers, "ListFilesQuery"),
        read_repository=file_read_repository,
    )

    get_file_download_handler = providers.Factory(
        _get_handler(_query_handlers, "GetFileDownloadQuery"),
        read_repository=file_read_repository,
    )
