import pytest
from unittest.mock import patch, MagicMock
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture
def boxer_1():
    """Fixture providing a sample Boxer object for testing.

    Returns:
        Boxer: A Boxer object representing 'Ali'.
    """
    return Boxer(id=1, name="Ali", weight=150, height=70, reach=72.5, age=25)


@pytest.fixture
def boxer_2():
    """Fixture providing another sample Boxer object for testing.

    Returns:
        Boxer: A Boxer object representing 'Tyson'.
    """
    return Boxer(id=2, name="Tyson", weight=160, height=72, reach=74.0, age=28)


@pytest.fixture
def ring():
    """Fixture providing a RingModel instance for testing.
    
    Returns:
        RingModel: A new instance of RingModel.
    """
    return RingModel()


def test_enter_ring_success(ring, boxer_1):
    """Test successful entry of a boxer into the ring."""
    ring.enter_ring(boxer_1)
    assert ring.ring == [boxer_1]


def test_enter_ring_type_error(ring):
    """Test entering non-Boxer object raises TypeError."""
    with pytest.raises(TypeError):
        ring.enter_ring("not_a_boxer")


def test_enter_ring_full(ring, boxer_1, boxer_2):
    """Test entering a third boxer raises ValueError when ring is full."""
    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)
    with pytest.raises(ValueError):
        ring.enter_ring(boxer_1)


def test_clear_ring(ring, boxer_1):
    """Test clearing the ring removes all boxers."""
    ring.enter_ring(boxer_1)
    ring.clear_ring()
    assert ring.ring == []


def test_get_boxers(ring, boxer_1, boxer_2):
    """Test retrieving boxers from the ring."""
    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)
    boxers = ring.get_boxers()
    assert boxer_1 in boxers and boxer_2 in boxers


@patch("boxing.models.ring_model.get_random", return_value=0.9)
@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_winner_loser_paths(mock_update_stats, mock_random, ring, boxer_1, boxer_2):
    """Test fight simulation updates stats for both winner and loser."""
    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)

    winner_name = ring.fight()

    assert winner_name in [boxer_1.name, boxer_2.name]
    assert mock_update_stats.call_count == 2

    calls = [call.args for call in mock_update_stats.call_args_list]
    assert any(call[1] == 'win' for call in calls)
    assert any(call[1] == 'loss' for call in calls)

    assert ring.ring == []


def test_get_fighting_skill_logic(ring, boxer_1):
    """Test calculation of fighting skill score."""
    skill = ring.get_fighting_skill(boxer_1)
    expected_skill = (boxer_1.weight * len(boxer_1.name)) + (boxer_1.reach / 10)
    assert skill == expected_skill