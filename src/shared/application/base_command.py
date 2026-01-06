"""
Command pattern implementation for CQRS.

Commands represent intentions to change state (Write operations).
Each command should have exactly one handler.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from shared.domain.result import Result

TResult = TypeVar("TResult")
TCommand = TypeVar("TCommand", bound="Command")


class Command(BaseModel, ABC):
    """
    Base command class.

    Commands are immutable requests that represent an intention to perform
    an action that changes state. They should:
    - Be named in imperative mood (CreateUser, UpdateOrder, DeleteFile)
    - Contain all data needed to perform the action
    - Be immutable (frozen)
    - Have exactly one handler

    Example:
        class CreateUserCommand(Command):
            email: str
            username: str
            first_name: str
            last_name: str

        class UpdateUserCommand(Command):
            user_id: UUID
            first_name: Optional[str] = None
            last_name: Optional[str] = None
    """

    class Config:
        frozen = True  # Make command immutable
        extra = "forbid"  # Don't allow extra fields


class CommandHandler(ABC, Generic[TCommand, TResult]):
    """
    Base command handler.

    Handles the execution of a specific command type and returns a Result.
    Command handlers:
    - Process exactly one command type
    - Modify state (create, update, delete)
    - Use write-optimized repositories
    - Manage transactions via Unit of Work
    - Publish domain events

    Example:
        class CreateUserHandler(CommandHandler[CreateUserCommand, UserDTO]):
            def __init__(
                self,
                user_repository: IUserRepository,
                uow_factory: IUnitOfWorkFactory,
            ):
                self._user_repo = user_repository
                self._uow_factory = uow_factory

            async def handle(self, command: CreateUserCommand) -> Result[UserDTO]:
                # Validate business rules
                # Create entity
                # Persist changes
                # Return result
                ...
    """

    @abstractmethod
    async def handle(self, command: TCommand) -> Result[TResult]:
        """
        Handle command execution.

        Args:
            command: Command to execute

        Returns:
            Result containing success value or error
        """
        pass
