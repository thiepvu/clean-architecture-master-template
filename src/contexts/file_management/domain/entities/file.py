"""
File domain entity
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from shared.domain.base_aggregate import AggregateRoot

from ..events.file_events import (
    FileDeletedEvent,
    FileDownloadedEvent,
    FileSharedEvent,
    FileUpdatedEvent,
    FileUploadedEvent,
)
from ..exceptions.file_exceptions import (
    FileAccessDeniedException,
    FileSizeLimitExceededException,
    InvalidFileTypeException,
)
from ..value_objects.file_path import FilePath
from ..value_objects.file_size import FileSize
from ..value_objects.mime_type import MimeType


class File(AggregateRoot):
    """
    File domain entity (Aggregate Root).
    Represents a file in the system with metadata and access control.
    """

    # File size limits
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    # Allowed mime types
    ALLOWED_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
        "application/zip",
        "application/x-rar-compressed",
    ]

    def __init__(
        self,
        name: str,
        original_name: str,
        path: FilePath,
        size: FileSize,
        mime_type: MimeType,
        owner_id: UUID,
        description: Optional[str] = None,
        is_public: bool = False,
        download_count: int = 0,
        id: Optional[UUID] = None,
    ):
        """
        Initialize file entity.

        Args:
            name: Internal file name (unique)
            original_name: Original uploaded filename
            path: File storage path
            size: File size
            mime_type: MIME type
            owner_id: User ID who owns the file
            description: Optional file description
            is_public: Whether file is publicly accessible
            download_count: Number of downloads
            id: Entity UUID
        """
        super().__init__(id)
        self._name = name
        self._original_name = original_name
        self._path = path
        self._size = size
        self._mime_type = mime_type
        self._owner_id = owner_id
        self._description = description
        self._is_public = is_public
        self._download_count = download_count
        self._shared_with: List[UUID] = []

    # Properties

    @property
    def name(self) -> str:
        """Get internal file name"""
        return self._name

    @property
    def original_name(self) -> str:
        """Get original filename"""
        return self._original_name

    @property
    def path(self) -> FilePath:
        """Get file path"""
        return self._path

    @property
    def size(self) -> FileSize:
        """Get file size"""
        return self._size

    @property
    def mime_type(self) -> MimeType:
        """Get MIME type"""
        return self._mime_type

    @property
    def owner_id(self) -> UUID:
        """Get owner user ID"""
        return self._owner_id

    @property
    def description(self) -> Optional[str]:
        """Get description"""
        return self._description

    @property
    def is_public(self) -> bool:
        """Check if file is public"""
        return self._is_public

    @property
    def download_count(self) -> int:
        """Get download count"""
        return self._download_count

    @property
    def shared_with(self) -> List[UUID]:
        """Get list of users file is shared with"""
        return self._shared_with.copy()

    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return self._original_name.split(".")[-1] if "." in self._original_name else ""

    @property
    def is_image(self) -> bool:
        """Check if file is an image"""
        return self._mime_type.value.startswith("image/")

    @property
    def is_document(self) -> bool:
        """Check if file is a document"""
        return self._mime_type.value in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

    # Factory method

    @staticmethod
    def create(
        name: str,
        original_name: str,
        path: str,
        size: int,
        mime_type: str,
        owner_id: UUID,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> "File":
        """
        Factory method to create a new file.
        Validates file size and type.

        Args:
            name: Internal file name
            original_name: Original filename
            path: Storage path
            size: File size in bytes
            mime_type: MIME type string
            owner_id: Owner user ID
            description: Optional description
            is_public: Public access flag

        Returns:
            New File instance

        Raises:
            FileSizeLimitExceededException: If file is too large
            InvalidFileTypeException: If file type not allowed
        """
        # Validate size
        if size > File.MAX_FILE_SIZE:
            raise FileSizeLimitExceededException(size, File.MAX_FILE_SIZE)

        # Validate mime type
        if mime_type not in File.ALLOWED_MIME_TYPES:
            raise InvalidFileTypeException(mime_type)

        # Create value objects
        file_path = FilePath(path)
        file_size = FileSize(size)
        file_mime_type = MimeType(mime_type)

        # Create file
        file = File(
            name=name,
            original_name=original_name,
            path=file_path,
            size=file_size,
            mime_type=file_mime_type,
            owner_id=owner_id,
            description=description,
            is_public=is_public,
            download_count=0,
        )

        # Emit domain event
        file.add_domain_event(
            FileUploadedEvent(file.id, name, original_name, size, mime_type, owner_id)
        )

        return file

    # Business logic methods

    def update_metadata(
        self, original_name: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        """
        Update file metadata.

        Args:
            original_name: New original filename
            description: New description
        """
        if original_name:
            self._original_name = original_name

        if description is not None:
            self._description = description

        self.update_timestamp()
        self.add_domain_event(FileUpdatedEvent(self.id))

    def make_public(self) -> None:
        """Make file publicly accessible"""
        if self._is_public:
            return

        self._is_public = True
        self.update_timestamp()
        self.add_domain_event(FileUpdatedEvent(self.id, {"visibility": "public"}))

    def make_private(self) -> None:
        """Make file private"""
        if not self._is_public:
            return

        self._is_public = False
        self._shared_with.clear()  # Clear all shares when making private
        self.update_timestamp()
        self.add_domain_event(FileUpdatedEvent(self.id, {"visibility": "private"}))

    def share_with(self, user_id: UUID) -> None:
        """
        Share file with a user.

        Args:
            user_id: User ID to share with
        """
        if user_id == self._owner_id:
            return  # Owner already has access

        if user_id not in self._shared_with:
            self._shared_with.append(user_id)
            self.update_timestamp()
            self.add_domain_event(FileSharedEvent(self.id, user_id))

    def unshare_with(self, user_id: UUID) -> None:
        """
        Revoke file access from a user.

        Args:
            user_id: User ID to revoke access from
        """
        if user_id in self._shared_with:
            self._shared_with.remove(user_id)
            self.update_timestamp()

    def can_be_accessed_by(self, user_id: UUID) -> bool:
        """
        Check if user can access this file.

        Args:
            user_id: User ID to check

        Returns:
            True if user can access, False otherwise
        """
        # Owner always has access
        if user_id == self._owner_id:
            return True

        # Public files are accessible by everyone
        if self._is_public:
            return True

        # Check if shared with user
        return user_id in self._shared_with

    def record_download(self, user_id: UUID) -> None:
        """
        Record a file download.

        Args:
            user_id: User who downloaded

        Raises:
            FileAccessDeniedException: If user doesn't have access
        """
        if not self.can_be_accessed_by(user_id):
            raise FileAccessDeniedException(self.id, user_id)

        self._download_count += 1
        self.update_timestamp()
        self.add_domain_event(FileDownloadedEvent(self.id, user_id))

    def soft_delete(self) -> None:
        """Soft delete the file"""
        self.mark_as_deleted()
        self.add_domain_event(FileDeletedEvent(self.id, self._owner_id))
