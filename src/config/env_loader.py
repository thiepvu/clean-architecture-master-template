"""
Environment Detection and .env File Loader

This module provides centralized environment detection and .env file loading.
It should be called ONCE at application startup by ConfigModule.

Priority for environment detection:
1. CLI argument: --env <environment>
2. OS environment variable: ENVIRONMENT
3. Default: development

.env file loading order (later files override earlier):
1. .env (base)
2. .env.{environment}
3. .env.local (local overrides, git-ignored)
4. .env.{environment}.local
"""

import os
import sys
from typing import List, Optional

from dotenv import load_dotenv

# Track if env has been loaded to prevent double loading
_env_loaded = False
_detected_environment: Optional[str] = None


def detect_environment(default: str = "development") -> str:
    """
    Detect environment with priority:
    1. CLI argument: --env
    2. OS environment variable: ENVIRONMENT
    3. Default: development

    Returns:
        Environment string (development, testing, staging, production)
    """
    global _detected_environment

    if _detected_environment is not None:
        return _detected_environment

    # 1. Check CLI argument
    if "--env" in sys.argv:
        try:
            idx = sys.argv.index("--env") + 1
            if idx < len(sys.argv):
                _detected_environment = sys.argv[idx]
                return _detected_environment
        except (ValueError, IndexError):
            pass

    # 2. Check OS environment variable
    env_var = os.getenv("ENVIRONMENT")
    if env_var:
        _detected_environment = env_var
        return _detected_environment

    # 3. Use default
    _detected_environment = default
    return _detected_environment


def load_env_files(environment: Optional[str] = None, force: bool = False) -> List[str]:
    """
    Load .env files in correct order.
    Later files override earlier ones.

    Args:
        environment: Environment name. If None, will detect automatically.
        force: Force reload even if already loaded.

    Returns:
        List of loaded file paths.

    Order (same as Nest.js/Next.js):
    1. .env (base)
    2. .env.{environment}
    3. .env.local (local overrides)
    4. .env.{environment}.local
    """
    global _env_loaded

    if _env_loaded and not force:
        return []

    env = environment or detect_environment()

    env_files = [
        ".env",
        f".env.{env}",
        ".env.local",
        f".env.{env}.local",
    ]

    loaded_files = []
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            loaded_files.append(env_file)

    _env_loaded = True
    return loaded_files


def get_environment() -> str:
    """
    Get the detected environment.
    Will detect if not already done.

    Returns:
        Environment string
    """
    return detect_environment()


def is_env_loaded() -> bool:
    """Check if env files have been loaded."""
    return _env_loaded


def reset_env_state() -> None:
    """
    Reset env loading state.
    Useful for testing.
    """
    global _env_loaded, _detected_environment
    _env_loaded = False
    _detected_environment = None
