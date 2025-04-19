import pytest
import requests
from unittest.mock import MagicMock
from boxing.utils.api_utils import get_random

# Use a separate constants file for better maintainability
from boxing.constants import RANDOM_NUMBER  

@pytest.fixture
def mock_random_org(mocker):
    """Mock the response from random.org for a successful request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = f"{RANDOM_NUMBER}\n"
    mocker.patch("requests.get", return_value=mock_response, autospec=True)
    return mock_response

def test_get_random_success(mock_random_org):
    """Ensure get_random successfully retrieves a number from random.org."""
    result = get_random()
    assert result == RANDOM_NUMBER, f"Expected {RANDOM_NUMBER}, got {result}"
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_request_failure(mocker):
    """Verify that get_random raises an error when the request fails."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"), autospec=True)

    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_timeout(mocker):
    """Ensure a timeout results in a RuntimeError."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout, autospec=True)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_invalid_response(mocker):
    """Check handling of an invalid response (non-numeric content)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "not_a_number"
    mocker.patch("requests.get", return_value=mock_response, autospec=True)

    with pytest.raises(ValueError, match="Invalid response from random.org: not_a_number"):
        get_random()

def test_get_random_http_error(mocker):
    """Ensure an HTTP error is correctly handled."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    mocker.patch("requests.get", return_value=mock_response, autospec=True)

    with pytest.raises(RuntimeError, match="Request to random.org failed: 500 Server Error"):
        get_random()
