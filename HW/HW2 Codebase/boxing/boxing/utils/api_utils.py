"""This module provides a utility function to fetch a random decimal fraction
from the random.org website.
"""
import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                            "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random() -> float:
    """
    Fetches a random decimal number (with two decimal places) from random.org.

    Uses the RANDOM_ORG_URL environment variable to construct the request URL.
    Falls back to a default endpoint if the variable is not set.

    Returns:
        float: A random decimal number between 0 and 1, rounded to two decimal places.

    Raises:
        RuntimeError: If the request to random.org fails or times out.
        ValueError: If the response from random.org is not a valid float.
    """
    
    try:
        logger.info(f"Fetching random number from {RANDOM_ORG_URL}")
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")
        logger.info(f"Received random number: {random_number}")
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")