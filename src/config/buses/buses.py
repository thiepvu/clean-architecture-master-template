"""
Buses (CQRS) configuration - Common/Port interface.

This is the PORT that defines what all bus adapters need.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import BusesConfigType


class BusesConfig(BaseSettings):
    """
    Common buses configuration (Port interface).

    This config is used to select which CQRS bus adapter to use.
    Adapter-specific configs extend this.

    Environment Variables:
        BUS_ADAPTER: Bus adapter type (in_memory | redis | rabbitmq)
    """

    BUS_ADAPTER: Literal["in_memory", "redis", "rabbitmq"] = Field(
        default="in_memory",
        description="Bus adapter: in_memory | redis | rabbitmq",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_in_memory(self) -> bool:
        """Check if using in-memory adapter."""
        return self.BUS_ADAPTER == "in_memory"

    @property
    def is_redis(self) -> bool:
        """Check if using Redis adapter."""
        return self.BUS_ADAPTER == "redis"

    @property
    def is_rabbitmq(self) -> bool:
        """Check if using RabbitMQ adapter."""
        return self.BUS_ADAPTER == "rabbitmq"

    def to_dict(self) -> BusesConfigType:
        """Convert to typed dictionary format."""
        return BusesConfigType(
            adapter=self.BUS_ADAPTER,
        )
