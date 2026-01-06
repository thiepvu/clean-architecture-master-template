"""
Jobs Factory.

Creates jobs adapters based on configuration.
Supports: Redis Celery, In-Memory
"""

from config.jobs import InMemoryJobsConfig, RedisCeleryJobsConfig, RedisCeleryJobsSettings
from config.types import JobsAdapterType
from shared.application.ports import IConfigService, IJobService, ILogger


class JobsFactory:
    """
    Factory for creating jobs adapters.

    Creates and initializes the appropriate jobs adapter
    based on configuration. Performs health check before returning.

    Example:
        jobs = await JobsFactory.create(
            adapter_type=JobsAdapterType.REDIS_CELERY,
            config_service=config_service,
            logger=logger,
        )
    """

    @staticmethod
    async def create(
        adapter_type: JobsAdapterType,
        config_service: IConfigService,
        logger: ILogger,
    ) -> IJobService:
        """
        Create and initialize jobs adapter.

        Args:
            adapter_type: Type of jobs adapter to create
            config_service: ConfigService instance
            logger: Logger instance

        Returns:
            Initialized jobs adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        logger.info(f"🔧 Creating jobs adapter: {adapter_type.value}")

        if adapter_type == JobsAdapterType.REDIS_CELERY:
            from .adapters.redis_celery import RedisCeleryJobAdapter

            # Factory loads adapter-specific config from config layer
            jobs_config = config_service.jobs
            celery_settings = RedisCeleryJobsSettings()
            adapter_config = RedisCeleryJobsConfig.from_settings(celery_settings, jobs_config)

            # Adapter only receives config and implements
            adapter = RedisCeleryJobAdapter(adapter_config, logger)

        elif adapter_type == JobsAdapterType.IN_MEMORY:
            from .adapters.in_memory import InMemoryJobAdapter

            # Factory loads adapter-specific config
            jobs_config = config_service.jobs
            adapter_config = InMemoryJobsConfig.from_config(jobs_config)

            adapter = InMemoryJobAdapter(adapter_config, logger)

        else:
            raise ValueError(f"Unknown jobs adapter type: {adapter_type}")

        # Initialize adapter
        await adapter.initialize()

        # Verify health
        if not await adapter.health_check():
            raise RuntimeError(f"Jobs adapter health check failed: {adapter_type.value}")

        logger.info(f"✅ Jobs adapter ready: {adapter_type.value}")
        return adapter
