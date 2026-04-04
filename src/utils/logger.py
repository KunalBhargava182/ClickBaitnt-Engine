"""
Structured logging setup for auto-shorts-engine.
Console output (colorized) + rotating file output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

import structlog


def setup_logger(
    name: str = "auto-shorts-engine",
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
) -> structlog.BoundLogger:
    """
    Configure and return a structured logger.

    Args:
        name: Logger name / log file basename.
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        log_dir: Directory for log files. Defaults to project logs/.

    Returns:
        A configured structlog BoundLogger instance.
    """
    if log_dir is None:
        log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "engine.log"

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Standard library logging handlers
    handlers: list[logging.Handler] = []

    # Console handler — colorized via structlog's ConsoleRenderer
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    handlers.append(console_handler)

    # Rotating file handler (10 MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    handlers.append(file_handler)

    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
        force=True,
    )

    # Structlog configuration
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=shared_processors,
    )

    for handler in handlers:
        handler.setFormatter(formatter)

    logger = structlog.get_logger(name)
    return logger


# Module-level default logger — import this everywhere
log = setup_logger()
