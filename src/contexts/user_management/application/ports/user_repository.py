from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, Optional

from contexts.user_management.domain.entities.user import User
from contexts.user_management.domain.value_objects.email import Email
from shared.application.ports.repositories import IRepository


class IUserRepository(IRepository[User]):
    """Repository interface for User aggregate."""

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Return a user by Email or None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Return a user by username or None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def count_by_criteria(self, filters: Dict[str, Any]) -> int:
        """Return count of users matching given criteria."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist a user and return the persisted entity (may be updated)."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: User) -> None:  # type: ignore[override]
        """Mark a user as deleted / remove from persistence."""
        raise NotImplementedError
