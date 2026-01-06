"""
Storage Factory.

Creates storage adapters based on configuration.
Follows the Factory pattern for adapter instantiation.
"""

from typing import TYPE_CHECKING

from config.storage import (
    LocalStorageConfig,
    LocalStorageSettings,
    S3StorageConfig,
    S3StorageSettings,
)
from config.types import StorageAdapterType
from shared.application.ports.storage import IStorageService

from .adapters.local import LocalStorageAdapter
from .adapters.s3 import S3StorageAdapter

if TYPE_CHECKING:
    from shared.application.ports import IConfigService, ILogger


class StorageFactory:
    """
    Factory for creating storage adapters.

    Responsibilities:
    - Read adapter type from config
    - Load adapter-specific configuration
    - Create adapter instance
    - Initialize adapter
    - Perform health check
    - Return initialized adapter
    """

    @staticmethod
    async def create(
        adapter_type: StorageAdapterType,
        config_service: "IConfigService",
        logger: "ILogger",
    ) -> IStorageService:
        """
        Create and initialize storage adapter.

        Flow:
        1. Determine adapter type
        2. Load adapter-specific config from config layer
        3. Create adapter instance
        4. Initialize adapter
        5. Perform health check
        6. Return initialized adapter

        Args:
            adapter_type: Type of adapter to create
            config_service: Configuration service
            logger: Logger instance

        Returns:
            Initialized storage adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        storage_config = config_service.storage

        if adapter_type == StorageAdapterType.LOCAL:
            # Load local-specific settings
            local_settings = LocalStorageSettings()
            adapter_config = LocalStorageConfig.from_settings(
                local_settings,
                storage_config,
            )
            adapter = LocalStorageAdapter(adapter_config, logger)
            logger.info(
                "Creating local storage adapter",
                extra={"upload_dir": adapter_config.upload_dir},
            )

        elif adapter_type == StorageAdapterType.S3:
            # Load S3-specific settings
            s3_settings = S3StorageSettings()
            adapter_config = S3StorageConfig.from_settings(
                s3_settings,
                storage_config,
            )
            adapter = S3StorageAdapter(adapter_config, logger)
            logger.info(
                "Creating S3 storage adapter",
                extra={
                    "bucket": adapter_config.bucket,
                    "region": adapter_config.region,
                },
            )

        else:
            raise ValueError(f"Unknown storage adapter type: {adapter_type}")

        # Initialize and verify
        await adapter.initialize()

        if not await adapter.health_check():
            raise RuntimeError(f"Storage adapter health check failed for {adapter_type.value}")

        logger.info(
            f"Storage adapter initialized: {adapter_type.value}",
            extra={"adapter": adapter_type.value},
        )

        return adapter
