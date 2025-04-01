import pytest
import requests

from boxing.utils.api_utils import get_random


RANDOM_DECIMAL = "0.78"


@pytest.fixture
def mock_random_org(mocker):
    """
    Fixture that mocks the requests.get() call to simulate a successful response
    from random.org with a decimal value of 0.78.

    Returns:
        mock.Mock: The mocked response object with `.text` set to "0.78".
    """
    mock_response = mocker.Mock()
    mock_response.text = RANDOM_DECIMAL
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random_success(mock_random_org):
    """
    Test that get_random() successfully retrieves a float from random.org.

    This test:
    - Mocks a valid response from random.org
    - Asserts the result is a float within [0, 1]
    - Confirms that the expected URL was called
    """
    result = get_random()

    assert isinstance(result, float)
    assert 0 <= result <= 1
    assert result == float(RANDOM_DECIMAL)

    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_invalid_response(mocker):
    """
    Test that get_random() raises a ValueError if the response text is not a valid float.

    This simulates random.org returning malformed data (e.g., non-numeric).
    """
    mock_response = mocker.Mock()
    mock_response.text = "not_a_number"
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid response from random.org: not_a_number"):
        get_random()


def test_get_random_timeout(mocker):
    """
    Test that get_random() raises a RuntimeError if the request times out.

    This simulates a timeout exception during the HTTP request.
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()


def test_get_random_request_failure(mocker):
    """
    Test that get_random() raises a RuntimeError on generic request failure.

    Simulates a generic RequestException (e.g., DNS failure, connection refused).
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Boom"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Boom"):
        get_random()