"""
File Repository Interface

Defines the contract for file repository operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from contexts.file_management.domain.entities.file import File
from shared.application.ports.repositories import IRepository


class IFileRepository(IRepository):
    """
    Interface for file repository.

    Defines all operations for managing file entities in the database.
    """

    # ========================================================================
    # BASIC CRUD - Inherited from IRepository
    # ========================================================================

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[File]:
        """
        Get file by ID.

        Args:
            id: File UUID

        Returns:
            File entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[File]:
        """
        Get all files with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted records

        Returns:
            List of file entities
        """
        pass

    @abstractmethod
    async def save(self, entity: File) -> File:
        """
        Save file entity (create or update).

        Args:
            entity: File entity to save

        Returns:
            Saved file entity with generated ID
        """
        pass

    @abstractmethod
    async def add(self, entity: File) -> File:
        """
        Add new file entity.

        Args:
            entity: File entity to add

        Returns:
            Added file entity with generated ID
        """
        pass

    @abstractmethod
    async def update(self, entity: File) -> File:
        """
        Update existing file entity.

        Args:
            entity: File entity to update

        Returns:
            Updated file entity
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID, soft: bool = True) -> None:
        """
        Delete file entity.

        Args:
            id: File UUID
            soft: If True, perform soft delete; if False, hard delete
        """
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """
        Check if file exists.

        Args:
            id: File UUID

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def count(self, include_deleted: bool = False) -> int:
        """
        Count all files.

        Args:
            include_deleted: Include soft-deleted records

        Returns:
            Total count
        """
        pass

    # ========================================================================
    # FILE-SPECIFIC OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[File]:
        """
        Get file by internal name.

        Args:
            name: Internal file name

        Returns:
            File entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[File]:
        """
        Get files by owner.

        Args:
            owner_id: Owner user UUID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of file entities owned by user
        """
        pass

    @abstractmethod
    async def get_public_files(self, skip: int = 0, limit: int = 100) -> List[File]:
        """
        Get public files.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of public file entities
        """
        pass

    @abstractmethod
    async def get_accessible_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[File]:
        """
        Get files accessible by user.

        Returns files that are:
        - Owned by user, OR
        - Public, OR
        - Shared with user

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of accessible file entities
        """
        pass

    @abstractmethod
    async def count_by_owner(self, owner_id: UUID) -> int:
        """
        Count files by owner.

        Args:
            owner_id: Owner user UUID

        Returns:
            Number of files owned by user
        """
        pass

    # ========================================================================
    # OPTIONAL: Additional Query Methods
    # ========================================================================

    @abstractmethod
    async def find_by_criteria(
        self,
        filters: dict,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> List[File]:
        """
        Find files by criteria.

        Args:
            filters: Dictionary of field:value filters
            skip: Number of records to skip
            limit: Maximum number of records
            order_by: Field to order by
            order_desc: Order descending if True

        Returns:
            List of matching file entities
        """
        pass

    @abstractmethod
    async def search(
        self, search_term: str, search_fields: List[str], skip: int = 0, limit: int = 100
    ) -> List[File]:
        """
        Search files by text in specified fields.

        Args:
            search_term: Text to search for
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of matching file entities
        """
        pass
