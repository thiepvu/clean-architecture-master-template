"""
Novu Notification Adapter.

Uses Novu notification platform for multi-channel notifications.
Suitable for production with advanced notification features.

Requirements:
    pip install novu
"""

from .adapter import NovuNotificationAdapter

__all__ = ["NovuNotificationAdapter"]
