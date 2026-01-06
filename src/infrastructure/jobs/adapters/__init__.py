"""
Jobs Adapters.

Available adapters:
- RedisCeleryJobAdapter: Redis Celery-based job processing
- InMemoryJobAdapter: In-memory job processing (for development/testing)
"""

from .in_memory import InMemoryJobAdapter

# Lazy import for RedisCeleryJobAdapter to avoid import error when celery is not installed
try:
    from .redis_celery import RedisCeleryJobAdapter
except ImportError:
    RedisCeleryJobAdapter = None  # type: ignore[misc, assignment]

__all__ = [
    "RedisCeleryJobAdapter",
    "InMemoryJobAdapter",
]
