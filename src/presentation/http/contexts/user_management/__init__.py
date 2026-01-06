"""
User Management HTTP Presentation Module.

Contains:
- Module: Handler registrations (CQRS, Events)
- Controllers: HTTP controllers (import from .controllers)
- Schemas: API request/response schemas (import from .schemas)
- Routes: API route definitions
- Dependencies: FastAPI dependencies

Note: Container is NOT exported here. Use bootstrapper.containers instead.

Usage:
──────
from presentation.http.contexts.user_management import UserManagementModule
from presentation.http.contexts.user_management.controllers import UserController
from presentation.http.contexts.user_management.schemas import CreateUserRequest

# For container, use:
from bootstrapper.containers import UserManagementContainer
"""

from .module import UserManagementModule

__all__ = [
    "UserManagementModule",
]
