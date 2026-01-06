"""
User Management Unit of Work Interface.

Context-specific UoW that exposes user repository.
This interface is used by Command Handlers in this bounded context.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from shared.domain.base_aggregate import AggregateRoot

from .user_repository import IUserRepository


class IUserManagementUoW(ABC):
    """
    Unit of Work for User Management bounded context.

    Exposes the user repository as a property.
    All write operations on users should go through this UoW.

    Example:
        async with uow_factory.create() as uow:
            user = await uow.users.get_by_email(email)
            if user:
                return Result.fail("Email exists")

            new_user = User.create(...)
            await uow.users.add(new_user)
            uow.track(new_user)
            await uow.commit()
    """

    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        """
        Get user repository.

        Returns:
            IUserRepository instance bound to current session
        """
        pass

    @abstractmethod
    async def __aenter__(self) -> IUserManagementUoW:
        """Enter async context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass

    @abstractmethod
    def track(self, aggregate: AggregateRoot) -> None:
        """Track aggregate for domain events."""
        pass


class IUserManagementUoWFactory(ABC):
    """
    Factory for creating User Management UoW instances.

    Returns IUserManagementUoW which has the .users property.
    """

    @abstractmethod
    def create(self) -> IUserManagementUoW:
        """
        Create a new User Management UoW.

        Returns:
            New IUserManagementUoW instance
        """
        pass
