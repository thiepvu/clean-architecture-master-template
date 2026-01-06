"""
Outbox Pattern Implementation for reliable event delivery.

The Outbox Pattern ensures reliable event publishing by:
1. Storing events in the same transaction as the aggregate changes
2. A background processor polls and publishes unpublished events
3. Events are marked as published after successful delivery

Flow:
┌─────────────────────────────────────────────────────────────────────────┐
│  1. Command Handler executes business logic                             │
│  2. UnitOfWork saves aggregate + outbox event in SAME transaction      │
│  3. Transaction commits (atomic: aggregate + event saved together)      │
│  4. OutboxProcessor polls unpublished events (using JobsModule)        │
│  5. Events published to Event Bus                                       │
│  6. Events marked as published in outbox table                         │
└─────────────────────────────────────────────────────────────────────────┘

Architecture:
- Ports: shared/application/ports/outbox.py (IOutboxEvent, IOutboxRepository, etc.)
- SQLAlchemy models/repo/uow: infrastructure/database/orm/adapters/sqlalchemy/shared/outbox/
- Publisher & Processor: This module (infrastructure/outbox/)

Benefits:
- Guaranteed delivery (events survive crashes)
- Atomic consistency (no orphan events)
- Retry on failure with exponential backoff
- Dead letter queue for failed events
"""

# Re-export from SQLAlchemy shared module for convenience
from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
    OutboxEvent,
    OutboxEventModel,
    OutboxRepository,
    OutboxUnitOfWork,
    OutboxUnitOfWorkFactory,
)

# Re-export from ports
from shared.application.ports.outbox import (
    IOutboxEvent,
    IOutboxProcessor,
    IOutboxRepository,
    OutboxEventStatus,
)

# Local exports
from .processor import OutboxProcessor, OutboxProcessorConfig, OutboxProcessorFactory
from .publisher import DomainEventFactory, OutboxEventPublisher

__all__ = [
    # SQLAlchemy implementations
    "OutboxEvent",
    "OutboxEventModel",
    "OutboxRepository",
    "OutboxUnitOfWork",
    "OutboxUnitOfWorkFactory",
    # Ports/Interfaces
    "IOutboxEvent",
    "IOutboxRepository",
    "IOutboxProcessor",
    "OutboxEventStatus",
    # Processor
    "OutboxProcessor",
    "OutboxProcessorConfig",
    "OutboxProcessorFactory",
    # Publisher
    "OutboxEventPublisher",
    "DomainEventFactory",
]
