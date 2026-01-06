"""
Event Handlers for User Management context.

Event handlers are invoked when domain events are published to the Event Bus.
They handle side effects like sending emails, updating read models, etc.

Architecture:
─────────────
┌─────────────────┐
│  Event Bus      │
│  publish(event) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Event Handlers  │  ← Subscribed handlers
│ - SendWelcome   │
│ - ProcessAvatar │
└─────────────────┘

Usage:
──────
# In bootstrapper/registrations/contexts/user_management.py
from contexts.user_management.application.event_handlers import (
    SendWelcomeEmailHandler,
    ProcessAvatarHandler,
)
event_bus.subscribe(UserCreatedEvent, welcome_handler)
event_bus.subscribe(UserProfilePhotoUpdatedEvent, avatar_handler)
"""

from .process_avatar_handler import ProcessAvatarHandler
from .send_welcome_email import SendWelcomeEmailHandler

__all__ = [
    "SendWelcomeEmailHandler",
    "ProcessAvatarHandler",
]
