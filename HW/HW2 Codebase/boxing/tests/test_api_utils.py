import pytest
import requests

from boxing.utils.api_utils import get_random

@pytest.fixture
def mock_api_response(mocker):
    """ Create a mock response object"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mocker.patch("requests.post", return_value=mock_response)
    return mock_response


def test_get_random(mocker):
    """Test retrieving a random decimal number between 0 and 1.
    """
    mock_response = mocker.Mock()
    mock_response.text = "0.42"
    mocker.patch("requests.get", return_value=mock_response)

    result = get_random()

    assert result == 0.42, f"Expected random number 0.42, but got {result}"

    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )


def test_get_random_request_failure(mocker):
    """Test handling of a request failure when calling random.org.
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request failed: Connection error"):
        get_random()


def test_get_random_timeout(mocker):
    """Test handling of a timeout when calling random.org.
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request timed out."):
        get_random()


def test_get_random_invalid_response(mocker):
    """Test handling of an invalid response from random.org.
    """
    mock_response = mocker.Mock()
    mock_response.text = "invalid_response"
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid response: invalid_response"):
        get_random()


