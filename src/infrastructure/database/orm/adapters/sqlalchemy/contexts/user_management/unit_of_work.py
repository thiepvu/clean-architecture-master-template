"""
User Management Unit of Work Implementation.

Concrete implementation of IUserManagementUoW that provides
the user repository bound to the current session.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contexts.user_management.application.ports import (
    IUserManagementUoW,
    IUserManagementUoWFactory,
    IUserRepository,
)
from infrastructure.database.orm.adapters.sqlalchemy.shared import (
    BaseUnitOfWork,
    BaseUnitOfWorkFactory,
)
from shared.application.ports.event_bus import IEventBus

from .repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class UserManagementUoW(BaseUnitOfWork, IUserManagementUoW):
    """
    Unit of Work for User Management bounded context.

    Provides access to user repository through the .users property.
    Repository is lazily created with the current session.

    Example:
        async with uow_factory.create() as uow:
            existing = await uow.users.get_by_email(email)
            if not existing:
                user = User.create(...)
                await uow.users.add(user)
                uow.track(user)
            await uow.commit()
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: Optional[IEventBus] = None,
        logger: Optional["ILogger"] = None,
    ):
        super().__init__(session_factory, event_bus, logger)
        self._user_repo: Optional[UserRepository] = None

    @property
    def users(self) -> IUserRepository:
        """
        Get user repository.

        Repository is lazily created with current session.

        Returns:
            IUserRepository instance
        """
        if self._user_repo is None:
            self._user_repo = UserRepository(self.session)
        return self._user_repo

    async def __aenter__(self) -> "UserManagementUoW":
        """Enter context and reset repository cache."""
        await super().__aenter__()
        self._user_repo = None  # Reset so it gets new session
        return self


class UserManagementUoWFactory(BaseUnitOfWorkFactory, IUserManagementUoWFactory):
    """
    Factory for creating User Management UoW instances.
    """

    def create(self) -> UserManagementUoW:
        """
        Create a new User Management UoW.

        Returns:
            New UserManagementUoW instance
        """
        return UserManagementUoW(
            session_factory=self._session_factory,
            event_bus=self._event_bus,
            logger=self._logger,
        )
