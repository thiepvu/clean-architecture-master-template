"""
Application entry point.
"""

import sys

import uvicorn

from bootstrapper.app_factory import create_app
from shared.bootstrap import create_config_service, create_logger


def main():
    """Main entry point"""
    # Initialize config service and logger (bootstrap level - uses helpers)
    config_service = create_config_service()
    logger = create_logger(config_service=config_service)

    base_config = config_service.base
    logging_config = config_service.logging

    # Remove --env arguments before passing to uvicorn
    # (because uvicorn doesn't understand --env)
    filtered_args = []
    skip_next = False
    for i, arg in enumerate(sys.argv[1:]):
        if skip_next:
            skip_next = False
            continue
        if arg == "--env":
            skip_next = True
            continue
        filtered_args.append(arg)

    # Create app
    app = create_app()

    # Run with uvicorn
    uvicorn_config = {
        "app": "main:app",  # Or use app directly: app=app
        "host": base_config.HOST,
        "port": base_config.PORT,
        "reload": base_config.is_development,
        "workers": 1 if base_config.is_development else base_config.WORKERS,
        "log_level": logging_config.LOG_LEVEL.lower(),
    }

    logger.info(f"🚀 Starting server on {base_config.SERVER_URL}")
    logger.info(f"📚 Docs available at {base_config.SERVER_URL}/api/docs")
    logger.info(f"📚 Redoc available at {base_config.SERVER_URL}/api/redoc")

    uvicorn.run(**uvicorn_config)


# For direct uvicorn usage
app = create_app()


if __name__ == "__main__":
    main()
