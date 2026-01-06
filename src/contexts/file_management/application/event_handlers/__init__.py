"""
File Management Event Handlers.

These handlers listen to domain events (both internal and cross-context)
and perform side effects like creating storage quotas, updating indices, etc.
"""

from .create_user_storage_handler import CreateUserStorageHandler

__all__ = [
    "CreateUserStorageHandler",
]
