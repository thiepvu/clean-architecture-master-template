"""
Log Formatters.

Extracted from logger.py for reuse across adapters.
"""

import json
import logging
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            record.levelname = colored_levelname

        formatted = super().format(record)
        record.levelname = levelname
        return formatted


class LevelFilter(logging.Filter):
    """Filter to only allow specific log levels."""

    def __init__(self, min_level: int, max_level: int):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


class CleanupRotatingFileHandler(RotatingFileHandler):
    """Enhanced RotatingFileHandler with automatic old file cleanup."""

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 10 * 1024 * 1024,
        backupCount: int = 5,
        encoding: Optional[str] = None,
        delay: bool = False,
        retention_days: int = 30,
    ):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.retention_days = retention_days
        self.cleanup_old_logs()

    def cleanup_old_logs(self):
        """Remove log files older than retention_days."""
        try:
            log_dir = Path(self.baseFilename).parent
            pattern = f"{Path(self.baseFilename).stem}*.log*"

            current_time = time.time()
            retention_seconds = self.retention_days * 24 * 60 * 60

            for log_file in log_dir.glob(pattern):
                if log_file.is_file():
                    file_age = current_time - log_file.stat().st_mtime
                    if file_age > retention_seconds:
                        try:
                            log_file.unlink()
                        except Exception:
                            pass
        except Exception:
            pass

    def doRollover(self):
        super().doRollover()
        self.cleanup_old_logs()


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """Enhanced TimedRotatingFileHandler with automatic cleanup."""

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 30,
        encoding: Optional[str] = None,
        delay: bool = False,
        utc: bool = True,
        retention_days: int = 30,
    ):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)
        self.retention_days = retention_days
        self.cleanup_old_logs()

    def cleanup_old_logs(self):
        """Remove log files older than retention_days."""
        try:
            log_dir = Path(self.baseFilename).parent
            pattern = f"{Path(self.baseFilename).stem}*.log*"

            current_time = time.time()
            retention_seconds = self.retention_days * 24 * 60 * 60

            for log_file in log_dir.glob(pattern):
                if log_file.is_file():
                    file_age = current_time - log_file.stat().st_mtime
                    if file_age > retention_seconds:
                        try:
                            log_file.unlink()
                        except Exception:
                            pass
        except Exception:
            pass

    def doRollover(self):
        super().doRollover()
        self.cleanup_old_logs()


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    retention_days: int = 30,
    separate_error_log: bool = True,
    use_daily_rotation: bool = True,
) -> None:
    """Setup application logging configuration."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    console_formatter: Union[JSONFormatter, ColoredFormatter]
    if format_type == "json":
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handlers
    formatter = JSONFormatter()
    log_levels = {
        "all": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    for log_name, log_level in log_levels.items():
        if log_level < getattr(logging, level.upper()):
            continue

        if log_name in ["error", "critical"] and not separate_error_log:
            continue

        if log_name not in ["all", "error", "critical"] and not separate_error_log:
            continue

        log_file = log_path / f"{log_name}.log"

        file_handler: Union[DailyRotatingFileHandler, CleanupRotatingFileHandler]
        if use_daily_rotation:
            file_handler = DailyRotatingFileHandler(
                filename=str(log_file),
                when="midnight",
                interval=1,
                backupCount=backup_count,
                encoding="utf-8",
                utc=True,
                retention_days=retention_days,
            )
            file_handler.suffix = "%Y-%m-%d"
        else:
            file_handler = CleanupRotatingFileHandler(
                filename=str(log_file),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
                retention_days=retention_days,
            )

        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        if log_name != "all":
            file_handler.addFilter(LevelFilter(log_level, log_level))

        logger.addHandler(file_handler)

    # Suppress noisy loggers
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
