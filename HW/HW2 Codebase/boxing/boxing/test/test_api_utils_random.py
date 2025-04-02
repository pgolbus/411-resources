import pytest
import requests
from boxing.utils.api_utils import get_random

def test_get_random_success(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "0.57\n"
    mock_response.raise_for_status.return_value = None

    mocker.patch("boxing.utils.api_utils.requests.get", return_value=mock_response)

    result = get_random()
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0

def test_get_random_invalid_response(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "not-a-number"
    mock_response.raise_for_status.return_value = None

    mocker.patch("boxing.utils.api_utils.requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

def test_get_random_timeout(mocker):
    mocker.patch("boxing.utils.api_utils.requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_request_failure(mocker):
    mocker.patch("boxing.utils.api_utils.requests.get", side_effect=requests.exceptions.RequestException("Network down"))

    with pytest.raises(RuntimeError, match="Request to random.org failed:"):
        get_random()