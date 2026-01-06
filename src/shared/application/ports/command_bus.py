"""
Command Bus Port (Interface).

Defines the contract for command bus implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Type

from shared.application.base_command import Command
from shared.domain.result import Result


class ICommandBus(ABC):
    """
    Command Bus interface.

    Responsible for:
    - Registering command handlers
    - Dispatching commands to appropriate handlers
    - Ensuring one handler per command type

    Example:
        class CreateUserCommand(Command):
            email: str
            username: str

        class CreateUserHandler(CommandHandler[CreateUserCommand, UserDTO]):
            async def handle(self, command: CreateUserCommand) -> Result[UserDTO]:
                ...

        # Usage
        bus = CommandBusFactory.create(adapter_type)
        bus.register(CreateUserCommand, CreateUserHandler(repo, uow))

        result = await bus.dispatch(CreateUserCommand(email="...", username="..."))
    """

    @abstractmethod
    def register(
        self,
        command_type: Type[Command],
        handler: Any,
    ) -> None:
        """
        Register a handler for a command type.

        Args:
            command_type: The command class
            handler: The handler instance

        Raises:
            ValueError: If handler already registered for this command
        """
        ...

    @abstractmethod
    async def dispatch(self, command: Command) -> Result[Any]:
        """
        Dispatch a command to its handler.

        Args:
            command: The command to dispatch

        Returns:
            Result from the handler

        Raises:
            ValueError: If no handler registered for this command
        """
        ...

    @abstractmethod
    def has_handler(self, command_type: Type[Command]) -> bool:
        """Check if a handler is registered for a command type."""
        ...

    @property
    @abstractmethod
    def registered_commands(self) -> List[Type[Command]]:
        """List all registered command types."""
        ...
