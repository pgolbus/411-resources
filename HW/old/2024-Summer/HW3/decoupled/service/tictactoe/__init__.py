from dataclasses import dataclass
import logging
from typing import List
import sys

from flask import current_app, has_request_context


SQUARE_OCCUPIED_ERROR_MSG = "Square already occupied"
INVALID_MOVE_ERROR_MSG = "Invalid move"


@dataclass
class Board:
    squares: List[str]


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the desired logging level here

# Create a console handler that logs to stderr
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)

# Create a formatter with a timestamp
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

def configure_logger():
    if has_request_context():
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)