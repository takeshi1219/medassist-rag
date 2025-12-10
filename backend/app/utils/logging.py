"""Logging configuration."""
import sys
from loguru import logger

from app.config import settings


def setup_logging():
    """Configure loguru logging."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler for production
    if settings.environment == "production":
        logger.add(
            "logs/medassist_{time}.log",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            format=log_format,
            level="INFO"
        )
    
    return logger

