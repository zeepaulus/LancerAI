"""Production-grade logging with UTF-8 console output and rotating file handler.

Provides a centralized logger factory that ensures consistent formatting,
proper Vietnamese character support on Windows, and automatic log rotation.

Usage:
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Khởi tạo thành công")
"""

import codecs
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

_LOG_DIR = "logs"
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
_BACKUP_COUNT = 5
_INITIALIZED_LOGGERS: set[str] = set()

# Format strings
_CONSOLE_FORMAT = (
    "\033[36m%(asctime)s\033[0m | \033[32m%(levelname)-8s\033[0m | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
_FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"


def get_logger(name: str, console_level: str = "DEBUG", file_level: str = "DEBUG") -> logging.Logger:
    """Create or retrieve a named logger with console and file handlers.

    Features:
    - UTF-8 console output (critical for Vietnamese text on Windows).
    - Rotating file handler (10MB per file, 5 backups).
    - Color-coded console output for quick visual scanning.
    - Prevents duplicate handler attachment on repeated calls.

    Args:
        name: Logger name, typically `__name__` of the calling module.
        console_level: Minimum log level for console output.
        file_level: Minimum log level for file output.
    """
    if name in _INITIALIZED_LOGGERS:
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # --- Console Handler (UTF-8 for Vietnamese support) ---
    try:
        utf8_writer: Any = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
        console_handler = logging.StreamHandler(utf8_writer)
    except Exception:
        console_stream: Any = sys.stdout
        console_handler = logging.StreamHandler(console_stream)

    console_handler.setLevel(getattr(logging, console_level.upper(), logging.DEBUG))
    console_handler.setFormatter(logging.Formatter(_CONSOLE_FORMAT, datefmt="%H:%M:%S"))
    logger.addHandler(console_handler)

    # --- File Handler (Rotating) ---
    try:
        log_dir = Path(_LOG_DIR)
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{name.replace('.', '_')}.log",
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
        file_handler.setFormatter(logging.Formatter(_FILE_FORMAT))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")

    _INITIALIZED_LOGGERS.add(name)
    return logger
