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
    Fetches a random number from random.org and returns it as a float.

    This function sends an HTTP GET request to the RANDOM_ORG_URL to retrieve a random number.
    The response is a string representation of a number as a float. 
    If the request fails or the response is invalid, appropriate exceptions are raised.

    Returns:
        float: A random number fetched from random.org.

    Raises:
        ValueError: If the response from random.org cannot be converted to a float.
        RuntimeError: If the request to random.org times out or fails due to a network error.
    """
    
    try:
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        logging.info("Sending request to random.org to fetch a random number.")
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
