"""
Events configuration - Common/Port interface.

This is the PORT that defines what all event bus adapters need.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import EventsConfigType


class EventsConfig(BaseSettings):
    """
    Common events configuration (Port interface).

    This config is used to select which event bus adapter to use.
    Adapter-specific configs extend this.

    Environment Variables:
        EVENT_BUS_ADAPTER: Event bus adapter type (in_memory | rabbitmq | kafka)
    """

    EVENT_BUS_ADAPTER: Literal["in_memory", "rabbitmq", "kafka"] = Field(
        default="in_memory",
        description="Event bus adapter: in_memory | rabbitmq | kafka",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_in_memory(self) -> bool:
        """Check if using in-memory adapter."""
        return self.EVENT_BUS_ADAPTER == "in_memory"

    @property
    def is_rabbitmq(self) -> bool:
        """Check if using RabbitMQ adapter."""
        return self.EVENT_BUS_ADAPTER == "rabbitmq"

    @property
    def is_kafka(self) -> bool:
        """Check if using Kafka adapter."""
        return self.EVENT_BUS_ADAPTER == "kafka"

    def to_dict(self) -> EventsConfigType:
        """Convert to typed dictionary format."""
        return EventsConfigType(
            adapter=self.EVENT_BUS_ADAPTER,
        )
