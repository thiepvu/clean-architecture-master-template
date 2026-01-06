"""Base configuration type."""

from typing import Literal, TypedDict


class BaseConfigType(TypedDict):
    """Base/Environment configuration type."""

    environment: Literal["development", "testing", "staging", "production"]
    debug: bool
    testing: bool
    app_name: str
    app_version: str
    app_description: str
    host: str
    port: int
    scheme: str
    workers: int
    server_url: str
