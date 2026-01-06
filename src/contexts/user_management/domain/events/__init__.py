"""User domain events"""

from .user_events import (
    UserActivatedEvent,
    UserCreatedEvent,
    UserDeactivatedEvent,
    UserUpdatedEvent,
)
from .user_profile_events import (
    UserProfileCreatedEvent,
    UserProfilePhotoUpdatedEvent,
    UserProfileSettingsUpdatedEvent,
    UserProfileUpdatedEvent,
)

__all__ = [
    # User events
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserActivatedEvent",
    "UserDeactivatedEvent",
    # UserProfile events
    "UserProfileCreatedEvent",
    "UserProfileUpdatedEvent",
    "UserProfilePhotoUpdatedEvent",
    "UserProfileSettingsUpdatedEvent",
]
