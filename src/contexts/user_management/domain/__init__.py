"""
User Management Domain Layer.

Contains:
- entities/ - Domain entities (User, UserProfile)
- value_objects/ - Value objects (Email)
- events/ - Domain events
- errors/ - Error codes
- exceptions/ - Domain exceptions
"""

from .entities import User, UserProfile
from .errors import UserErrorCode, register_user_error_codes
from .events import (
    UserActivatedEvent,
    UserCreatedEvent,
    UserDeactivatedEvent,
    UserProfileCreatedEvent,
    UserProfilePhotoUpdatedEvent,
    UserProfileSettingsUpdatedEvent,
    UserProfileUpdatedEvent,
    UserUpdatedEvent,
)
from .exceptions import InvalidEmailException, InvalidUserStateException, UserAlreadyExistsException
from .value_objects import Email

__all__ = [
    # Entities
    "User",
    "UserProfile",
    # Value Objects
    "Email",
    # Events - User
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserActivatedEvent",
    "UserDeactivatedEvent",
    # Events - UserProfile
    "UserProfileCreatedEvent",
    "UserProfileUpdatedEvent",
    "UserProfilePhotoUpdatedEvent",
    "UserProfileSettingsUpdatedEvent",
    # Errors
    "UserErrorCode",
    "register_user_error_codes",
    # Exceptions
    "InvalidEmailException",
    "InvalidUserStateException",
    "UserAlreadyExistsException",
]
