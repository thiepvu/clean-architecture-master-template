"""
File Management Application Ports.

Contains repository and service interfaces (outbound ports).
These are the contracts that Infrastructure layer must implement.

Note: IStorageService is now a shared infrastructure port.
Use: from shared.application.ports import IStorageService
"""

from .file_read_repository import IFileReadRepository
from .file_repository import IFileRepository
from .unit_of_work import IFileManagementUoW, IFileManagementUoWFactory

__all__ = [
    # File Repository
    "IFileRepository",
    "IFileReadRepository",
    # Unit of Work
    "IFileManagementUoW",
    "IFileManagementUoWFactory",
]
