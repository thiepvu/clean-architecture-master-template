"""Repository interface (Outbound Port)"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from shared.domain.base_entity import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class IRepository(ABC, Generic[TEntity]):
    """
    Generic repository interface.
    Defines contract for data access operations.

    This is an outbound port that will be implemented
    by the infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[TEntity]:
        """
        Get entity by ID.

        Args:
            id: Entity UUID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[TEntity]:
        """
        Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            include_deleted: Include soft-deleted records

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    async def add(self, entity: TEntity) -> TEntity:
        """
        Add new entity.

        Args:
            entity: Entity to add

        Returns:
            Added entity with generated ID
        """
        pass

    @abstractmethod
    async def update(self, entity: TEntity) -> TEntity:
        """
        Update existing entity.

        Args:
            entity: Entity to update

        Returns:
            Updated entity
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID, soft: bool = True) -> None:
        """
        Delete entity.

        Args:
            id: Entity UUID
            soft: If True, perform soft delete
        """
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.

        Args:
            id: Entity UUID

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def count(self, include_deleted: bool = False) -> int:
        """
        Count entities.

        Args:
            include_deleted: Include soft-deleted records

        Returns:
            Total count
        """
        pass
