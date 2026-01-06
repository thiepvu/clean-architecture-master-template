"""File domain events"""

from typing import Any, Dict, Optional
from uuid import UUID

from shared.domain.events import DomainEvent


class FileUploadedEvent(DomainEvent):
    """File uploaded domain event"""

    def __init__(
        self,
        file_id: UUID,
        name: str,
        original_name: str,
        size: int,
        mime_type: str,
        owner_id: UUID,
    ):
        super().__init__()
        self.file_id = file_id
        self.name = name
        self.original_name = original_name
        self.size = size
        self.mime_type = mime_type
        self.owner_id = owner_id

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "file_id": str(self.file_id),
                "name": self.name,
                "original_name": self.original_name,
                "size": self.size,
                "mime_type": self.mime_type,
                "owner_id": str(self.owner_id),
            }
        )
        return data


class FileUpdatedEvent(DomainEvent):
    """File updated domain event"""

    def __init__(self, file_id: UUID, changes: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.file_id = file_id
        self.changes = changes or {}

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"file_id": str(self.file_id), "changes": self.changes})
        return data


class FileDeletedEvent(DomainEvent):
    """File deleted domain event"""

    def __init__(self, file_id: UUID, owner_id: UUID):
        super().__init__()
        self.file_id = file_id
        self.owner_id = owner_id

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"file_id": str(self.file_id), "owner_id": str(self.owner_id)})
        return data


class FileSharedEvent(DomainEvent):
    """File shared domain event"""

    def __init__(self, file_id: UUID, shared_with_user_id: UUID):
        super().__init__()
        self.file_id = file_id
        self.shared_with_user_id = shared_with_user_id

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {"file_id": str(self.file_id), "shared_with_user_id": str(self.shared_with_user_id)}
        )
        return data


class FileDownloadedEvent(DomainEvent):
    """File downloaded domain event"""

    def __init__(self, file_id: UUID, user_id: UUID):
        super().__init__()
        self.file_id = file_id
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"file_id": str(self.file_id), "user_id": str(self.user_id)})
        return data
