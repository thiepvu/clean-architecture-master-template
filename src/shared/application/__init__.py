"""
Shared Application Layer Components.

Contains:
- Command/Query base classes (CQRS pattern)
- DTO base class
- Ports (interfaces) for infrastructure
"""

from .base_command import Command, CommandHandler
from .base_query import Query, QueryHandler
from .dto import DTO

__all__ = [
    # CQRS
    "Command",
    "CommandHandler",
    "Query",
    "QueryHandler",
    # DTO
    "DTO",
]
