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
    Gets a random float between 0 and 1 from random.org.

    Makes a GET request to RANDOM_ORG_URL. If the response is valid and can be converted as a float, 
    the value is returned. Handles and raises descriptive errors in the case of failure.

    Returns:
        float: A random float between 0 and 1 from random.org.

    Raises:
        RuntimeError: If the request times out or any request-related error occurs.
        ValueError: If the response text cannot be converted into a float.
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
