"""
File Management Composition Root Exports.

This module defines what the context needs for DI wiring.
Bootstrapper imports from here instead of knowing internal implementation details.

Clean Architecture:
───────────────────
- Context defines WHAT it needs (handlers, dependencies)
- Bootstrapper decides HOW to wire them (infrastructure adapters)
- Single source of truth for handler registrations (CQRS only)

Usage:
──────
from contexts.file_management.composition import FileManagementComposition

# Get handler mappings
for cmd_type, handler_type in FileManagementComposition.COMMAND_HANDLERS.items():
    command_bus.register(cmd_type, container.resolve(handler_type))
"""

from typing import Any, Dict, List, Type

# Commands & Handlers
from .application.commands import (
    DeleteFileCommand,
    DeleteFileHandler,
    ShareFileCommand,
    ShareFileHandler,
    UpdateFileCommand,
    UpdateFileHandler,
    UploadFileCommand,
    UploadFileHandler,
)

# Queries & Handlers
from .application.queries import (
    GetFileByIdHandler,
    GetFileByIdQuery,
    GetFileDownloadHandler,
    GetFileDownloadQuery,
    ListFilesHandler,
    ListFilesQuery,
)


class FileManagementComposition:
    """
    Composition metadata for File Management bounded context.

    Bootstrapper uses this to wire dependencies without knowing
    implementation details of each handler.

    Currently follows CQRS pattern only (Commands & Queries).

    Benefits:
    - Single source of truth for registrations
    - Easy to add/remove handlers
    - Bootstrapper doesn't need to know internal imports
    - Testable (can mock composition for testing)
    """

    # =========================================================================
    # Context Identifier
    # =========================================================================
    CONTEXT_NAME = "file_management"

    # =========================================================================
    # Command Handlers Mapping
    # Command Type -> Handler Type
    # =========================================================================
    COMMAND_HANDLERS: Dict[Type, Type[Any]] = {
        UploadFileCommand: UploadFileHandler,
        UpdateFileCommand: UpdateFileHandler,
        DeleteFileCommand: DeleteFileHandler,
        ShareFileCommand: ShareFileHandler,
    }

    # =========================================================================
    # Query Handlers Mapping
    # Query Type -> Handler Type
    # =========================================================================
    QUERY_HANDLERS: Dict[Type, Type[Any]] = {
        GetFileByIdQuery: GetFileByIdHandler,
        ListFilesQuery: ListFilesHandler,
        GetFileDownloadQuery: GetFileDownloadHandler,
    }

    # =========================================================================
    # Handler Provider Names (for container access)
    # Maps handler type to container provider name
    # =========================================================================
    HANDLER_PROVIDERS: Dict[Type, str] = {
        # Command Handlers
        UploadFileHandler: "upload_file_handler",
        UpdateFileHandler: "update_file_handler",
        DeleteFileHandler: "delete_file_handler",
        ShareFileHandler: "share_file_handler",
        # Query Handlers
        GetFileByIdHandler: "get_file_by_id_handler",
        ListFilesHandler: "list_files_handler",
        GetFileDownloadHandler: "get_file_download_handler",
    }

    @classmethod
    def get_handler_provider_name(cls, handler_type: Type) -> str:
        """Get container provider name for a handler type."""
        return cls.HANDLER_PROVIDERS.get(handler_type, "")

    @classmethod
    def get_all_command_types(cls) -> List[Type]:
        """Get all command types for this context."""
        return list(cls.COMMAND_HANDLERS.keys())

    @classmethod
    def get_all_query_types(cls) -> List[Type]:
        """Get all query types for this context."""
        return list(cls.QUERY_HANDLERS.keys())
