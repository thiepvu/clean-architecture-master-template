"""
Base Configuration

Defines BaseConfig with common application settings.
Environment detection and .env loading is handled by ConfigModule via env_loader.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import env_loader to get detected environment
# Note: env_loader.load_env_files() is called by ConfigModule before configs are instantiated
from config.env_loader import get_environment
from config.types import BaseConfigType


class BaseConfig(BaseSettings):
    """Base configuration with common settings"""

    # Environment - uses detected environment as default
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = Field(
        default_factory=get_environment, description="Environment name"
    )
    DEBUG: bool = Field(default=False, description="Debug mode")
    TESTING: bool = Field(default=False, description="Testing mode")

    # Application info
    APP_NAME: str = Field(default="Clean Architecture API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(
        default="Clean Architecture", description="Application description"
    )

    # Server
    HOST: str = Field(default="0.0.0.0", description="Host address")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Port number")
    SCHEME: str = Field(default="http", description="URL scheme (http or https)")

    # Workers
    WORKERS: int = Field(default=1, ge=1, description="Number of worker processes")

    # Pydantic will read from environment variables (loaded by ConfigModule)
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_nested_delimiter="__",
    )

    @property
    def SERVER_URL(self) -> str:
        """Build server URL from SCHEME, HOST, PORT"""
        if (self.SCHEME == "http" and self.PORT == 80) or (
            self.SCHEME == "https" and self.PORT == 443
        ):
            return f"{self.SCHEME}://{self.HOST}"
        return f"{self.SCHEME}://{self.HOST}:{self.PORT}"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"

    def to_dict(self) -> BaseConfigType:
        """Convert to typed dictionary format."""
        return BaseConfigType(
            environment=self.ENVIRONMENT,
            debug=self.DEBUG,
            testing=self.TESTING,
            app_name=self.APP_NAME,
            app_version=self.APP_VERSION,
            app_description=self.APP_DESCRIPTION,
            host=self.HOST,
            port=self.PORT,
            scheme=self.SCHEME,
            workers=self.WORKERS,
            server_url=self.SERVER_URL,
        )
