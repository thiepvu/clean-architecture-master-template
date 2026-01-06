"""
Shared Kernel for Clean Architecture.

This module contains shared components used across all bounded contexts:
- domain: Domain primitives (Entity, AggregateRoot, ValueObject, Events, Result)
- application: Application layer components (Command, Query, DTO, Ports)
- presentation: API/HTTP layer components (Controllers, Responses, ErrorHandlers)
- bootstrap: Bootstrap helpers for app-level code (main.py, scripts)
- errors: Error handling (ErrorCodes, Exceptions)

Usage by Layer:
───────────────
Domain/Application Layer:
    from shared import Command, Query, Result, AggregateRoot

Presentation Layer:
    from shared.presentation import ApiResponse, BaseController

Bootstrap/Scripts:
    from shared.bootstrap import create_config_service, create_logger
"""

# Application Layer
from .application import DTO, Command, CommandHandler, Query, QueryHandler

# Ports (Interfaces)
from .application.ports import (
    ICacheService,
    ICommandBus,
    IConfigService,
    IDatabaseAdapter,
    IEventBus,
    IEventHandler,
    ILogger,
    IQueryBus,
    IRepository,
    IUnitOfWork,
    IUnitOfWorkFactory,
)

# Bootstrap Helpers (for main.py, scripts, app_factory.py)
from .bootstrap import (
    create_config_service,
    create_logger,
    reset_bootstrap_config,
    reset_bootstrap_logger,
)

# Domain Layer
from .domain import AggregateRoot, BaseEntity, DomainEvent, Result, ValueObject

# Errors
from .errors import (
    BadRequestException,
    BaseException,
    ConflictException,
    DomainException,
    ErrorCode,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)

__all__ = [
    # =========================================================================
    # Domain Layer
    # =========================================================================
    "BaseEntity",
    "AggregateRoot",
    "ValueObject",
    "DomainEvent",
    "Result",
    # =========================================================================
    # Application Layer
    # =========================================================================
    "Command",
    "CommandHandler",
    "Query",
    "QueryHandler",
    "DTO",
    # =========================================================================
    # Ports (Interfaces)
    # =========================================================================
    "IRepository",
    "IUnitOfWork",
    "IUnitOfWorkFactory",
    "IEventBus",
    "IEventHandler",
    "ICommandBus",
    "IQueryBus",
    "IConfigService",
    "ICacheService",
    "IDatabaseAdapter",
    "ILogger",
    # =========================================================================
    # Bootstrap Helpers
    # =========================================================================
    "create_config_service",
    "create_logger",
    "reset_bootstrap_config",
    "reset_bootstrap_logger",
    # =========================================================================
    # Errors
    # =========================================================================
    "ErrorCode",
    "BaseException",
    "DomainException",
    "NotFoundException",
    "ValidationException",
    "ConflictException",
    "UnauthorizedException",
    "ForbiddenException",
    "BadRequestException",
    "InternalServerException",
]
