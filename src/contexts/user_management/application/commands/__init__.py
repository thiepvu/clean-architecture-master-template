"""
User Management Commands and Command Handlers.

Commands represent intentions to change state (write operations).
Each command has exactly one handler.

Structure:
- Commands: Data objects representing the action
- Handlers: Execute the command logic
"""

from .activate_user import ActivateUserCommand, ActivateUserHandler
from .create_user import CreateUserCommand, CreateUserHandler
from .deactivate_user import DeactivateUserCommand, DeactivateUserHandler
from .delete_user import DeleteUserCommand, DeleteUserHandler
from .update_user import UpdateUserCommand, UpdateUserHandler

__all__ = [
    # Commands
    "CreateUserCommand",
    "UpdateUserCommand",
    "DeleteUserCommand",
    "ActivateUserCommand",
    "DeactivateUserCommand",
    # Handlers
    "CreateUserHandler",
    "UpdateUserHandler",
    "DeleteUserHandler",
    "ActivateUserHandler",
    "DeactivateUserHandler",
]
