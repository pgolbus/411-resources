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
    Gets random int from random.org.

    Returns:
        float: A random number。

    Raises:
        RuntimeError: If the request to random.org fails.
        ValueError: If the response from random.org is not a valid float.

    """
    try:
        logger.info("Fetching a random number...")
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.error("Inappropriate response from random.org.")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        logger.info("Successfully generated random number.")
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Unsuccessful: Was not able to fetch a random number from random.org due to a timeout.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Unsuccessful: Was not able to fetch a random number from random.org due to a failure.")
        raise RuntimeError(f"Request to random.org failed: {e}")
