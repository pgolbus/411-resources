import logging
import os
import requests

from boxing.utils.logger import configure_logger


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random() -> float:
    """
    it gets a random decimal number from random.org

    Returns:
        float: The random  decimal number from random.org with 2 decimal places

    Raises:
        ValueError is there is an invalid number that is not a float from random.org
        RuntimeError if the request to random.org does not work or times out
    """
    try:
        logger.info(f"Fetching random decimal number from {RANDOM_ORG_URL}")
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
