"""
Logging Bootstrap Helper.

Provides helper function to create Logger for bootstrap/app level code.

USAGE RESTRICTION:
─────────────────
This helper is ONLY for bootstrap/app level code:
- main.py (entry point)
- app_factory.py (app initialization)
- scripts (migrate.py, seed.py, CLI tools)
- alembic/env.py (migrations)

For module/application layer code, use DI injection:
    from shared.application.ports import ILogger

    class MyService:
        def __init__(self, logger: ILogger):
            self._logger = logger

Usage:
    from shared.bootstrap import create_logger

    # In main.py, scripts, etc.
    logger = create_logger()
    logger.info("Application started")
"""

from typing import Optional

from infrastructure.logging import LoggingModule
from shared.application.ports import IConfigService, ILogger

from .config import create_config_service

# Cached instance for bootstrap use
_bootstrap_logger: Optional[ILogger] = None


def create_logger(
    config_service: Optional[IConfigService] = None,
    name: str = "app",
) -> ILogger:
    """
    Bootstrap helper to create Logger.

    This function creates and caches a Logger instance for use
    in bootstrap/app level code. The instance is cached for performance.

    USAGE RESTRICTION:
    ─────────────────
    This function is ONLY for bootstrap/app level code:
    - main.py (entry point)
    - app_factory.py (app initialization)
    - scripts (migrate.py, seed.py, CLI tools)
    - alembic/env.py (migrations)

    For all other code, use DI injection:
        from shared.application.ports import ILogger

        class MyService:
            def __init__(self, logger: ILogger):
                self._logger = logger

    Args:
        config_service: ConfigService instance (optional, will create if not provided)
        name: Logger name (default: "app")

    Returns:
        ILogger instance (cached for performance)

    Example:
        from shared.bootstrap import create_logger

        logger = create_logger()
        logger.info("Application started")
    """
    global _bootstrap_logger

    if _bootstrap_logger is None:
        # Get or create config service
        cs = config_service or create_config_service()

        _bootstrap_logger = LoggingModule.create_logger(
            config_service=cs,
            name=name,
        )

    return _bootstrap_logger


def reset_bootstrap_logger() -> None:
    """
    Reset bootstrap logger cache.

    Useful for testing or when configuration changes.
    Call this before create_logger() to force reload.

    Example:
        from shared.bootstrap import reset_bootstrap_logger, create_logger

        reset_bootstrap_logger()
        logger = create_logger()
    """
    global _bootstrap_logger
    _bootstrap_logger = None
