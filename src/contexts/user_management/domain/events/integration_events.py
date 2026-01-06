"""
User Management Integration Events.

These events are published to other bounded contexts when significant
changes occur in the User Management BC.

Integration events use the Outbox Pattern for reliable delivery.
"""

from typing import Optional
from uuid import UUID

from shared.domain.integration_events import (
    EntityCreatedIntegrationEvent,
    IntegrationEvent,
    StateChangedIntegrationEvent,
)


class UserRegisteredIntegrationEvent(EntityCreatedIntegrationEvent):
    """
    Published when a new user registers.

    Consumers:
    - Notification BC: Send welcome email
    - Analytics BC: Track new registrations
    - File Management BC: Create default folder structure
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        email: str,
        username: str,
        full_name: str,
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="User",
            **kwargs,
        )
        self.user_id = user_id
        self.email = email
        self.username = username
        self.full_name = full_name


class UserDeactivatedIntegrationEvent(StateChangedIntegrationEvent):
    """
    Published when a user account is deactivated.

    Consumers:
    - File Management BC: Revoke file shares
    - Session BC: Invalidate all sessions
    - Billing BC: Pause subscriptions
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        reason: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="User",
            from_state="active",
            to_state="deactivated",
            **kwargs,
        )
        self.user_id = user_id
        self.reason = reason


class UserActivatedIntegrationEvent(StateChangedIntegrationEvent):
    """
    Published when a user account is activated.

    Consumers:
    - Notification BC: Send reactivation email
    - File Management BC: Restore file access
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="User",
            from_state="deactivated",
            to_state="active",
            **kwargs,
        )
        self.user_id = user_id


class UserDeletedIntegrationEvent(IntegrationEvent):
    """
    Published when a user account is permanently deleted.

    This is a critical event that triggers cascading cleanups.

    Consumers:
    - File Management BC: Delete all user files
    - Comment BC: Anonymize user comments
    - Audit BC: Archive user activity
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        email: str,  # For audit purposes
        deletion_type: str = "user_requested",  # user_requested, admin, gdpr
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="User",
            **kwargs,
        )
        self.user_id = user_id
        self.email_hash = self._hash_email(email)  # Don't expose PII
        self.deletion_type = deletion_type

    def _hash_email(self, email: str) -> str:
        """Hash email for audit without exposing PII."""
        import hashlib

        return hashlib.sha256(email.encode()).hexdigest()[:16]


class UserProfileUpdatedIntegrationEvent(IntegrationEvent):
    """
    Published when user profile information is updated.

    Consumers:
    - Search BC: Update search index
    - Analytics BC: Track profile completeness
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        updated_fields: list[str],
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="User",
            **kwargs,
        )
        self.user_id = user_id
        self.updated_fields = updated_fields
