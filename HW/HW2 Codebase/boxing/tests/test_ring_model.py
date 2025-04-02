import math
from unittest.mock import patch

import pytest

from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel


@pytest.fixture
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def boxer1():
    """Fixture providing a sample Boxer instance."""
    return Boxer(id=1, name="Boxer One", weight=160, height=70, reach=72.0, age=25)

@pytest.fixture
def boxer2():
    """Fixture providing another sample Boxer instance."""
    return Boxer(id=2, name="Boxer Two", weight=170, height=72, reach=74.0, age=30)

@pytest.fixture
def boxer_young():
    """Fixture providing a young Boxer instance."""
    return Boxer(id=3, name="Young Champ", weight=150, height=69, reach=71.0, age=22)

@pytest.fixture
def boxer_old():
    """Fixture providing an old Boxer instance."""
    return Boxer(id=4, name="Old Timer", weight=180, height=73, reach=75.0, age=38)

@pytest.fixture
def mock_get_random():
    """Mocks the get_random function."""
    with patch("boxing.models.ring_model.get_random") as mock:
        yield mock

@pytest.fixture
def mock_update_boxer_stats():
    """Mocks the update_boxer_stats function."""
    with patch("boxing.models.ring_model.update_boxer_stats") as mock:
        yield mock


def test_ring_model_initialization(ring_model):
    """Tests that a RingModel instance is initialized with an empty ring."""
    assert not ring_model.ring

def test_enter_ring_success(ring_model, boxer1):
    """Tests that a boxer can successfully enter the ring."""
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0] == boxer1

def test_enter_ring_second_boxer(ring_model, boxer1, boxer2):
    """Tests that a second boxer can enter the ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    assert len(ring_model.ring) == 2
    assert boxer1 in ring_model.ring
    assert boxer2 in ring_model.ring

def test_enter_ring_invalid_type(ring_model):
    """Tests that a TypeError is raised when trying to enter a non-Boxer object."""
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'str'"):
        ring_model.enter_ring("Not a Boxer")

def test_enter_ring_full(ring_model, boxer1, boxer2, boxer_young):
    """Tests that a ValueError is raised when trying to add a third boxer to a full ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(boxer_young)

def test_clear_ring_empty(ring_model):
    """Tests that clearing an empty ring does nothing."""
    ring_model.clear_ring()
    assert not ring_model.ring

def test_clear_ring_with_boxers(ring_model, boxer1, boxer2):
    """Tests that clearing a ring with boxers removes all boxers."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    ring_model.clear_ring()
    assert not ring_model.ring

def test_get_boxers_empty(ring_model):
    """Tests that get_boxers returns an empty list for an empty ring."""
    assert not ring_model.get_boxers()

def test_get_boxers_with_boxers(ring_model, boxer1, boxer2):
    """Tests that get_boxers returns the list of boxers in the ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert boxer1 in boxers
    assert boxer2 in boxers

def test_get_fighting_skill(ring_model, boxer1):
    """Tests the calculation of the fighting skill for a boxer."""
    # Skill calculation: (weight * len(name)) + (reach / 10) + age_modifier
    # Boxer One: weight=160, name="Boxer One" (9), reach=72.0, age=25 (modifier=0)
    expected_skill = (160 * 9) + (72.0 / 10) + 0
    assert ring_model.get_fighting_skill(boxer1) == expected_skill

def test_get_fighting_skill_young_boxer(ring_model, boxer_young):
    """Tests the fighting skill calculation for a young boxer."""
    # Boxer Young: weight=150, name="Young Champ" (11), reach=71.0, age=22 (modifier=-1)
    expected_skill = (150 * 11) + (71.0 / 10) - 1
    assert ring_model.get_fighting_skill(boxer_young) == expected_skill

def test_get_fighting_skill_old_boxer(ring_model, boxer_old):
    """Tests the fighting skill calculation for an old boxer."""
    # Boxer Old: weight=180, name="Old Timer" (9), reach=75.0, age=38 (modifier=-2)
    expected_skill = (180 * 9) + (75.0 / 10) - 2
    assert ring_model.get_fighting_skill(boxer_old) == expected_skill

def test_fight_not_enough_boxers(ring_model, boxer1):
    """Tests that a ValueError is raised when trying to start a fight with fewer than two boxers."""
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()
    ring_model.enter_ring(boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_boxer1_wins(mock_update, ring_model, boxer1, boxer2, mock_get_random):
    """Tests the scenario where the first boxer wins the fight."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    skill1 = ring_model.get_fighting_skill(boxer1)
    skill2 = ring_model.get_fighting_skill(boxer2)
    delta = abs(skill1 - skill2)
    normalized_delta = 1 / (1 + math.e ** (-delta))

    mock_get_random.return_value = normalized_delta - 0.01  # Ensure random is less than normalized delta

    winner_name = ring_model.fight()
    assert winner_name == boxer1.name
    mock_update.assert_any_call(boxer1.id, 'win')
    mock_update.assert_any_call(boxer2.id, 'loss')
    assert not ring_model.ring  # Ring should be cleared

@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_boxer2_wins(mock_update, ring_model, boxer1, boxer2, mock_get_random):
    """Tests the scenario where the second boxer wins the fight."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    skill1 = ring_model.get_fighting_skill(boxer1)
    skill2 = ring_model.get_fighting_skill(boxer2)
    delta = abs(skill1 - skill2)
    normalized_delta = 1 / (1 + math.e ** (-delta))

    mock_get_random.return_value = normalized_delta + 0.01  # Ensure random is greater than or equal to normalized delta

    winner_name = ring_model.fight()
    assert winner_name == boxer2.name
    mock_update.assert_any_call(boxer2.id, 'win')
    mock_update.assert_any_call(boxer1.id, 'loss')
    assert not ring_model.ring  # Ring should be cleared