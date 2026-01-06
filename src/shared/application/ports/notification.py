"""
Notification Service Port (Interface).

Defines the contract for sending notifications.
Implementations: InMemoryNotificationAdapter, NovuNotificationAdapter
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable


class NotificationChannel(str, Enum):
    """Available notification channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationRecipient:
    """Recipient information for a notification."""

    subscriber_id: str  # Unique identifier for the recipient
    email: Optional[str] = None
    phone: Optional[str] = None
    device_tokens: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class NotificationPayload:
    """Payload for a notification."""

    # Content
    subject: Optional[str] = None
    body: str = ""
    html_body: Optional[str] = None

    # Template (for providers like Novu)
    template_id: Optional[str] = None
    template_variables: Optional[dict[str, Any]] = None

    # Attachments
    attachments: Optional[list[dict[str, Any]]] = None

    # Action buttons/links
    actions: Optional[list[dict[str, Any]]] = None

    # Custom data
    data: Optional[dict[str, Any]] = None


@dataclass
class NotificationRequest:
    """Request to send a notification."""

    recipient: NotificationRecipient
    payload: NotificationPayload
    channels: list[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.EMAIL])
    priority: NotificationPriority = NotificationPriority.NORMAL

    # Scheduling
    scheduled_at: Optional[datetime] = None

    # Deduplication
    idempotency_key: Optional[str] = None

    # Metadata
    metadata: Optional[dict[str, Any]] = None


@dataclass
class NotificationResult:
    """Result of sending a notification."""

    notification_id: str
    status: NotificationStatus
    channel: NotificationChannel
    recipient_id: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    provider_message_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class BulkNotificationResult:
    """Result of sending bulk notifications."""

    total: int
    successful: int
    failed: int
    results: list[NotificationResult] = field(default_factory=list)


@runtime_checkable
class INotificationService(Protocol):
    """
    Notification service port (interface).

    All notification adapters must implement this protocol.
    Supports multiple channels and async operations.

    Example:
        class NovuNotificationAdapter:
            async def send(
                self,
                request: NotificationRequest,
            ) -> NotificationResult:
                ...
    """

    async def send(self, request: NotificationRequest) -> NotificationResult:
        """
        Send a notification to a single recipient.

        Args:
            request: Notification request with recipient, payload, and channels

        Returns:
            NotificationResult with status and metadata

        Raises:
            NotificationError: If sending fails
        """
        ...

    async def send_bulk(
        self,
        requests: list[NotificationRequest],
    ) -> BulkNotificationResult:
        """
        Send notifications to multiple recipients.

        Args:
            requests: List of notification requests

        Returns:
            BulkNotificationResult with aggregated status
        """
        ...

    async def send_to_topic(
        self,
        topic: str,
        payload: NotificationPayload,
        channels: Optional[list[NotificationChannel]] = None,
    ) -> BulkNotificationResult:
        """
        Send notification to all subscribers of a topic.

        Args:
            topic: Topic/group identifier
            payload: Notification content
            channels: Channels to use (optional)

        Returns:
            BulkNotificationResult with aggregated status
        """
        ...

    async def get_status(self, notification_id: str) -> Optional[NotificationResult]:
        """
        Get status of a sent notification.

        Args:
            notification_id: Notification ID

        Returns:
            NotificationResult or None if not found
        """
        ...

    async def cancel(self, notification_id: str) -> bool:
        """
        Cancel a scheduled notification.

        Args:
            notification_id: Notification ID to cancel

        Returns:
            True if cancelled, False if not found or already sent
        """
        ...

    async def subscribe(
        self,
        subscriber_id: str,
        topic: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Subscribe a user to a topic for notifications.

        Args:
            subscriber_id: User/subscriber ID
            topic: Topic to subscribe to
            metadata: Additional subscription metadata

        Returns:
            True if subscribed successfully
        """
        ...

    async def unsubscribe(self, subscriber_id: str, topic: str) -> bool:
        """
        Unsubscribe a user from a topic.

        Args:
            subscriber_id: User/subscriber ID
            topic: Topic to unsubscribe from

        Returns:
            True if unsubscribed successfully
        """
        ...

    async def create_subscriber(
        self,
        subscriber_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Create or update a subscriber profile.

        Args:
            subscriber_id: Unique subscriber ID
            email: Email address
            phone: Phone number
            first_name: First name
            last_name: Last name
            metadata: Additional metadata

        Returns:
            True if created/updated successfully
        """
        ...

    async def delete_subscriber(self, subscriber_id: str) -> bool:
        """
        Delete a subscriber profile.

        Args:
            subscriber_id: Subscriber ID to delete

        Returns:
            True if deleted successfully
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if notification service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    async def initialize(self) -> None:
        """
        Initialize the notification service.

        Called during application startup.
        """
        ...

    async def close(self) -> None:
        """
        Close the notification service.

        Called during application shutdown.
        """
        ...


class NotificationError(Exception):
    """Base exception for notification operations."""

    pass


class NotificationSendError(NotificationError):
    """Exception raised when notification sending fails."""

    pass


class NotificationTemplateError(NotificationError):
    """Exception raised when template is not found or invalid."""

    pass


class NotificationSubscriberError(NotificationError):
    """Exception raised when subscriber operations fail."""

    pass
