"""
Bounded Context HTTP Presentations.

Each context has:
- module.py - Handler registrations (CQRS, Events)
- routes.py - API routes
- controllers/ - Controllers (import from .{context}.controllers)
- schemas/ - Request schemas (import from .{context}.schemas)
- dependencies.py - FastAPI dependencies

Note: Containers are NOT in presentation layer. Use bootstrapper.containers instead.

Usage:
──────
from presentation.http.contexts import UserManagementModule, FileManagementModule
from presentation.http.contexts.user_management.controllers import UserController
from presentation.http.contexts.file_management.schemas import UpdateFileRequest

# For containers, use:
from bootstrapper.containers import UserManagementContainer, FileManagementContainer
"""

from .file_management import FileManagementModule
from .user_management import UserManagementModule

__all__ = [
    # User Management
    "UserManagementModule",
    # File Management
    "FileManagementModule",
]
