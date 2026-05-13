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
import os
import sys
from pathlib import Path
from typing import Any

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
_BACKUP_COUNT = 5

# Format strings
_CONSOLE_FORMAT = (
    "\033[36m%(asctime)s\033[0m | \033[32m%(levelname)-8s\033[0m | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
_FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"


def _log_dir_for_files() -> Path | None:
    """Directory for rotating log files, or None when file logging is disabled."""
    flag = os.environ.get("LOG_TO_FILE", "true").strip().lower()
    if flag in ("0", "false", "no"):
        return None
    override = os.environ.get("LOG_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent.parent.parent / "logs"


def get_logger(name: str, console_level: str = "DEBUG", file_level: str = "DEBUG") -> logging.Logger:
    """Create or retrieve a named logger with console and file handlers.

    Features:
    - UTF-8 console output (critical for Vietnamese text on Windows).
    - Rotating file handler (10MB per file, 5 backups).
    - Color-coded console output for quick visual scanning.
    - Thread-safe: uses stdlib's logger.handlers to prevent duplicate attachment.

    Args:
        name: Logger name, typically `__name__` of the calling module.
        console_level: Minimum log level for console output.
        file_level: Minimum log level for file output.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

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
    log_dir = _log_dir_for_files()
    if log_dir is None:
        return logger

    try:
        log_dir.mkdir(parents=True, exist_ok=True)

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
        logger.warning("Could not create file handler: %s", e)

    return logger
