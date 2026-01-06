"""
User Management Dependencies for FastAPI.

Re-exports shared dependencies and provides context-specific ones.
"""

# Re-export shared dependencies
from shared.presentation.dependencies import CommandBusDep, QueryBusDep

__all__ = [
    # Shared dependencies (re-exported for convenience)
    "CommandBusDep",
    "QueryBusDep",
    # Context-specific dependencies can be added here
]
