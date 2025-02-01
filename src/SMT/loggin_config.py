import logging

def setup_logger(log_file="debug.log", level=logging.DEBUG):
    """
    Set up the logger with file and console handlers.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Format for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Constraints loggings 
def log_constraint(logger, description, constraint):
    logger.debug(f"Adding constraint: {description} -> {constraint}") 