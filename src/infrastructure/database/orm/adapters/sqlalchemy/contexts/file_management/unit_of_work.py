"""
File Management Unit of Work Implementation.

Concrete implementation of IFileManagementUoW that provides
the file repository bound to the current session.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contexts.file_management.application.ports import (
    IFileManagementUoW,
    IFileManagementUoWFactory,
    IFileRepository,
)
from infrastructure.database.orm.adapters.sqlalchemy.shared import (
    BaseUnitOfWork,
    BaseUnitOfWorkFactory,
)
from shared.application.ports.event_bus import IEventBus

from .repositories.file_repository import FileRepository

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class FileManagementUoW(BaseUnitOfWork, IFileManagementUoW):
    """
    Unit of Work for File Management bounded context.

    Provides access to file repository through the .files property.
    Repository is lazily created with the current session.

    Example:
        async with uow_factory.create() as uow:
            file = File.create(...)
            await uow.files.add(file)
            uow.track(file)
            await uow.commit()
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: Optional[IEventBus] = None,
        logger: Optional["ILogger"] = None,
    ):
        super().__init__(session_factory, event_bus, logger)
        self._file_repo: Optional[FileRepository] = None

    @property
    def files(self) -> IFileRepository:
        """
        Get file repository.

        Repository is lazily created with current session.

        Returns:
            IFileRepository instance
        """
        if self._file_repo is None:
            self._file_repo = FileRepository(self.session)
        return self._file_repo

    async def __aenter__(self) -> "FileManagementUoW":
        """Enter context and reset repository cache."""
        await super().__aenter__()
        self._file_repo = None  # Reset so it gets new session
        return self


class FileManagementUoWFactory(BaseUnitOfWorkFactory, IFileManagementUoWFactory):
    """
    Factory for creating File Management UoW instances.
    """

    def create(self) -> FileManagementUoW:
        """
        Create a new File Management UoW.

        Returns:
            New FileManagementUoW instance
        """
        return FileManagementUoW(
            session_factory=self._session_factory,
            event_bus=self._event_bus,
            logger=self._logger,
        )
