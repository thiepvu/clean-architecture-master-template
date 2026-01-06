"""
Logger Adapters.

Available adapters:
- StandardLoggerAdapter: Standard Python logging with JSON/colored output
"""

from .standard import StandardLoggerAdapter

__all__ = [
    "StandardLoggerAdapter",
]
