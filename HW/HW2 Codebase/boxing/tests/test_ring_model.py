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
    """Mock the update_boxer_stats function for testing."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(id=1, name="Boxer 1", age=33, weight=148, reach=72, height=70)

@pytest.fixture
def sample_boxer2():
    return Boxer(id=2, name="Boxer 2", age=23, weight=146, reach=70, height=68)

@pytest.fixture
def sample_boxer3():
    return Boxer(id=3, name="Boxer 3", age=40, weight=140, reach=75, height=69)

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

def test_enter_invalid_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding an invalid boxer to the ring.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'dict'"):
        ring_model.enter_ring(asdict(sample_boxer1))

def test_enter_boxers_to_full_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test error when adding more than two boxers to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)


def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ring.

    """
    ring_model.enter_ring(sample_boxer1)
    
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"


##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_one_boxer(ring_model, sample_boxer1):
    """Test successfully retrieving one boxer from the ring.

    """
    ring_model.enter_ring(sample_boxer1)

    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 1
    assert all_boxers[0].id == 1

def test_get_all_boxers(ring_model, sample_boxer1, sample_boxer2):
    """Test successfully retrieving all boxers from the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[1].id == 2

def test_get_all_boxers_empty(ring_model):
    """Test retrieving boxers from an empty ring.

    """
    assert ring_model.get_boxers() == [], "List of boxers should be empty when ring is empty"


##################################################
# Utility Function Test Cases
##################################################


def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test calculating the fighting skill of a boxer older than 25 and younger than 35.

    """
    skill = ring_model.get_fighting_skill(sample_boxer1)
    expected_skill = (148 * 7) + (72 / 10) + 0  # expected_skill = 1043.2
    assert skill == expected_skill, f"Expected fighting skill {expected_skill}, got {skill}"

def test_get_younger_boxer_fighting_skill(ring_model, sample_boxer2):
    """Test calculating the fighting skill of a boxer younger than 25.w

    """
    skill = ring_model.get_fighting_skill(sample_boxer2)
    expected_skill = (146 * 7) + (70 / 10) - 1  # expected_skill = 1028
    assert skill == expected_skill, f"Expected fighting skill {expected_skill}, got {skill}"

def test_get_older_boxer_fighting_skill(ring_model, sample_boxer3):
    """Test calculating the fighting skill of a boxer older than 35.

    """
    skill = ring_model.get_fighting_skill(sample_boxer3)
    expected_skill = (140 * 7) + (75 / 10) - 2  # expected_skill = 985.5
    assert skill == expected_skill, f"Expected fighting skill {expected_skill}, got {skill}"


##################################################
# Fight Test Cases
##################################################


def test_fight_with_empty_ring(ring_model):
    """Test error when trying to start a fight with an empty ring.

    """
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_with_one_boxer(ring_model, sample_boxer1):
    """Test error when trying to start a fight with one boxer.

    """
    ring_model.enter_ring(sample_boxer1)
    
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_boxer1_wins(ring_model, sample_boxer1, sample_boxer2, mocker, mock_update_boxer_stats):
    """Test a full fight between two boxers where boxer1 wins.

    Patching get_random to return 0.0 (low number) to select boxer 1 as the winner.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.0)
    
    winner_name = ring_model.fight()
    assert winner_name == sample_boxer1.name, f"Expected winner to be {sample_boxer1.name}, got {winner_name}"

    mock_update_boxer_stats.assert_any_call(sample_boxer1.id, 'win')
    mock_update_boxer_stats.assert_any_call(sample_boxer2.id, 'loss')

    assert len(ring_model.ring) == 0, "Ring should be cleared after match finished"

def test_fight_boxer2_wins(ring_model, sample_boxer1, sample_boxer2, mocker, mock_update_boxer_stats):
    """Test a full fight between two boxers where boxer2 wins.

    Patching get_random to return 1.0 (high number) to select boxer2 as the winner.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    mocker.patch("boxing.models.ring_model.get_random", return_value=1.0)

    winner_name = ring_model.fight()
    assert winner_name == sample_boxer2.name, f"Expected winner to be {sample_boxer2.name}, got {winner_name}"

    mock_update_boxer_stats.assert_any_call(sample_boxer2.id, 'win')
    mock_update_boxer_stats.assert_any_call(sample_boxer1.id, 'loss')
    assert len(ring_model.ring) == 0, "Ring should be cleared after match finished"


def test_fight_equal_skills(ring_model, sample_boxer1, sample_boxer2, mocker, mock_update_boxer_stats):
    """Test a fight where both boxers have equal fighting skills.

    Make the boxers have equal fighting skill by patching get_fighting_skill to return 1000 for both boxers. Also patch get_random to return 0.5, in this case normalized_delta will always be 0.5 since the fighting skill of the two boxers are equal, this should make boxer2 win, as 0.5<0.5 is false.

    """
    mocker.patch.object(ring_model, "get_fighting_skill", return_value=1000)

    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    mocker.patch("boxing.models.ring_model.get_random", return_value=0.5)

    winner_name = ring_model.fight()
    assert winner_name == sample_boxer2.name, f"Expected winner to be {sample_boxer2.name}, got {winner_name}"

    mock_update_boxer_stats.assert_any_call(sample_boxer2.id, 'win')
    mock_update_boxer_stats.assert_any_call(sample_boxer1.id, 'loss')
    assert len(ring_model.ring) == 0, "Ring should be cleared after match finished"
