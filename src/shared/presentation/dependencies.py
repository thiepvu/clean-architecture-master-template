"""
Shared FastAPI Dependencies.

Common dependencies used across all bounded contexts.
Uses Request.app.state to access container, avoiding circular imports.

Clean Architecture:
───────────────────
- Presentation layer does NOT import from Bootstrapper
- Container is accessed via app.state (set during startup)
- Dependencies are resolved at runtime, not import time

Usage:
──────
from shared.presentation.dependencies import CommandBusDep, QueryBusDep

@router.post("/")
async def create_user(request: CreateUserRequest, command_bus: CommandBusDep):
    await command_bus.dispatch(CreateUserCommand(...))
"""

from typing import Annotated

from fastapi import Depends, Request

from shared.application.ports import ICommandBus, IQueryBus

# ============================================================================
# Dependency Providers (Runtime Resolution)
# ============================================================================


def get_command_bus(request: Request) -> ICommandBus:
    """
    Get command bus from application state.

    The container is attached to app.state during startup by bootstrapper.
    This avoids circular imports between presentation and bootstrapper layers.

    Args:
        request: FastAPI request object

    Returns:
        Command bus instance from DI container
    """
    container = request.app.state.container
    return container.infrastructure.command_bus()


def get_query_bus(request: Request) -> IQueryBus:
    """
    Get query bus from application state.

    The container is attached to app.state during startup by bootstrapper.
    This avoids circular imports between presentation and bootstrapper layers.

    Args:
        request: FastAPI request object

    Returns:
        Query bus instance from DI container
    """
    container = request.app.state.container
    return container.infrastructure.query_bus()


# ============================================================================
# CQRS Dependencies (Type-annotated for IDE support)
# ============================================================================

CommandBusDep = Annotated[ICommandBus, Depends(get_command_bus)]
"""Command Bus dependency for write operations (Commands)."""

QueryBusDep = Annotated[IQueryBus, Depends(get_query_bus)]
"""Query Bus dependency for read operations (Queries)."""
