"""
Bootstrap Helpers.

Provides helper functions for application bootstrap/startup code.
These helpers are ONLY for use in:
- main.py (entry point)
- app_factory.py (app initialization)
- scripts (migrate.py, seed.py, CLI tools)
- alembic/env.py (migrations)

For module/application layer code, use DI injection instead.

Usage:
    from shared.bootstrap import create_config_service, create_logger

    # In main.py, scripts, etc.
    config_service = create_config_service()
    logger = create_logger()
"""

from .config import create_config_service, reset_bootstrap_config
from .logging import create_logger, reset_bootstrap_logger

__all__ = [
    # Config
    "create_config_service",
    "reset_bootstrap_config",
    # Logging
    "create_logger",
    "reset_bootstrap_logger",
]
