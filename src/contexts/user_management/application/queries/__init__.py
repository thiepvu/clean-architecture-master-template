"""
User Management Queries and Query Handlers.

Queries represent read operations that don't change state.
Each query has exactly one handler.

Structure:
- Queries: Data objects representing the data request
- Handlers: Execute the query logic (read-only)
"""

from .get_user_by_email import GetUserByEmailHandler, GetUserByEmailQuery
from .get_user_by_id import GetUserByIdHandler, GetUserByIdQuery
from .get_user_by_username import GetUserByUsernameHandler, GetUserByUsernameQuery
from .list_users import ListUsersHandler, ListUsersQuery

__all__ = [
    # Queries
    "GetUserByIdQuery",
    "GetUserByEmailQuery",
    "GetUserByUsernameQuery",
    "ListUsersQuery",
    # Handlers
    "GetUserByIdHandler",
    "GetUserByEmailHandler",
    "GetUserByUsernameHandler",
    "ListUsersHandler",
]
