"""
Bounded Contexts.

Each context is a self-contained module with:
- domain/ - Domain layer (entities, value objects, events, errors)
- application/ - Application layer (commands, queries, handlers, DTOs)

Public API is exposed via context's __init__.py.

Usage:
──────
from contexts.user_management import CreateUserCommand, UserReadModel
from contexts.file_management import UploadFileCommand, FileReadModel
"""
