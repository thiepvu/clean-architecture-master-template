"""
API configuration
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

from config.types import APIConfigType


class APIConfig(BaseSettings):
    """API configuration settings"""

    # API versioning
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    API_V2_PREFIX: str = Field(default="/api/v2", description="API v2 prefix")

    # Documentation
    DOCS_ENABLED: bool = Field(
        default=True, description="Enable API documentation (Swagger, ReDoc)"
    )
    DOCS_TITLE: str = Field(default="API Documentation", description="Documentation title")
    DOCS_DESCRIPTION: str = Field(
        default="Clean Architecture API",
        description="Documentation description",
    )
    DOCS_LOGO_URL: str = Field(
        default="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        description="Documentation logo URL",
    )
    DOCS_FAVICON_URL: str = Field(
        default="/static/favicon.ico", description="Documentation favicon URL"
    )

    # Internal docs
    INTERNAL_DOCS_ENABLED: bool = Field(default=True, description="Enable internal documentation")
    DOCS_IP_WHITELIST: List[str] = Field(
        default_factory=lambda: [
            "127.0.0.1",
            "localhost",
            "::1",
        ],
        description="IP whitelist for documentation access",
    )

    # Request/Response
    REQUEST_TIMEOUT: int = Field(default=30, ge=1, description="Request timeout in seconds")
    MAX_REQUEST_SIZE: int = Field(
        default=10 * 1024 * 1024, ge=1024, description="Maximum request size in bytes"  # 10MB
    )

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(
        default=20, ge=1, le=100, description="Default pagination page size"
    )
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, description="Maximum pagination page size")

    @property
    def docs_enabled(self) -> bool:
        """Alias for DOCS_ENABLED"""
        return self.DOCS_ENABLED

    def to_dict(self) -> APIConfigType:
        """Convert to typed dictionary format."""
        return APIConfigType(
            api_v1_prefix=self.API_V1_PREFIX,
            api_v2_prefix=self.API_V2_PREFIX,
            docs_enabled=self.DOCS_ENABLED,
            docs_title=self.DOCS_TITLE,
            docs_description=self.DOCS_DESCRIPTION,
            request_timeout=self.REQUEST_TIMEOUT,
            max_request_size=self.MAX_REQUEST_SIZE,
            default_page_size=self.DEFAULT_PAGE_SIZE,
            max_page_size=self.MAX_PAGE_SIZE,
            docs_ip_whitelist=self.DOCS_IP_WHITELIST,
        )
