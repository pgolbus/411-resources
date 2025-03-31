from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats():
    """Mock the update_boxer_stats function for testing."""
    return Mock()

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(id=1, name="Boxer 1", age=35, weight=148, reach=72)

@pytest.fixture
def sample_boxer2():
    return Boxer(id=2, name="Boxer 2", age=33, weight=146, reach=70)

@pytest.fixture
def sample_boxer3():
    return Boxer(id=3, name="Boxer 3", age=40, weight=140, reach=75)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

##################################################
# Add / Remove Boxer Management Test Cases
##################################################

def test_enter_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer 1'

def test_add_duplicate_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding a duplicate boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer with ID 1 already exists in the ring"):
        ring_model.enter_ring(sample_boxer1)

def test_enter_invalid_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding an invalid boxer to the ring.

    """
    with pytest.raises(TypeError, match="Boxer is not a valid Boxer instance"):
        ring_model.enter_ring(asdict(sample_boxer1))

def test_enter_boxers_to_full_ring(ring_model, sample_ring, sample_boxer1):
    """Test error when adding more than two boxers to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Can't add boxers to a full ring."):
        ring_model.enter_ring(sample_boxer3)


def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ring.

    """
    ring_model.ring.append(sample_boxer1)
    
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"


