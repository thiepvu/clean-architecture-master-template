"""
File Management Unit of Work Interface.

Context-specific UoW that exposes file repository.
This interface is used by Command Handlers in this bounded context.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from shared.domain.base_aggregate import AggregateRoot

from .file_repository import IFileRepository


class IFileManagementUoW(ABC):
    """
    Unit of Work for File Management bounded context.

    Exposes the file repository as a property.
    All write operations on files should go through this UoW.

    Example:
        async with uow_factory.create() as uow:
            file = File.create(...)
            await uow.files.add(file)
            uow.track(file)
            await uow.commit()
    """

    @property
    @abstractmethod
    def files(self) -> IFileRepository:
        """
        Get file repository.

        Returns:
            IFileRepository instance bound to current session
        """
        pass

    @abstractmethod
    async def __aenter__(self) -> IFileManagementUoW:
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


class IFileManagementUoWFactory(ABC):
    """
    Factory for creating File Management UoW instances.

    Returns IFileManagementUoW which has the .files property.
    """

    @abstractmethod
    def create(self) -> IFileManagementUoW:
        """
        Create a new File Management UoW.

        Returns:
            New IFileManagementUoW instance
        """
        pass
