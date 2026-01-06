"""
Unit of Work Interface (Outbound Port).

Defines the contract for transaction management in Clean Architecture.
UoW is injected into Application Layer (Command Handlers) and controls
transaction boundaries.

Pattern: UoW owns session and exposes repositories.
- Each UoW instance creates a NEW session when entering context
- Repositories are accessed via properties (uow.users, uow.files)
- Session is closed when exiting context

Example:
    class CreateUserHandler:
        def __init__(self, uow_factory: IUserManagementUoWFactory):
            self._uow_factory = uow_factory

        async def handle(self, command: CreateUserCommand) -> Result[UserDTO]:
            async with self._uow_factory.create() as uow:
                # Check business rules using repository from UoW
                existing = await uow.users.get_by_email(command.email)
                if existing:
                    return Result.fail("Email exists")

                # Create and persist
                user = User.create(...)
                await uow.users.add(user)

                # Track for domain events
                uow.track(user)

                # Commit transaction
                await uow.commit()

            return Result.ok(UserDTO.from_entity(user))
"""

from abc import ABC, abstractmethod
from typing import Any

from shared.domain.base_aggregate import AggregateRoot


class IUnitOfWork(ABC):
    """
    Base Unit of Work interface for transaction management.

    Responsibilities:
    - Owns database session (created on enter, closed on exit)
    - Manages transaction lifecycle (commit/rollback)
    - Tracks aggregates for domain event publishing

    Context-specific UoW interfaces should extend this to add
    repository properties. For example:

        class IUserManagementUoW(IUnitOfWork):
            @property
            @abstractmethod
            def users(self) -> IUserRepository:
                pass
    """

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """
        Enter async context.
        Creates a new database session.

        Returns:
            Self
        """
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context.
        Commits on success, rolls back on exception.
        Closes session.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        pass

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit transaction.
        Saves all changes to the database.
        Domain events are published AFTER successful commit.
        """
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """
        Rollback transaction.
        Discards all changes.
        """
        pass

    @abstractmethod
    def track(self, aggregate: AggregateRoot) -> None:
        """
        Track an aggregate for domain event collection.
        Events will be published after successful commit.

        Args:
            aggregate: Aggregate root to track
        """
        pass


class IUnitOfWorkFactory(ABC):
    """
    Factory for creating Unit of Work instances.

    Each call to create() returns a NEW UoW with its OWN session.
    This is critical for:
    - Short-lived transactions (no DB lock during CPU-bound work)
    - Multiple independent transactions in one request
    - Background jobs that need their own sessions

    Context-specific factories should return context-specific UoW types.
    """

    @abstractmethod
    def create(self) -> IUnitOfWork:
        """
        Create a new Unit of Work instance.

        Returns:
            New IUnitOfWork instance with its own session
        """
        pass

    def __call__(self) -> IUnitOfWork:
        """Allow using factory as callable."""
        return self.create()
