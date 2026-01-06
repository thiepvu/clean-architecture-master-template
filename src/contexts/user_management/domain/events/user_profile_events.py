"""
UserProfile Domain Events.

Event Types:
- UserProfileCreatedEvent: Direct event (internal side effects only)
- UserProfileUpdatedEvent: Direct event (internal side effects only)
- UserProfilePhotoUpdatedEvent: Outbox event (cross-context, reliable delivery)
- UserProfileSettingsUpdatedEvent: Direct event (internal side effects only)

Direct events are published immediately to in-memory Event Bus.
Outbox events are saved to DB in same transaction, then published by OutboxProcessor.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from shared.domain.events import DomainEvent, OutboxEvent


class UserProfileCreatedEvent(DomainEvent):
    """
    Published when a new UserProfile is created.

    Direct event - triggers internal side effects only.
    """

    def __init__(self, profile_id: UUID, user_id: UUID):
        """
        Initialize event.

        Args:
            profile_id: UserProfile UUID
            user_id: Associated User UUID
        """
        super().__init__()
        self.profile_id = profile_id
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "profile_id": str(self.profile_id),
                "user_id": str(self.user_id),
            }
        )
        return data


class UserProfileUpdatedEvent(DomainEvent):
    """
    Published when UserProfile bio or general info is updated.

    Subscribers might:
    - Update search index
    - Invalidate cache
    - Log activity
    """

    def __init__(
        self,
        profile_id: UUID,
        user_id: UUID,
        changes: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize event.

        Args:
            profile_id: UserProfile UUID
            user_id: Associated User UUID
            changes: Dictionary of field changes
        """
        super().__init__()
        self.profile_id = profile_id
        self.user_id = user_id
        self.changes = changes or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "profile_id": str(self.profile_id),
                "user_id": str(self.user_id),
                "changes": self.changes,
            }
        )
        return data


class UserProfilePhotoUpdatedEvent(DomainEvent, OutboxEvent):
    """
    Published when user avatar/photo is updated.

    Outbox event - saved to outbox table for reliable cross-context delivery.

    Subscribers (via OutboxProcessor):
    - CDN cache purging
    - Image resizing jobs
    - Thumbnail generation
    - File Management BC notifications
    """

    def __init__(
        self,
        profile_id: UUID,
        user_id: UUID,
        old_avatar_url: Optional[str],
        new_avatar_url: str,
    ):
        """
        Initialize event.

        Args:
            profile_id: UserProfile UUID
            user_id: Associated User UUID
            old_avatar_url: Previous avatar URL (None if first upload)
            new_avatar_url: New avatar URL
        """
        super().__init__()
        self.profile_id = profile_id
        self.user_id = user_id
        self.old_avatar_url = old_avatar_url
        self.new_avatar_url = new_avatar_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "profile_id": str(self.profile_id),
                "user_id": str(self.user_id),
                "old_avatar_url": self.old_avatar_url,
                "new_avatar_url": self.new_avatar_url,
            }
        )
        return data


class UserProfileSettingsUpdatedEvent(DomainEvent):
    """
    Published when user settings/preferences are updated.

    Subscribers might:
    - Sync settings to client apps
    - Update notification preferences
    - Log preference changes for analytics
    """

    def __init__(
        self,
        profile_id: UUID,
        user_id: UUID,
        old_settings: Dict[str, Any],
        new_settings: Dict[str, Any],
    ):
        """
        Initialize event.

        Args:
            profile_id: UserProfile UUID
            user_id: Associated User UUID
            old_settings: Previous settings state
            new_settings: Updated settings state
        """
        super().__init__()
        self.profile_id = profile_id
        self.user_id = user_id
        self.old_settings = old_settings
        self.new_settings = new_settings

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "profile_id": str(self.profile_id),
                "user_id": str(self.user_id),
                "old_settings": self.old_settings,
                "new_settings": self.new_settings,
            }
        )
        return data
