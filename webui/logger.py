"""Structured logging configuration for See-through UI."""

import logging
import sys
from pathlib import Path

from .config import SEETHROUGH_ROOT


def setup_logger(name="seethrough_ui", level=logging.INFO):
    """Set up structured logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create log directory
    log_dir = SEETHROUGH_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_dir / "ui.log", encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# Default logger instance
logger = setup_logger()