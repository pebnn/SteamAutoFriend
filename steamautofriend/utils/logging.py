import logging
from ..config import LOG_FILE, LOG_FORMAT, DATE_FORMAT, LOG_LEVEL

# Set up the root logger to handle all loggers in the application
def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    # Configure the root logger
    root_logger = logging.getLogger()
    
    # Only set up logging if no handlers exist
    if not root_logger.handlers:
        # Get log level from config
        level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        
        # File handler - always include DEBUG level for better troubleshooting
        try:
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG in the file
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error setting up log file: {str(e)}")
        
        # Console handler - use configured level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Create the main application logger as a child of root
        app_logger = logging.getLogger("SteamAutoFriend")
        app_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
        
        # Print the log file path to make it easier to find
        print(f"Log file: {LOG_FILE}")
    
    # Return the application logger
    return logging.getLogger("SteamAutoFriend")

# Create a logger for this module that writes to the file
logger = logging.getLogger("SteamAutoFriend.logging")
