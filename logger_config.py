"""
Comprehensive logging configuration for generative agents.
Provides structured logging with different levels and outputs.
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up comprehensive logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional specific log file name
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Set up log file name
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"generative_agents_{timestamp}.log"
    
    log_file_path = log_path / log_file
    
    # Configure logging format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get logger
    logger = logging.getLogger('generative_agents')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_path = log_path / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_log_path)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logging initialized. Log file: {log_file_path}")
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance with the specified name."""
    if name:
        return logging.getLogger(f'generative_agents.{name}')
    return logging.getLogger('generative_agents')

# Security logging functions
def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """Log security-related events."""
    security_logger = get_logger('security')
    log_level = getattr(logging, severity.upper())
    security_logger.log(log_level, f"SECURITY_EVENT: {event_type} - {details}")

def log_api_call(api_name: str, cost: float = None, success: bool = True):
    """Log API calls for monitoring and cost tracking."""
    api_logger = get_logger('api')
    status = "SUCCESS" if success else "FAILED"
    cost_info = f" (Cost: ${cost:.4f})" if cost else ""
    api_logger.info(f"API_CALL: {api_name} - {status}{cost_info}")

def log_simulation_event(event_type: str, persona_name: str = None, details: str = ""):
    """Log simulation-specific events."""
    sim_logger = get_logger('simulation')
    persona_info = f"[{persona_name}]" if persona_name else ""
    sim_logger.info(f"SIM_EVENT: {event_type} {persona_info} - {details}")

# Initialize default logger
try:
    # Try to load log level from config
    from config import DEBUG
    default_log_level = "DEBUG" if DEBUG else "INFO"
except ImportError:
    default_log_level = "INFO"

default_logger = setup_logging(log_level=default_log_level)