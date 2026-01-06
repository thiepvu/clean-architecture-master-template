"""
Bounded Context DI Containers - Composition Root.

This is the Composition Root where ALL dependencies are wired.
Located in bootstrapper layer - the ONLY place allowed to import from
all layers (Domain, Application, Infrastructure).

Why here?
─────────
Clean Architecture requires Presentation NOT to know Infrastructure.
But DI containers need to wire Infrastructure adapters to Application ports.

Solution: Move container definitions to bootstrapper (Composition Root).
Presentation layer only receives pre-wired containers.

Structure:
──────────
bootstrapper/containers/contexts/
├── __init__.py              # This file - exports all containers
├── user_management.py       # UserManagementContainer
└── file_management.py       # FileManagementContainer

Usage in ApplicationContainer:
──────────────────────────────
from bootstrapper.containers.contexts import (
    UserManagementContainer,
    FileManagementContainer,
)
"""

from .file_management import FileManagementContainer
from .user_management import UserManagementContainer

__all__ = [
    "UserManagementContainer",
    "FileManagementContainer",
]
