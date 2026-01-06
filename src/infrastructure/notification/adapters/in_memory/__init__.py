"""
In-Memory Notification Adapter.

Stores notifications in memory for development and testing.
Not suitable for production or distributed systems.
"""

from .adapter import InMemoryNotificationAdapter

__all__ = ["InMemoryNotificationAdapter"]
