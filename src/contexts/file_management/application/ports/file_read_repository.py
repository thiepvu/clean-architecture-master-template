"""
File Read Repository Interface.

This is the Query-side repository interface, separate from the
Write-side repository (IFileRepository in domain layer).

Read repositories:
- Return Read Models (DTOs), not domain entities
- Are optimized for queries
- May use different database tables/views
- Can include caching
- Never modify data
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..read_models import FileDownloadReadModel, FileListItemReadModel, FileReadModel


class IFileReadRepository(ABC):
    """
    Read-only repository for File queries.

    This interface is used by Query Handlers to fetch data
    in a read-optimized way. It returns Read Models directly,
    avoiding the overhead of loading full domain entities.
    """

    @abstractmethod
    async def get_by_id(self, file_id: UUID) -> Optional[FileReadModel]:
        """
        Get file by ID.

        Args:
            file_id: File UUID

        Returns:
            FileReadModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_download_info(self, file_id: UUID) -> Optional[FileDownloadReadModel]:
        """
        Get file download information.

        Args:
            file_id: File UUID

        Returns:
            FileDownloadReadModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_files(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        accessible_by: Optional[UUID] = None,
    ) -> List[FileListItemReadModel]:
        """
        List files with pagination and optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            owner_id: Filter by owner ID
            is_public: Filter by public status
            accessible_by: Filter by files accessible to user (owner, public, or shared)

        Returns:
            List of FileListItemReadModel
        """
        pass

    @abstractmethod
    async def count(
        self,
        owner_id: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        accessible_by: Optional[UUID] = None,
    ) -> int:
        """
        Count files matching criteria.

        Args:
            owner_id: Filter by owner ID
            is_public: Filter by public status
            accessible_by: Filter by files accessible to user

        Returns:
            Count of matching files
        """
        pass

    @abstractmethod
    async def exists(self, file_id: UUID) -> bool:
        """
        Check if file exists.

        Args:
            file_id: File UUID

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def can_access(self, file_id: UUID, user_id: UUID) -> bool:
        """
        Check if user can access file.

        User can access if:
        - User is the owner
        - File is public
        - File is shared with user

        Args:
            file_id: File UUID
            user_id: User UUID

        Returns:
            True if user can access, False otherwise
        """
        pass

    @abstractmethod
    async def is_owner(self, file_id: UUID, user_id: UUID) -> bool:
        """
        Check if user is the file owner.

        Args:
            file_id: File UUID
            user_id: User UUID

        Returns:
            True if user is owner, False otherwise
        """
        pass
