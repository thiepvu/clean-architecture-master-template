"""
SQLAlchemy Outbox Pattern Implementation.

This module provides SQLAlchemy-based implementation of the Outbox pattern:
- OutboxEventModel: SQLAlchemy ORM model for persistence
- OutboxEvent: Domain model for application layer
- OutboxRepository: Repository for CRUD operations
- OutboxUnitOfWork: UoW with atomic event persistence

Usage:
    from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
        OutboxEvent,
        OutboxEventModel,
        OutboxRepository,
        OutboxUnitOfWork,
        OutboxUnitOfWorkFactory,
    )
"""

from .models import OutboxEvent, OutboxEventModel
from .repository import OutboxRepository
from .unit_of_work import OutboxUnitOfWork, OutboxUnitOfWorkFactory

__all__ = [
    # Models
    "OutboxEventModel",
    "OutboxEvent",
    # Repository
    "OutboxRepository",
    # Unit of Work
    "OutboxUnitOfWork",
    "OutboxUnitOfWorkFactory",
]
