from flask import Flask
from loguru import logger
import sys
import os

def init_extensions(_: Flask) -> None:
    """Initialize Flask extensions and logging."""

    # Ensure logs directory exists
    logs_dir = "logs"
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        # If directory cannot be created, fall back to stdout-only logging
        print(f"Warning: Could not create logs directory '{logs_dir}': {e}")
        logs_dir = None

    # Reset existing handlers
    logger.remove()

    # Console logging
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # File logging only if directory is available
    if logs_dir:
        logger.add(
            os.path.join(logs_dir, "app.log"),
            rotation="5 MB",
            retention="7 days",
            compression="zip",
            level="DEBUG",
            enqueue=True  # safer when multiple requests write logs
        )

    logger.info("Extensions initialized")
