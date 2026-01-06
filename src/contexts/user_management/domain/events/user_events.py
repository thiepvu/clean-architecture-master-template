"""
User domain events.

Event Types:
- UserCreatedEvent: Outbox event (cross-context: File BC creates storage)
- UserUpdatedEvent: Direct event (internal side effects only)
- UserActivatedEvent: Direct event (internal side effects only)
- UserDeactivatedEvent: Direct event (internal side effects only)

OutboxEvent marker means the event will be saved to outbox table
for reliable cross-context delivery via OutboxProcessor.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from shared.domain.events import DomainEvent, OutboxEvent


class UserCreatedEvent(DomainEvent, OutboxEvent):
    """
    User created domain event.

    This is an OutboxEvent because:
    - File Management BC needs to create default storage for new users
    - Other BCs may need to react to user creation
    - Guaranteed delivery is required for cross-context integration
    """

    def __init__(self, user_id: UUID, email: str):
        """
        Initialize user created event.

        Args:
            user_id: User UUID
            email: User email address
        """
        super().__init__()
        self.user_id = user_id
        self.email = email

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = super().to_dict()
        data.update({"user_id": str(self.user_id), "email": self.email})
        return data


class UserUpdatedEvent(DomainEvent):
    """User updated domain event"""

    def __init__(self, user_id: UUID, changes: Optional[Dict[str, Any]] = None):
        """
        Initialize user updated event.

        Args:
            user_id: User UUID
            changes: Dictionary of changes made
        """
        super().__init__()
        self.user_id = user_id
        self.changes = changes or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = super().to_dict()
        data.update({"user_id": str(self.user_id), "changes": self.changes})
        return data


class UserActivatedEvent(DomainEvent):
    """User activated domain event"""

    def __init__(self, user_id: UUID):
        """
        Initialize user activated event.

        Args:
            user_id: User UUID
        """
        super().__init__()
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = super().to_dict()
        data.update({"user_id": str(self.user_id)})
        return data


class UserDeactivatedEvent(DomainEvent):
    """User deactivated domain event"""

    def __init__(self, user_id: UUID):
        """
        Initialize user deactivated event.

        Args:
            user_id: User UUID
        """
        super().__init__()
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = super().to_dict()
        data.update({"user_id": str(self.user_id)})
        return data
