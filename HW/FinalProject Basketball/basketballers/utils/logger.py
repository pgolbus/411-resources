import logging

def configure_logger(logger: logging.Logger) -> None:
    """Configure the logger for the application."""
    
    # Create a handler to write logs to a file
    handler = logging.StreamHandler()  # You can change this to FileHandler if you want to log to a file
    
    # Set the logging level (DEBUG for development, ERROR for production)
    logger.setLevel(logging.DEBUG) 
    
    # Define a formatter to structure the log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(handler)
    
    # Optionally, you can also set up a FileHandler to log to a file, for example:
    # file_handler = logging.FileHandler('app.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    logger.info("Logger configured successfully.")
