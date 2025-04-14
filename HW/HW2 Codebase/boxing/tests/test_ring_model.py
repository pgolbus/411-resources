from dataclasses import asdict
import math
import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()


@pytest.fixture()
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")


@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function used to determine fight outcomes."""
    return mocker.patch("boxing.models.ring_model.get_random")


@pytest.fixture()
def boxer_1():
    """Fixture to provide a Boxer instance for testing."""
    return Boxer(id=1, name="Boxer 1", weight=160, reach=75, age=30, height=180)


@pytest.fixture()
def boxer_2():
    """Fixture to provide another Boxer instance for testing."""
    return Boxer(id=2, name="Boxer 2", weight=155, reach=72, age=28, height=175)


def test_enter_ring_success(ring_model, boxer_1):
    """Test the enter_ring method with a valid boxer."""
    ring_model.enter_ring(boxer_1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0] == boxer_1


def test_enter_ring_full(ring_model, boxer_1, boxer_2):
    """Test trying to add a third boxer to a full ring."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(Boxer(id=3, name="Boxer 3", weight=170, reach=80, age=35))


def test_enter_ring_invalid_type(ring_model):
    """Test adding an invalid type to the ring."""
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
        ring_model.enter_ring("Not a boxer")


def test_fight_success(ring_model, boxer_1, boxer_2, mock_get_random, mock_update_boxer_stats):
    """Test a successful fight simulation."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)
    # Mocking the random number to simulate a specific outcome
    mock_get_random.return_value = 0.7  # Assume that boxer 1 has the advantage

    winner_name = ring_model.fight()

    # Assert that the winner is boxer 1, based on the mock value
    assert winner_name == "Boxer 1"

    # Ensure the stats update function was called for both boxers
    mock_update_boxer_stats.assert_any_call(boxer_1.id, 'win')
    mock_update_boxer_stats.assert_any_call(boxer_2.id, 'loss')


def test_fight_not_enough_boxers(ring_model):
    """Test that the fight method raises an error when there are not enough boxers."""
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()


def test_clear_ring(ring_model, boxer_1, boxer_2):
    """Test that the clear_ring method works correctly."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)
    assert len(ring_model.ring) == 2

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0


def test_get_fighting_skill(ring_model, boxer_1):
    """Test the get_fighting_skill method to ensure correct skill calculation."""
    skill = ring_model.get_fighting_skill(boxer_1)
    expected_skill = (boxer_1.weight * len(boxer_1.name)) + (boxer_1.reach / 10) - 1  # Age modifier is -1 for boxer_1 (age 30)

    assert math.isclose(skill, expected_skill)


def test_get_boxers(ring_model, boxer_1, boxer_2):
    """Test the get_boxers method."""
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert boxers[0] == boxer_1
    assert boxers[1] == boxer_2
