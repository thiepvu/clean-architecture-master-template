"""
File Management Application Services.

Application services orchestrate use cases that may involve
multiple aggregates or cross-context communication.
"""

from .user_verification_service import UserVerificationService

__all__ = [
    "UserVerificationService",
]
