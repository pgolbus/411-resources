from dataclasses import asdict

import pytest
from pytest_mock import mocker

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

##################################################
#   Pytest fixtures                              #
##################################################

@pytest.fixture
def mock_ring():
    """Fixture to create an instance of RingModel."""
    return RingModel()

@pytest.fixture
def boxer1():
    """Fixture to create an instance of Boxer 1 (Ali)."""
    return Boxer(id=1, name='Ali', weight=180, height=70, reach=72.5, age=28, weight_class="MIDDLEWEIGHT")

@pytest.fixture
def boxer2():
    """Fixture to create an instance of Boxer 2 (Tyson)."""
    return Boxer(id=2, name='Tyson', weight=220, height=72, reach=75, age=30, weight_class="HEAVYWEIGHT")

@pytest.fixture
def mock_updated_boxer_stats_cursor(mocker):
    """Fixture to mock an updated_boxer_stats call after fight."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

##################################################
#   Clear / fill ring test cases                 #
##################################################

def test_clear_ring(mock_ring, boxer1, boxer2):
    """Test to successfully clear ring of boxers."""

    mock_ring.enter_ring(boxer1)
    mock_ring.enter_ring(boxer2)

    assert len(mock_ring.ring) == 2

    mock_ring.clear_ring()
 
    assert len(mock_ring.ring) == 0

def test_add_boxer_to_ring(mock_ring, boxer1):
    """Test to successfully add a boxer to an empty ring."""

    RingModel.enter_ring(mock_ring, boxer1)

    # Check ring contains exactly 1 boxer named 'Ali'.
    assert len(mock_ring.ring) == 1
    assert mock_ring.ring[0].name == 'Ali'

def test_fail_ring_is_full(mock_ring, boxer1, boxer2):
    """Test to check failure when attempt to add boxer to a full ring."""

    mock_ring.enter_ring(boxer1)
    mock_ring.enter_ring(boxer2)

    # Check that ValueError and message is raised since ring is full.
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        mock_ring.enter_ring(Boxer(id=1234, name='Paddy', weight=186, height= 72, reach=72, age=28))

##################################################
#  Get boxer test cases                          #
##################################################

def test_get_boxers(mock_ring):
    """Test to successfully retrieve list of boxers."""

    fake_boxer_1 = Boxer(id=2222, name='Kiki', weight= 130, height= 65, reach=66, age=23)
    fake_boxer_2 = Boxer(id=4289, name='Bouba', weight= 132, height= 66, reach=66, age=24)

    mock_ring.enter_ring(fake_boxer_1)
    mock_ring.enter_ring(fake_boxer_2)

    actual_result = mock_ring.get_boxers()
    expected_result = [fake_boxer_1, fake_boxer_2]

    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"

    mock_ring.clear_ring()

    actual_result = mock_ring.get_boxers()
    expected_result = []

    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"    

##################################################
#  Get fighting skill test cases                 #
##################################################

def test_get_fighting_skill(mock_ring, boxer1):
    """Test the calculation of the fighting skill of a boxer."""

    mock_ring.enter_ring(boxer1)

    actual_skill = mock_ring.get_fighting_skill(boxer1)
    expected_skill = (boxer1.weight * len(boxer1.name)) + (boxer1.reach / 10)  # Adjusted expected calculation
    
    assert actual_skill == expected_skill, f"Expected {expected_skill}, but got {actual_skill}"

##################################################
#  Run fight test cases                          #
##################################################

def test_fight_success(mock_updated_boxer_stats_cursor, mock_ring, boxer1, boxer2):
    """Test a successful fight between two boxers."""
    mock_ring.enter_ring(boxer1)
    mock_ring.enter_ring(boxer2)

    # Ensure the correct winner is returned
    actual_winner = mock_ring.fight()

    if actual_winner == boxer1.name:
        winner_id = boxer1.id
        loser_id = boxer2.id
    else: 
        winner_id = boxer2.id
        loser_id = boxer1.id
    
    # Check that updated_boxer_stats get called twice.
    mock_updated_boxer_stats_cursor.assert_any_call(winner_id, 'win')
    mock_updated_boxer_stats_cursor.assert_any_call(loser_id, 'loss')

def test_ring_clear_after_fight(mock_updated_boxer_stats_cursor, mock_ring, boxer1, boxer2):
    """Test to see if ring clears after fight."""

    mock_ring.enter_ring(boxer1)
    mock_ring.enter_ring(boxer2)

    mock_ring.fight()

    assert len(mock_ring.ring) == 0, "Expected cleared ring after fight."

def test_fail_fight_unsuccessful(mock_ring, boxer1):
    """Test to check failure when fight is triggered with less than 2 boxers."""

    mock_ring.enter_ring(boxer1)

    # Check ValueError and message is raised since fight is triggered with only 1 boxer in ring.
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        mock_ring.fight()
