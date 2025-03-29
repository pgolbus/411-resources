import logging
import sys

from flask import current_app, has_request_context


def configure_logger(logger):
    """
    Configures a logger to output logs to stderr.

    This function sets up a logger with a StreamHandler and a timestamped formatter.
    If running in a Flask request context it will also attach Flask's handlers to make sure logs
    are captured consistently.

    Args:  
        logger (logging.Logger): The logger instance to configure

    Returns:
        None
    """

    logger.setLevel(logging.DEBUG)

    # Create a console handler that logs to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # Create a formatter with a timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # We also need to add the handler to the Flask logger
    if has_request_context():
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)