"""
File Management HTTP Presentation Module.

Contains:
- Module: Handler registrations (CQRS, Events)
- Controllers: HTTP controllers (import from .controllers)
- Schemas: API request/response schemas (import from .schemas)
- Routes: API route definitions
- Dependencies: FastAPI dependencies

Note: Container is NOT exported here. Use bootstrapper.containers instead.

Usage:
──────
from presentation.http.contexts.file_management import FileManagementModule
from presentation.http.contexts.file_management.controllers import FileController
from presentation.http.contexts.file_management.schemas import UpdateFileRequest

# For container, use:
from bootstrapper.containers import FileManagementContainer
"""

from .module import FileManagementModule

__all__ = [
    "FileManagementModule",
]
