"""
Storage Module.

Pure composer for storage service creation.
Follows the Module pattern for DI composition.
"""

from typing import TYPE_CHECKING

from config.types import StorageAdapterType
from shared.application.ports.storage import IStorageService

from .factory import StorageFactory

if TYPE_CHECKING:
    from shared.application.ports import IConfigService, ILogger


class StorageModule:
    """
    Pure Storage Composer - No singleton management.

    Responsibilities:
    - Load StorageConfig from ConfigService
    - Read adapter type from config
    - Delegate to StorageFactory
    - Return storage instance

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)

    Usage:
        # In DI container
        storage_service = providers.Singleton(
            StorageModule.create_storage,
            config_service=config_service,
            logger=logger,
        )

        # Direct usage
        storage = await StorageModule.create_storage(
            config_service=config_service,
            logger=logger,
        )
    """

    @staticmethod
    async def create_storage(
        config_service: "IConfigService",
        logger: "ILogger",
    ) -> IStorageService:
        """
        Create and return storage instance.

        Flow:
        1. Load StorageConfig from ConfigService
        2. Read adapter type from config
        3. Delegate to StorageFactory
        4. Return storage instance

        Args:
            config_service: Configuration service
            logger: Logger instance

        Returns:
            Initialized storage service
        """
        storage_config = config_service.storage
        adapter_type = StorageAdapterType(storage_config.STORAGE_ADAPTER)

        logger.info(
            f"Creating storage service with adapter: {adapter_type.value}",
            extra={"adapter": adapter_type.value},
        )

        return await StorageFactory.create(
            adapter_type=adapter_type,
            config_service=config_service,
            logger=logger,
        )
