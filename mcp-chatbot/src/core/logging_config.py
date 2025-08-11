"""
Enhanced logging configuration for AWS MCP Agent
Provides detailed, colorful console output for debugging
"""

import logging
import sys
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the log level
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Add color to specific prefixes
        prefixes = {
            '🎯': '\033[94m',  # Blue
            '🧠': '\033[95m',  # Magenta
            '🔧': '\033[96m',  # Cyan
            '📋': '\033[37m',  # White
            '✅': '\033[92m',  # Bright Green
            '❌': '\033[91m',  # Bright Red
            '⚠️': '\033[93m',  # Bright Yellow
            '📤': '\033[94m',  # Blue
            '📥': '\033[94m',  # Blue
            '🤖': '\033[95m',  # Magenta
        }
        
        for prefix, color in prefixes.items():
            if prefix in formatted:
                formatted = formatted.replace(prefix, f"{color}{prefix}{self.COLORS['RESET']}")
        
        return formatted


def setup_enhanced_logging(level: str = "INFO") -> None:
    """
    Set up enhanced logging with colors and detailed formatting.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels for detailed debugging
    loggers_config = {
        'core.agent': numeric_level,
        'core.isolated_mcp_client': numeric_level,
        'core.async_handler': numeric_level,
        '__main__': numeric_level,
        'streamlit': logging.WARNING,  # Reduce Streamlit noise
        'urllib3': logging.WARNING,    # Reduce HTTP noise
        'botocore': logging.WARNING,   # Reduce AWS SDK noise
    }
    
    for logger_name, logger_level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(logger_level)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 [LOGGING] Enhanced logging configured at {level} level")
    logger.info(f"🔧 [LOGGING] Console output with colors enabled")


def log_separator(title: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log a visual separator with title.
    
    Args:
        title: Title for the separator
        logger: Logger to use (defaults to root logger)
    """
    if logger is None:
        logger = logging.getLogger()
    
    separator = "=" * 60
    logger.info(f"\n{separator}")
    logger.info(f"🎯 {title}")
    logger.info(f"{separator}")


def log_step(step_number: int, description: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log a numbered step.
    
    Args:
        step_number: Step number
        description: Step description
        logger: Logger to use (defaults to root logger)
    """
    if logger is None:
        logger = logging.getLogger()
    
    logger.info(f"📋 Step {step_number}: {description}")


def log_result(success: bool, message: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Log a result with appropriate icon.
    
    Args:
        success: Whether the operation was successful
        message: Result message
        logger: Logger to use (defaults to root logger)
    """
    if logger is None:
        logger = logging.getLogger()
    
    icon = "✅" if success else "❌"
    logger.info(f"{icon} {message}")
