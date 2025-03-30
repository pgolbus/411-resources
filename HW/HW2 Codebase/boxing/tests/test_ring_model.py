from dataclasses import asdict

import math

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

##################################################
# Ring Entry / Exit Tests
##################################################


#test add fighter to ring
def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == sample_boxer1.name

#test add fighter to full ring
def test_add_boxer_to_full_ring(ring_model, sample_boxer1):
    """Test error when adding a boxer to a full ring.

    """
    ring_model.add_boxer_to_ring(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer cannot be added. Ring is already full."):
        ring_model.add_boxer_to_ring(sample_boxer1)

#test add duplicate fighter to ring
def test_add_duplicate_boxer_to_playlist(ring_model, sample_boxer1):
    """Test error when adding a duplicate boxer to the ring.

    """
    ring_model.add_boxer_to_ring(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer already exists in the ring"):
        ring_model.add_boxer_to_ring(sample_boxer1)

# test add incorrect / non boxer to ring
def test_add_invalid_boxer_to_ring(ring_model):
    """Test error when adding an invalid (non-Boxer) object to the ring."""
    with pytest.raises(TypeError, match="Expected 'Boxer'"):
        ring_model.enter_ring({"name": "Fake Boxer", "weight": 200})


#test clear ring
def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ring.

    """
    ring_model.ring.append(sample_boxer1)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"

#test clear empty ring
def test_clear_empty_ring(ring_model):
    ring_model.clear_ring()
    with pytest.raises(ValueError, match="Ring is already empty"):
        ring_model.clear_ring()
    

##################################################
# Getter Tests
##################################################

#test get all boxers
def test_get_all_boxers(ring_model, sample_ring):
    """Test successfully retrieving all songs from the playlist.

    """
    ring_model.ring.extend(sample_ring)

    all_boxers = ring_model.get_all_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[1].id == 2


##################################################
# Fight Tests
##################################################

#test fight boxer 1 wins
def test_fight_winner_boxer1(ring_model, sample_boxer1, sample_boxer2, mock_update_boxer_stats, mock_get_random):
    """Test that boxer 1 wins the fight if random number < normalized delta."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    mock_get_random.return_value = 0.01  
    winner = ring_model.fight()

    assert winner == sample_boxer1.name
    mock_update_boxer_stats.assert_any_call(sample_boxer1.id, 'win')
    mock_update_boxer_stats.assert_any_call(sample_boxer2.id, 'loss')
    assert ring_model.ring == []

#test fight boxer 2 wins
def test_fight_winner_boxer2(ring_model, sample_boxer1, sample_boxer2, mock_update_boxer_stats, mock_get_random):
    """Test that boxer 2 wins the fight if random number > normalized delta."""
    ring_model.enter_ring(sample_boxer2)  # Jon Jones
    ring_model.enter_ring(sample_boxer1)  # Ilia Topuria

    mock_get_random.return_value = 0.99  # high enough to trigger boxer 2 win
    winner = ring_model.fight()

    assert winner == sample_boxer2.name
    mock_update_boxer_stats.assert_any_call(sample_boxer2.id, 'win')
    mock_update_boxer_stats.assert_any_call(sample_boxer1.id, 'loss')


#test fight <2 boxers
def test_fight_not_enough_boxers(ring_model, sample_boxer1):
    """Test that a fight cannot start with less than 2 boxers."""
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

##################################################
# Fighting Skill Tests
##################################################

#test skill average age boxer
def test_get_fighting_skill_mid_age(sample_boxer1):
    """Test fighting skill with a boxer of typical age (no penalty)."""
    ring = RingModel()
    skill = ring.get_fighting_skill(sample_boxer1)

    # Manual calculation check
    expected = (145 * len("Ilia Topuria")) + (69.0 / 10)  # age modifier = 0
    assert math.isclose(skill, expected, abs_tol=0.1)

#test skill young boxer
def test_get_fighting_skill_young_boxer():
    """Test fighting skill for a young boxer (age < 25)."""
    boxer = Boxer(4, 'Young Boxer', 140, 68, 70.0, 22)
    ring = RingModel()
    skill = ring.get_fighting_skill(boxer)

    expected = (140 * len("Young Boxer")) + (70.0 / 10) - 1
    assert math.isclose(skill, expected, abs_tol=0.1)

#test skill old boxer
def test_get_fighting_skill_old_boxer():
    """Test fighting skill for an older boxer (age > 35)."""
    boxer = Boxer(5, 'Old Boxer', 180, 70, 75.0, 38)
    ring = RingModel()
    skill = ring.get_fighting_skill(boxer)

    expected = (180 * len("Old Boxer")) + (75.0 / 10) - 2
    assert math.isclose(skill, expected, abs_tol=0.1)

#test skill invalid boxer
def test_get_fighting_skill_invalid_type():
    """Test that get_fighting_skill raises an error when passed a non-Boxer object."""
    ring = RingModel()
    with pytest.raises(AttributeError):
        ring.get_fighting_skill({"name": "Invalid", "weight": 180})


















