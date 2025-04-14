import pytest
import requests

from boxing.utils.api_utils import get_random

RANDOM_NUMBER = 0.42

@pytest.fixture
def mock_random_org(mocker):
    """Mock the response from random.org to return a fixed random number."""
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random()
    
    assert result == RANDOM_NUMBER, f"Expected random number {RANDOM_NUMBER}, but got {result}"
    
    requests.get.assert_called_once_with("https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new", timeout=5)

def test_get_random_request_failure(mocker):
    """Test handling of a request failure when calling random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))
    
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_timeout(mocker):
    """Test handling of a timeout when calling random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_invalid_response(mock_random_org):
    """Test handling of an invalid response from random.org."""
    mock_random_org.text = "invalid_response"
    
    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()
