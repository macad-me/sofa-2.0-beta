
import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


"""
Centralized logging configuration for the SOFA project.
"""
import os
import sys
import logging
from loguru import logger

# Remove default handler
logger.remove()

# Default log level mapping
VERBOSITY_LEVELS = {
    0: "WARNING",  # Default: show only warnings and errors
    1: "INFO",     # -v: show info and above
    2: "DEBUG",    # -vv: show debug and above
    3: "TRACE"     # -vvv: show trace (very detailed logging)
}

# Create a class to intercept standard logging messages and redirect to loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def configure_logger(verbosity=0):
    """
    Configure the logger based on verbosity level.
    
    Args:
        verbosity: Integer representing verbosity level (0-3)
    """
    # Remove any existing handlers
    logger.remove()
    
    # Cap verbosity at maximum defined level
    if verbosity > max(VERBOSITY_LEVELS.keys()):
        verbosity = max(VERBOSITY_LEVELS.keys())
    
    # Get the corresponding log level
    log_level = VERBOSITY_LEVELS.get(verbosity, "WARNING")
    
    # Add console handler with appropriate level
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler (always keep more detailed logs in the file)
    log_dir = os.getenv("SOFA_LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "sofa.log")
    
    logger.add(
        log_file,
        rotation="10 MB",
        retention="1 week",
        level="DEBUG",  # File logs can be more detailed
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Configure standard logging to use our interceptor
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Log the configured level
    logger.debug(f"Logging configured with console level: {log_level}")

def get_logger(name=None):
    """
    Returns a configured logger instance.
    
    Args:
        name: Optional name for the logger, typically __name__
        
    Returns:
        A configured Loguru logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
