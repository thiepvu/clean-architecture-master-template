"""
CORS configuration
"""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from config.types import CORSConfigType


class CORSConfig(BaseSettings):
    """CORS configuration settings"""

    CORS_ENABLED: bool = Field(default=True, description="Enable CORS")
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
        ],
        description="Allowed CORS origins",
    )
    CORS_CREDENTIALS: bool = Field(
        default=True, description="Allow credentials (cookies, authorization headers)"
    )
    CORS_METHODS: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed HTTP methods"
    )
    CORS_HEADERS: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed HTTP headers"
    )
    CORS_EXPOSE_HEADERS: List[str] = Field(
        default_factory=lambda: [], description="Headers exposed to browser"
    )
    CORS_MAX_AGE: int = Field(
        default=600, ge=0, description="Preflight request cache duration in seconds"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_origins(cls, v):
        """Validate and parse CORS origins"""
        if isinstance(v, str):
            # Support comma-separated string
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def allow_all_origins(self) -> bool:
        """Check if all origins are allowed"""
        return "*" in self.CORS_ORIGINS

    def to_dict(self) -> CORSConfigType:
        """Convert to typed dictionary format."""
        return CORSConfigType(
            cors_enabled=self.CORS_ENABLED,
            cors_origins=self.CORS_ORIGINS,
            cors_credentials=self.CORS_CREDENTIALS,
            cors_methods=self.CORS_METHODS,
            cors_headers=self.CORS_HEADERS,
            cors_expose_headers=self.CORS_EXPOSE_HEADERS,
            cors_max_age=self.CORS_MAX_AGE,
        )
