"""
Context registrations.

Each context module exports register_all() function.
"""

from . import file_management, user_management

__all__ = [
    "user_management",
    "file_management",
]
