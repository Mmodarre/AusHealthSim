"""
Centralized logging configuration for the Health Insurance AU simulation.
"""
import os
import logging
import sys

# Default log level is INFO, but can be overridden with environment variable
DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def get_log_level():
    """Get the log level from environment variable or use default."""
    env_level = os.environ.get('HEALTH_INSURANCE_LOG_LEVEL', '').upper()
    if env_level in LOG_LEVELS:
        return LOG_LEVELS[env_level]
    return DEFAULT_LOG_LEVEL

def configure_logging(level=None, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        level: Log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If None, uses environment variable HEALTH_INSURANCE_LOG_LEVEL or defaults to INFO
        log_file: Optional file path to write logs to (in addition to console)
    
    Returns:
        The configured logger
    """
    if level is None:
        level = get_log_level()
    elif isinstance(level, str) and level.upper() in LOG_LEVELS:
        level = LOG_LEVELS[level.upper()]
    
    # Create handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Set level for all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(level)
    
    # Set level for root logger as well
    logging.getLogger().setLevel(level)
    
    # Return root logger
    return logging.getLogger()

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: Name for the logger, typically __name__ of the calling module
    
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Ensure the logger has the correct level
    if os.environ.get('HEALTH_INSURANCE_LOG_LEVEL'):
        env_level = os.environ.get('HEALTH_INSURANCE_LOG_LEVEL').upper()
        if env_level in LOG_LEVELS:
            logger.setLevel(LOG_LEVELS[env_level])
    
    return logger