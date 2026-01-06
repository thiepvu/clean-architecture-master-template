"""Shared domain primitives for Clean Architecture."""

from .base_aggregate import AggregateRoot
from .base_entity import BaseEntity
from .events import DomainEvent
from .result import Result
from .value_objects import ValueObject

__all__ = [
    "BaseEntity",
    "AggregateRoot",
    "ValueObject",
    "DomainEvent",
    "Result",
]
