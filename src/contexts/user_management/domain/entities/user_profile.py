"""
UserProfile Aggregate Root.

Manages extended user profile information like avatar, bio, preferences.
Separate from User aggregate to follow Single Responsibility Principle.

This demonstrates:
- Creating a new aggregate with domain events
- Event publishing via UoW
- Eventual consistency with other bounded contexts
"""

from typing import Any, Dict, Optional
from uuid import UUID

from shared.domain.base_aggregate import AggregateRoot

from ..events.user_profile_events import (
    UserProfileCreatedEvent,
    UserProfilePhotoUpdatedEvent,
    UserProfileSettingsUpdatedEvent,
    UserProfileUpdatedEvent,
)


class UserProfile(AggregateRoot):
    """
    UserProfile Aggregate Root.

    Manages extended profile information for a user.
    Publishes domain events when profile changes occur.

    Example:
        profile = UserProfile.create(user_id=user.id, bio="Hello!")
        profile.update_bio("New bio")
        # profile.domain_events contains [UserProfileCreatedEvent, UserProfileUpdatedEvent]
    """

    def __init__(
        self,
        user_id: UUID,
        bio: str = "",
        avatar_url: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        id: Optional[UUID] = None,
    ):
        """
        Initialize UserProfile.

        Args:
            user_id: Reference to the User aggregate
            bio: User biography/description
            avatar_url: URL to user's avatar image
            settings: User preferences/settings
            id: Entity UUID (generated if not provided)
        """
        super().__init__(id)
        self._user_id = user_id
        self._bio = bio
        self._avatar_url = avatar_url
        self._settings = settings or {}

    # Properties (read-only access)

    @property
    def user_id(self) -> UUID:
        """Get associated user ID."""
        return self._user_id

    @property
    def bio(self) -> str:
        """Get user biography."""
        return self._bio

    @property
    def avatar_url(self) -> Optional[str]:
        """Get avatar URL."""
        return self._avatar_url

    @property
    def settings(self) -> Dict[str, Any]:
        """Get user settings (copy to prevent external modification)."""
        return self._settings.copy()

    # Factory method

    @staticmethod
    def create(
        user_id: UUID,
        bio: str = "",
        avatar_url: Optional[str] = None,
    ) -> "UserProfile":
        """
        Factory method to create a new UserProfile.

        Args:
            user_id: Reference to the User aggregate
            bio: Initial biography
            avatar_url: Initial avatar URL

        Returns:
            New UserProfile instance with creation event
        """
        profile = UserProfile(
            user_id=user_id,
            bio=bio,
            avatar_url=avatar_url,
            settings={
                "notifications_enabled": True,
                "theme": "light",
                "language": "en",
            },
        )

        # Emit domain event
        profile.add_domain_event(
            UserProfileCreatedEvent(
                profile_id=profile.id,
                user_id=user_id,
            )
        )

        return profile

    # Business logic methods

    def update_bio(self, new_bio: str) -> None:
        """
        Update user biography.

        Args:
            new_bio: New biography text
        """
        old_bio = self._bio
        self._bio = new_bio
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(
            UserProfileUpdatedEvent(
                profile_id=self.id,
                user_id=self._user_id,
                changes={"bio": {"old": old_bio, "new": new_bio}},
            )
        )

    def update_avatar(self, new_avatar_url: str) -> None:
        """
        Update user avatar.

        Args:
            new_avatar_url: New avatar URL
        """
        old_avatar = self._avatar_url
        self._avatar_url = new_avatar_url
        self.update_timestamp()

        # Emit domain event - separate event for avatar updates
        # Could trigger cache invalidation, CDN purging, etc.
        self.add_domain_event(
            UserProfilePhotoUpdatedEvent(
                profile_id=self.id,
                user_id=self._user_id,
                old_avatar_url=old_avatar,
                new_avatar_url=new_avatar_url,
            )
        )

    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """
        Update user settings/preferences.

        Args:
            new_settings: Dictionary of settings to update
        """
        old_settings = self._settings.copy()

        # Merge new settings
        self._settings.update(new_settings)
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(
            UserProfileSettingsUpdatedEvent(
                profile_id=self.id,
                user_id=self._user_id,
                old_settings=old_settings,
                new_settings=self._settings,
            )
        )

    def enable_notifications(self) -> None:
        """Enable notifications for user."""
        self.update_settings({"notifications_enabled": True})

    def disable_notifications(self) -> None:
        """Disable notifications for user."""
        self.update_settings({"notifications_enabled": False})

    def set_theme(self, theme: str) -> None:
        """
        Set user theme preference.

        Args:
            theme: Theme name (e.g., "light", "dark")
        """
        if theme not in ("light", "dark", "system"):
            raise ValueError(f"Invalid theme: {theme}. Must be light, dark, or system.")
        self.update_settings({"theme": theme})

    def set_language(self, language: str) -> None:
        """
        Set user language preference.

        Args:
            language: Language code (e.g., "en", "vi")
        """
        self.update_settings({"language": language})
