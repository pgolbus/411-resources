from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function used to determine fight outcomes."""
    return mocker.patch("boxing.models.ring_model.get_random")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Ilia Topuria', 145, 67, 69.0, 28)

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Jon Jones', 250, 76, 84.5, 36)

@pytest.fixture
def sample_boxer3():
    return Boxer(3, 'Dustin Poirier', 155, 68, 72.0, 34)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

#define tests 

#test add fighter to ring

#test add duplicate fighter to ring

#test add incorrect fighter to ring

#test remove fighter from ring

#test remove nonexistent fighter from ring

#test get boxers 















