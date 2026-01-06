"""
File Management Integration Events.

These events are published to other bounded contexts when significant
changes occur in the File Management BC.

Integration events use the Outbox Pattern for reliable delivery.
"""

from typing import List, Optional
from uuid import UUID

from shared.domain.integration_events import (
    EntityCreatedIntegrationEvent,
    EntityDeletedIntegrationEvent,
    IntegrationEvent,
)


class FileUploadedIntegrationEvent(EntityCreatedIntegrationEvent):
    """
    Published when a new file is uploaded.

    Consumers:
    - Search BC: Index file for search
    - Analytics BC: Track storage usage
    - Virus Scan BC: Queue for scanning
    """

    VERSION = "1.0"

    def __init__(
        self,
        file_id: UUID,
        owner_id: UUID,
        filename: str,
        size: int,
        mime_type: str,
        **kwargs,
    ):
        super().__init__(
            aggregate_id=file_id,
            aggregate_type="File",
            **kwargs,
        )
        self.file_id = file_id
        self.owner_id = owner_id
        self.filename = filename
        self.size = size
        self.mime_type = mime_type


class FileSharedIntegrationEvent(IntegrationEvent):
    """
    Published when a file is shared with other users.

    Consumers:
    - Notification BC: Notify recipients
    - Activity BC: Log sharing activity
    - Analytics BC: Track collaboration metrics
    """

    VERSION = "1.0"

    def __init__(
        self,
        file_id: UUID,
        owner_id: UUID,
        shared_with_user_id: UUID,
        permission_level: str = "read",  # read, write, admin
        **kwargs,
    ):
        super().__init__(
            aggregate_id=file_id,
            aggregate_type="File",
            **kwargs,
        )
        self.file_id = file_id
        self.owner_id = owner_id
        self.shared_with_user_id = shared_with_user_id
        self.permission_level = permission_level


class FileDeletedIntegrationEvent(EntityDeletedIntegrationEvent):
    """
    Published when a file is deleted.

    Consumers:
    - Search BC: Remove from search index
    - Storage BC: Clean up physical storage
    - Analytics BC: Update storage metrics
    """

    VERSION = "1.0"

    def __init__(
        self,
        file_id: UUID,
        owner_id: UUID,
        size: int,  # For storage metrics
        deletion_type: str = "soft",  # soft, hard
        **kwargs,
    ):
        super().__init__(
            aggregate_id=file_id,
            aggregate_type="File",
            **kwargs,
        )
        self.file_id = file_id
        self.owner_id = owner_id
        self.size = size
        self.deletion_type = deletion_type


class FileAccessedIntegrationEvent(IntegrationEvent):
    """
    Published when a file is accessed (downloaded/viewed).

    Consumers:
    - Analytics BC: Track file access patterns
    - Audit BC: Log access for compliance
    """

    VERSION = "1.0"

    def __init__(
        self,
        file_id: UUID,
        accessed_by_user_id: UUID,
        access_type: str = "download",  # download, view, preview
        **kwargs,
    ):
        super().__init__(
            aggregate_id=file_id,
            aggregate_type="File",
            **kwargs,
        )
        self.file_id = file_id
        self.accessed_by_user_id = accessed_by_user_id
        self.access_type = access_type


class StorageQuotaExceededIntegrationEvent(IntegrationEvent):
    """
    Published when a user exceeds their storage quota.

    Consumers:
    - Notification BC: Warn user
    - Billing BC: Offer upgrade
    """

    VERSION = "1.0"

    def __init__(
        self,
        user_id: UUID,
        current_usage: int,
        quota_limit: int,
        **kwargs,
    ):
        super().__init__(
            aggregate_id=user_id,
            aggregate_type="UserStorage",
            **kwargs,
        )
        self.user_id = user_id
        self.current_usage = current_usage
        self.quota_limit = quota_limit
        self.usage_percentage = round((current_usage / quota_limit) * 100, 2)
