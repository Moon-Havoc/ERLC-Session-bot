"""Structured logging utility for SessionCore."""

import logging
import sys
from typing import Optional
from pathlib import Path

from config import config


class StructuredLogger:
    """Structured logger with consistent formatting."""
    
    def __init__(self, name: str, log_file: Optional[str] = None) -> None:
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.log_level))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file or config.log_file:
            file_path = Path(log_file or config.log_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(getattr(logging, config.log_level))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get or create a logger for a specific module."""
    return StructuredLogger(name)
