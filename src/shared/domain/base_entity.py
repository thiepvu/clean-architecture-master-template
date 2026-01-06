"""
Base entity class for domain entities.
Entities have identity and lifecycle.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


class BaseEntity:
    """
    Base entity with identity.
    All domain entities should inherit from this class.
    """

    def __init__(self, id: Optional[UUID] = None):
        """
        Initialize entity.

        Args:
            id: Entity UUID (generated if not provided)
        """
        self._id: UUID = id or uuid4()
        self._created_at: datetime = datetime.utcnow()
        self._updated_at: datetime = datetime.utcnow()
        self._is_deleted: bool = False

    @property
    def id(self) -> UUID:
        """Get entity ID"""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp"""
        return self._updated_at

    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft deleted"""
        return self._is_deleted

    def mark_as_deleted(self) -> None:
        """
        Mark entity as deleted (soft delete).
        Does not remove from database.
        """
        self._is_deleted = True
        self._updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft-deleted entity"""
        self._is_deleted = False
        self._updated_at = datetime.utcnow()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self._updated_at = datetime.utcnow()

    def __eq__(self, other: Any) -> bool:
        """
        Compare entities by identity.
        Two entities are equal if they have the same ID.
        """
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on entity ID"""
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation"""
        return f"<{self.__class__.__name__}(id={self.id})>"
