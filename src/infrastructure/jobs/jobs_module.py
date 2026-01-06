"""
JobsModule - Pure Jobs Composer.

This module is responsible ONLY for composing jobs instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│   JobsModule    │  ← Pure Composer
│  - load config  │     Load JobsConfig from ConfigService
│  - call factory │     Pass config to JobsFactory
└────────┬────────┘
         │ create_jobs()
         ▼
┌─────────────────┐
│  JobsFactory    │  ← Adapter Switcher
│  - read adapter │     Read adapter type from config
│  - create adapt │     Create adapter
│  - init + check │     Init + health check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IJobService    │  ← Jobs instance
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   job_service = providers.Singleton(
       JobsModule.create_jobs,
       config_service=config_service,
       logger=logger,
   )

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, jobs: IJobService):
           self._jobs = jobs
"""

from config.types import JobsAdapterType
from shared.application.ports import IConfigService, IJobService, ILogger

from .factory import JobsFactory


class JobsModule:
    """
    Pure Jobs Composer.

    Responsibilities:
    - Load JobsConfig from ConfigService
    - Read adapter type from config
    - Pass to JobsFactory
    - Return jobs instance to DI

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)
    """

    @staticmethod
    async def create_jobs(
        config_service: IConfigService,
        logger: ILogger,
    ) -> IJobService:
        """
        Create and return jobs instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            IJobService instance
        """
        # Load jobs config from ConfigService
        jobs_config = config_service.jobs

        # Read adapter type from config
        adapter_type = JobsAdapterType(jobs_config.JOBS_ADAPTER)

        # Delegate to factory
        return await JobsFactory.create(
            adapter_type=adapter_type,
            config_service=config_service,
            logger=logger,
        )
