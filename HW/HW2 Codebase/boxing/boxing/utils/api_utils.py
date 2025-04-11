import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random() -> float:
    """Returns a random number.
    
    Returns: 
        float: A random number as determined by random.org.

    Raises:
        ValueError: Did not recieve random number.
        RunTimeError: Request timed out.
        RunTimeError: Request failed.

    """
    logger.info("Received request to get random number.")
    try:
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.warning(" Did not recieve random number.")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")
        
        logger.info("Successfully returned random number.")
        return random_number

    except requests.exceptions.Timeout:
        logger.warning("Request timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.warning("Request failed.")
        raise RuntimeError(f"Request to random.org failed: {e}")
