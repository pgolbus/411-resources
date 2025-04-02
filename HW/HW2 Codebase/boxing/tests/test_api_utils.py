"""
Unit tests for the boxing.utils.api_utils module.

This file tests the get_random function to ensure it correctly handles:
    - A valid HTTP response returning a numeric string.
    - An HTTP response with an invalid (non-numeric) string.
    - A timeout scenario resulting in a RuntimeError.
"""

import pytest
import requests
from boxing.utils.api_utils import get_random

def test_get_random_success(mocker):
    """Test that get_random returns a valid float when a valid response is received.

    Mocks a successful HTTP GET request to random.org by patching requests.get
    to return a response containing a valid numeric string ("0.25"). Verifies that
    the function returns the correct float value.

    Args:
        mocker: Pytest fixture for patching objects.
    """
    fake_response = mocker.Mock()
    fake_response.text = "0.25"
    fake_response.raise_for_status.return_value = None
    mocker.patch("boxing.utils.api_utils.requests.get", return_value=fake_response)
    result = get_random()
    assert isinstance(result, float)
    assert result == 0.25

def test_get_random_invalid_response(mocker):
    """Test that get_random raises ValueError for a non-numeric response.

    Mocks an HTTP GET request to random.org where the response text is not a number.
    Expects the get_random function to raise a ValueError indicating an invalid response.

    Args:
        mocker: Pytest fixture for patching objects.
    """
    fake_response = mocker.Mock()
    fake_response.text = "not_a_number"
    fake_response.raise_for_status.return_value = None
    mocker.patch("boxing.utils.api_utils.requests.get", return_value=fake_response)
    with pytest.raises(ValueError, match="Invalid response"):
        get_random()

def test_get_random_timeout(mocker):
    """Test that get_random raises RuntimeError when the request times out.

    Mocks the requests.get call to simulate a timeout by raising a requests.exceptions.Timeout.
    Expects the get_random function to raise a RuntimeError indicating that the request timed out.

    Args:
        mocker: Pytest fixture for patching objects.
    """
    mocker.patch("boxing.utils.api_utils.requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        get_random()
