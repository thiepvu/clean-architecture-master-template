"""
User Management Application Ports.

Contains repository and service interfaces (outbound ports).
These are the contracts that Infrastructure layer must implement.
"""

from .unit_of_work import IUserManagementUoW, IUserManagementUoWFactory
from .user_read_repository import IUserReadRepository
from .user_repository import IUserRepository

__all__ = [
    # User Repository
    "IUserRepository",
    "IUserReadRepository",
    # Unit of Work
    "IUserManagementUoW",
    "IUserManagementUoWFactory",
]
