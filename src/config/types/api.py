"""API configuration type."""

from typing import List, TypedDict


class APIConfigType(TypedDict):
    """API configuration type."""

    api_v1_prefix: str
    api_v2_prefix: str
    docs_enabled: bool
    docs_title: str
    docs_description: str
    request_timeout: int
    max_request_size: int
    default_page_size: int
    max_page_size: int
    docs_ip_whitelist: List[str]
