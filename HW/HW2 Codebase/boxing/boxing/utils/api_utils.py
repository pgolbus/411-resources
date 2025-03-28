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
    Gets a random decimal number between 0 and 1 from the url

    Makes an HTTP request to the RANDOM_ORG_URL endpoint tries to
    parse the result into a float.

    Returns:
        float: A random number from the url

    Raises:
        RuntimeError: If the HTTP request fails or times out
        ValueError: If the response is an invalid response
    """ 
    try:
        response = requests.get(RANDOM_ORG_URL, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        return random_number

    except requests.exceptions.Timeout:
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request to random.org failed: {e}")
