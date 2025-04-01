import logging
import sys

from flask import current_app, has_request_context


def configure_logger(logger):
    """
    Configures a logger to output detailed logs to stderr and can also
    attach Flask app log handlers

    The logger sets log levels to debug, outputs logs to stderr along with
    the timestamps, shares log handlers with Flask's app logger if it's inside
    a request context

    Args:
        logger (logging.Logger): The logger instance for configuring
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
    logger.debug("Logger has been configured with a stream handler and formatter")

    # We also need to add the handler to the Flask logger
    if has_request_context():
        logger.debug("Flask request context detected, attaching Flask app logger handlers")
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)
        logger.debug("Flask logger handlers successfully attached")
    else:
        logger.debug("No Flask request context")