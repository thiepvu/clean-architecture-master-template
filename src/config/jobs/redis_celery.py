"""
Redis Celery jobs adapter configuration.

This is the ADAPTER-specific config for Redis Celery jobs.
Includes both Redis connection settings and Celery-specific settings.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import RedisCeleryJobsConfigType

if TYPE_CHECKING:
    from config.jobs import JobsConfig


class RedisCeleryJobsSettings(BaseSettings):
    """
    Redis Celery connection settings loaded from environment.

    Environment Variables:
        # Broker (Redis)
        CELERY_BROKER_HOST: Redis broker host
        CELERY_BROKER_PORT: Redis broker port
        CELERY_BROKER_DB: Redis broker database number
        CELERY_BROKER_USERNAME: Redis broker username
        CELERY_BROKER_PASSWORD: Redis broker password
        CELERY_BROKER_SSL: Enable SSL/TLS for broker

        # Backend (Redis)
        CELERY_BACKEND_HOST: Redis backend host
        CELERY_BACKEND_PORT: Redis backend port
        CELERY_BACKEND_DB: Redis backend database number
        CELERY_BACKEND_USERNAME: Redis backend username
        CELERY_BACKEND_PASSWORD: Redis backend password
        CELERY_BACKEND_SSL: Enable SSL/TLS for backend

        # Celery settings
        CELERY_TASK_SERIALIZER: Task serialization format
        CELERY_RESULT_SERIALIZER: Result serialization format
        CELERY_ACCEPT_CONTENT: Accepted content types (comma-separated)
        CELERY_TIMEZONE: Celery timezone
        CELERY_TASK_TRACK_STARTED: Track task started state
        CELERY_TASK_TIME_LIMIT: Hard time limit for tasks
        CELERY_TASK_SOFT_TIME_LIMIT: Soft time limit for tasks
        CELERY_WORKER_PREFETCH_MULTIPLIER: Worker prefetch multiplier
        CELERY_WORKER_CONCURRENCY: Worker concurrency
        CELERY_RESULT_EXPIRES: Result expiration in seconds
    """

    # Broker (Redis)
    CELERY_BROKER_HOST: str = Field(default="localhost", description="Broker host")
    CELERY_BROKER_PORT: int = Field(default=6379, ge=1, le=65535, description="Broker port")
    CELERY_BROKER_DB: int = Field(default=1, ge=0, le=15, description="Broker DB number")
    CELERY_BROKER_USERNAME: Optional[str] = Field(default=None, description="Broker username")
    CELERY_BROKER_PASSWORD: Optional[str] = Field(default=None, description="Broker password")
    CELERY_BROKER_SSL: bool = Field(default=False, description="Enable SSL for broker")

    # Backend (Redis)
    CELERY_BACKEND_HOST: str = Field(default="localhost", description="Backend host")
    CELERY_BACKEND_PORT: int = Field(default=6379, ge=1, le=65535, description="Backend port")
    CELERY_BACKEND_DB: int = Field(default=2, ge=0, le=15, description="Backend DB number")
    CELERY_BACKEND_USERNAME: Optional[str] = Field(default=None, description="Backend username")
    CELERY_BACKEND_PASSWORD: Optional[str] = Field(default=None, description="Backend password")
    CELERY_BACKEND_SSL: bool = Field(default=False, description="Enable SSL for backend")

    # Celery settings
    CELERY_TASK_SERIALIZER: str = Field(default="json", description="Task serializer")
    CELERY_RESULT_SERIALIZER: str = Field(default="json", description="Result serializer")
    CELERY_ACCEPT_CONTENT: str = Field(default="json", description="Accepted content types")
    CELERY_TIMEZONE: str = Field(default="UTC", description="Timezone")
    CELERY_TASK_TRACK_STARTED: bool = Field(default=True, description="Track started state")
    CELERY_TASK_TIME_LIMIT: int = Field(default=300, ge=1, description="Hard time limit")
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=270, ge=1, description="Soft time limit")
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = Field(
        default=1, ge=1, description="Prefetch multiplier"
    )
    CELERY_WORKER_CONCURRENCY: int = Field(default=4, ge=1, description="Worker concurrency")
    CELERY_RESULT_EXPIRES: int = Field(default=86400, ge=1, description="Result expiration")

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )


@dataclass
class RedisCeleryJobsConfig:
    """
    Redis Celery jobs adapter configuration.

    Contains all settings needed to connect to Redis as Celery broker/backend.
    Created from RedisCeleryJobsSettings + JobsConfig.
    """

    # Broker (Redis)
    broker_host: str
    broker_port: int
    broker_db: int
    broker_password: Optional[str]
    broker_username: Optional[str]
    broker_ssl: bool

    # Backend (Redis)
    backend_host: str
    backend_port: int
    backend_db: int
    backend_password: Optional[str]
    backend_username: Optional[str]
    backend_ssl: bool

    # Celery settings
    task_serializer: str
    result_serializer: str
    accept_content: list[str] = field(default_factory=lambda: ["json"])
    timezone: str = "UTC"
    task_track_started: bool = True
    task_time_limit: int = 300
    task_soft_time_limit: int = 270
    worker_prefetch_multiplier: int = 1
    worker_concurrency: int = 4
    result_expires: int = 86400

    # Jobs settings
    default_queue: str = "default"
    default_max_retries: int = 3
    default_timeout: int = 300

    @property
    def broker_url(self) -> str:
        """Build Redis broker connection URL."""
        auth = ""
        if self.broker_username and self.broker_password:
            auth = f"{self.broker_username}:{self.broker_password}@"
        elif self.broker_password:
            auth = f":{self.broker_password}@"

        protocol = "rediss" if self.broker_ssl else "redis"
        return f"{protocol}://{auth}{self.broker_host}:{self.broker_port}/{self.broker_db}"

    @property
    def backend_url(self) -> str:
        """Build Redis backend connection URL."""
        auth = ""
        if self.backend_username and self.backend_password:
            auth = f"{self.backend_username}:{self.backend_password}@"
        elif self.backend_password:
            auth = f":{self.backend_password}@"

        protocol = "rediss" if self.backend_ssl else "redis"
        return f"{protocol}://{auth}{self.backend_host}:{self.backend_port}/{self.backend_db}"

    @classmethod
    def from_settings(
        cls,
        celery_settings: RedisCeleryJobsSettings,
        jobs_config: "JobsConfig",
    ) -> "RedisCeleryJobsConfig":
        """
        Create from RedisCeleryJobsSettings and JobsConfig.

        Args:
            celery_settings: Redis Celery connection settings
            jobs_config: Jobs common configuration

        Returns:
            RedisCeleryJobsConfig instance
        """
        accept_content = [c.strip() for c in celery_settings.CELERY_ACCEPT_CONTENT.split(",")]

        return cls(
            broker_host=celery_settings.CELERY_BROKER_HOST,
            broker_port=celery_settings.CELERY_BROKER_PORT,
            broker_db=celery_settings.CELERY_BROKER_DB,
            broker_password=celery_settings.CELERY_BROKER_PASSWORD,
            broker_username=celery_settings.CELERY_BROKER_USERNAME,
            broker_ssl=celery_settings.CELERY_BROKER_SSL,
            backend_host=celery_settings.CELERY_BACKEND_HOST,
            backend_port=celery_settings.CELERY_BACKEND_PORT,
            backend_db=celery_settings.CELERY_BACKEND_DB,
            backend_password=celery_settings.CELERY_BACKEND_PASSWORD,
            backend_username=celery_settings.CELERY_BACKEND_USERNAME,
            backend_ssl=celery_settings.CELERY_BACKEND_SSL,
            task_serializer=celery_settings.CELERY_TASK_SERIALIZER,
            result_serializer=celery_settings.CELERY_RESULT_SERIALIZER,
            accept_content=accept_content,
            timezone=celery_settings.CELERY_TIMEZONE,
            task_track_started=celery_settings.CELERY_TASK_TRACK_STARTED,
            task_time_limit=celery_settings.CELERY_TASK_TIME_LIMIT,
            task_soft_time_limit=celery_settings.CELERY_TASK_SOFT_TIME_LIMIT,
            worker_prefetch_multiplier=celery_settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
            worker_concurrency=celery_settings.CELERY_WORKER_CONCURRENCY,
            result_expires=celery_settings.CELERY_RESULT_EXPIRES,
            default_queue=jobs_config.JOBS_DEFAULT_QUEUE,
            default_max_retries=jobs_config.JOBS_DEFAULT_MAX_RETRIES,
            default_timeout=jobs_config.JOBS_DEFAULT_TIMEOUT,
        )

    def to_dict(self) -> RedisCeleryJobsConfigType:
        """Convert to typed dictionary format."""
        return RedisCeleryJobsConfigType(
            broker_host=self.broker_host,
            broker_port=self.broker_port,
            broker_db=self.broker_db,
            broker_password=self.broker_password,
            broker_username=self.broker_username,
            broker_ssl=self.broker_ssl,
            backend_host=self.backend_host,
            backend_port=self.backend_port,
            backend_db=self.backend_db,
            backend_password=self.backend_password,
            backend_username=self.backend_username,
            backend_ssl=self.backend_ssl,
            task_serializer=self.task_serializer,
            result_serializer=self.result_serializer,
            accept_content=self.accept_content,
            timezone=self.timezone,
            task_track_started=self.task_track_started,
            task_time_limit=self.task_time_limit,
            task_soft_time_limit=self.task_soft_time_limit,
            worker_prefetch_multiplier=self.worker_prefetch_multiplier,
            worker_concurrency=self.worker_concurrency,
            result_expires=self.result_expires,
            default_queue=self.default_queue,
            default_max_retries=self.default_max_retries,
            default_timeout=self.default_timeout,
            broker_url=self.broker_url,
            backend_url=self.backend_url,
        )
