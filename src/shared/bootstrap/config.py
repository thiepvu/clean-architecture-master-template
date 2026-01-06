"""
Configuration Bootstrap Helper.

Provides helper function to create ConfigService for bootstrap/app level code.

USAGE RESTRICTION:
─────────────────
This helper is ONLY for bootstrap/app level code:
- main.py (entry point)
- app_factory.py (app initialization)
- scripts (migrate.py, seed.py, CLI tools)
- alembic/env.py (migrations)

For module/application layer code, use DI injection:
    from shared.application.ports import IConfigService

    class MyService:
        def __init__(self, config_service: IConfigService):
            self._config = config_service

Usage:
    from shared.bootstrap import create_config_service

    # In main.py, scripts, etc.
    config_service = create_config_service()
    db_url = config_service.database.DATABASE_URL
"""

from typing import Optional

from infrastructure.config import ConfigModule
from shared.application.ports import IConfigService

# Cached instance for bootstrap use
_bootstrap_config_service: Optional[IConfigService] = None


def create_config_service(environment: Optional[str] = None) -> IConfigService:
    """
    Bootstrap helper to create ConfigService.

    This function creates and caches a ConfigService instance for use
    in bootstrap/app level code. The instance is cached for performance.

    USAGE RESTRICTION:
    ─────────────────
    This function is ONLY for bootstrap/app level code:
    - main.py (entry point)
    - app_factory.py (app initialization)
    - scripts (migrate.py, seed.py, CLI tools)
    - alembic/env.py (migrations)

    For all other code, use DI injection:
        from shared.application.ports import IConfigService

        class MyService:
            def __init__(self, config_service: IConfigService):
                self._config = config_service

    Args:
        environment: Override environment detection (optional)

    Returns:
        IConfigService instance (cached for performance)

    Example:
        from shared.bootstrap import create_config_service

        config_service = create_config_service()
        db_url = config_service.database.DATABASE_URL
    """
    global _bootstrap_config_service

    if _bootstrap_config_service is None:
        _bootstrap_config_service = ConfigModule.create_service(environment)

    return _bootstrap_config_service


def reset_bootstrap_config() -> None:
    """
    Reset bootstrap config cache.

    Useful for testing or when environment changes.
    Call this before create_config_service() to force reload.

    Example:
        from shared.bootstrap import reset_bootstrap_config, create_config_service

        reset_bootstrap_config()
        config_service = create_config_service("testing")
    """
    global _bootstrap_config_service
    _bootstrap_config_service = None
