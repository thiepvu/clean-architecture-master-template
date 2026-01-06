"""API versioning utilities"""

from enum import Enum


class APIVersion(str, Enum):
    """API version enum"""

    V1 = "v1"
    V2 = "v2"


def get_api_prefix(version: APIVersion) -> str:
    """
    Get API prefix for version.

    Args:
        version: API version

    Returns:
        API prefix string
    """
    return f"/api/{version.value}"
