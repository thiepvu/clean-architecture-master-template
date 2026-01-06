"""CORS configuration type."""

from typing import List, TypedDict


class CORSConfigType(TypedDict):
    """CORS configuration type."""

    cors_enabled: bool
    cors_origins: List[str]
    cors_credentials: bool
    cors_methods: List[str]
    cors_headers: List[str]
    cors_expose_headers: List[str]
    cors_max_age: int
