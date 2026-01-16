"""Logging utilities for the server."""

import logging

logger = logging.getLogger("ngui_e2e_server")


def log_info(message: str) -> None:
    """Log an info message."""
    logger.info(message)
    print(message)  # Also print for uvicorn console


def log_error(message: str) -> None:
    """Log an error message."""
    logger.error(message)
    print(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(message)
    print(message)


def log_debug(message: str) -> None:
    """Log a debug message."""
    logger.debug(message)


def log_section(title: str) -> None:
    """Log a section header."""
    separator = "=" * 60
    message = f"\n{separator}\n{title}\n{separator}"
    log_info(message)
