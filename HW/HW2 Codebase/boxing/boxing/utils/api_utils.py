import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random() -> float:
    """Fetches a random decimal fraction between 0.00 and 0.99 from random.org.

    The function makes an HTTP GET request to the URL specified by the
    `RANDOM_ORG_URL` environment variable, or a default URL if the environment
    variable is not set. It parses the response to extract the random number.

    Returns:
        float: A random decimal fraction between 0.00 and 0.99 (inclusive).

    Raises:
        RuntimeError: If the request to random.org times out or if the request
            fails due to other network-related issues.
        ValueError: If the response from random.org is invalid and cannot be
            parsed as a float.
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
