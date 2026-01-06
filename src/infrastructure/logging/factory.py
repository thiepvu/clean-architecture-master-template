"""
Logger Factory.

Adapter switcher for logging - creates the appropriate logger adapter
based on adapter type from config.

Architecture:
─────────────
LoggerFactory receives LoggingConfig from LoggingModule:
- Reads adapter type from config.LOG_ADAPTER
- Loads adapter-specific config (e.g., StandardLoggerConfig)
- Creates adapter with specific config
- Init + health check
- Returns adapter instance

Usage:
    # Called by LoggingModule (internal)
    logger = LoggerFactory.create(
        logging_config=logging_config,
        name="app",
    )
"""

from typing import Any

from config.logging import StandardLoggerConfig
from shared.application.ports import ILogger

from .adapters.standard import StandardLoggerAdapter


class LoggerFactory:
    """
    Factory for creating logger adapters.

    This is the adapter switcher:
    - Receives LoggingConfig from LoggingModule
    - Reads adapter type from config.LOG_ADAPTER
    - Loads adapter-specific config
    - Creates adapter with specific config (adapter only implements)
    - Init + health check
    - Returns adapter instance

    Called by LoggingModule, not directly by DI Container.
    """

    @staticmethod
    def create(
        logging_config: Any,  # LoggingConfig from config.logging
        name: str = "app",
    ) -> ILogger:
        """
        Create and initialize logger adapter.

        Args:
            logging_config: LoggingConfig instance (from config.logging)
            name: Logger name

        Returns:
            Initialized logger adapter implementing ILogger

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        # Read adapter type from config (Literal["standard", "structlog"])
        adapter_type = logging_config.LOG_ADAPTER

        if adapter_type == "standard":
            # Factory loads specific config from LoggingConfig
            adapter_config = StandardLoggerConfig.from_config(logging_config)

            # Adapter only receives config and implements
            adapter = StandardLoggerAdapter(
                config=adapter_config,
                name=name,
            )

        # Future adapters:
        # elif adapter_type == "structlog":
        #     adapter_config = StructlogConfig.from_config(logging_config)
        #     adapter = StructlogAdapter(config=adapter_config, name=name)

        else:
            raise ValueError(f"Unknown logger adapter type: {adapter_type}")

        # Initialize adapter
        adapter.initialize()

        # Verify health (fail-fast)
        if not adapter.health_check():
            raise RuntimeError(f"Logger adapter health check failed: {adapter_type}")

        adapter.info(f"✅ Logger adapter ready: {adapter_type}")
        return adapter
