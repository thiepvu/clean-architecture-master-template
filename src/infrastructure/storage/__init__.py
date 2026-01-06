"""
Storage Infrastructure Module.

Provides file storage capabilities with Port & Adapter pattern.

Adapters:
- LocalStorageAdapter: Local filesystem storage (default)
- S3StorageAdapter: AWS S3 / S3-compatible storage

Usage:
──────
# Via DI Container (Recommended)
storage_service = providers.Singleton(
    StorageModule.create_storage,
    config_service=config_service,
    logger=logger,
)

# Direct Factory Usage
from infrastructure.storage import StorageFactory
from config.types import StorageAdapterType

storage = await StorageFactory.create(
    adapter_type=StorageAdapterType.LOCAL,
    config_service=config_service,
    logger=logger,
)

# Direct Adapter Usage (Development)
from infrastructure.storage import LocalStorageAdapter
from config.storage import LocalStorageConfig, LocalStorageSettings, StorageConfig

storage_config = StorageConfig()
local_settings = LocalStorageSettings()
config = LocalStorageConfig.from_settings(local_settings, storage_config)
storage = LocalStorageAdapter(config, logger)
await storage.initialize()

Configuration:
─────────────
Environment variables:
- STORAGE_ADAPTER: "local" or "s3" (default: "local")
- UPLOAD_DIR: Upload directory for local storage (default: "uploads")
- S3_BUCKET: S3 bucket name (required for S3)
- S3_REGION: AWS region (default: "us-east-1")
- AWS_ACCESS_KEY_ID: AWS credentials (optional, uses IAM if not set)
- AWS_SECRET_ACCESS_KEY: AWS credentials

See config/storage/ for full configuration options.
"""

# Adapters (for direct usage or testing)
from .adapters import LocalStorageAdapter, S3StorageAdapter

# Factory (for direct creation)
from .factory import StorageFactory

# Module (primary interface for DI)
from .storage_module import StorageModule

__all__ = [
    # Module (primary interface)
    "StorageModule",
    # Factory
    "StorageFactory",
    # Adapters
    "LocalStorageAdapter",
    "S3StorageAdapter",
]
