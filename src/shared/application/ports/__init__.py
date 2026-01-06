"""
Ports (Interfaces) for Clean Architecture.

Ports define the contracts between layers:
- Inbound ports: Use Cases (called by controllers)
- Outbound ports: Repository interfaces, external services (implemented by infrastructure)

Infrastructure Ports:
- IConfigService: Configuration access
- ICacheService: Cache operations (Redis, In-Memory)
- IStorageService: File storage operations (Local, S3)
- INotificationService: Notification operations (In-Memory, Novu)
- IEventBus: Event publishing and subscription
- IDatabaseAdapter: Database connection management
- ILogger: Logging operations

CQRS Ports:
- ICommandBus: Command dispatching
- IQueryBus: Query dispatching
"""

from .cache import ICacheService
from .command_bus import ICommandBus
from .config import IConfigService
from .database import IDatabaseAdapter
from .event_bus import IEventBus, IEventHandler
from .jobs import IJobService, JobInfo, JobResult, JobStatus
from .logger import ILogger
from .notification import (
    BulkNotificationResult,
    INotificationService,
    NotificationChannel,
    NotificationError,
    NotificationPayload,
    NotificationPriority,
    NotificationRecipient,
    NotificationRequest,
    NotificationResult,
    NotificationSendError,
    NotificationStatus,
    NotificationSubscriberError,
    NotificationTemplateError,
)
from .outbox import (
    IOutboxEvent,
    IOutboxEventPublisher,
    IOutboxProcessor,
    IOutboxRepository,
    OutboxEventStatus,
)
from .query_bus import IQueryBus
from .repositories import IRepository
from .storage import (
    IStorageService,
    PresignedUrl,
    StorageDownloadError,
    StorageError,
    StorageFile,
    StoragePermissionError,
    StorageUploadError,
)
from .unit_of_work import IUnitOfWork, IUnitOfWorkFactory

__all__ = [
    # Repository & UoW
    "IRepository",
    "IUnitOfWork",
    "IUnitOfWorkFactory",
    # Infrastructure
    "IConfigService",
    "ICacheService",
    "IStorageService",
    "StorageFile",
    "PresignedUrl",
    "StorageError",
    "StorageUploadError",
    "StorageDownloadError",
    "StoragePermissionError",
    "INotificationService",
    "NotificationChannel",
    "NotificationStatus",
    "NotificationPriority",
    "NotificationRecipient",
    "NotificationPayload",
    "NotificationRequest",
    "NotificationResult",
    "BulkNotificationResult",
    "NotificationError",
    "NotificationSendError",
    "NotificationTemplateError",
    "NotificationSubscriberError",
    "IEventBus",
    "IEventHandler",
    "IDatabaseAdapter",
    "ILogger",
    "IJobService",
    "JobResult",
    "JobStatus",
    "JobInfo",
    # Outbox
    "IOutboxEvent",
    "IOutboxRepository",
    "IOutboxProcessor",
    "IOutboxEventPublisher",
    "OutboxEventStatus",
    # CQRS
    "ICommandBus",
    "IQueryBus",
]
