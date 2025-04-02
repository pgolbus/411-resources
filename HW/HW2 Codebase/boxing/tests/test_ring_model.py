"""
Unit tests for the boxing.models.ring_model 

This file tests:
  - enter_ring: Test adding a boxer to the ring.
  - fight: Test conducts a fight and makes sure it results in a winner and is cleared after.
  - clear_ring: Tests that a ring is cleared after a fight.
  - get_fighting_skill: Test that the fighting skill is correctly calculated.
  - get_boxers: Tests that get_boxers retuns the correct list of boxers.
  - Tests that adding a non-boxer raises a TypeError
  - Tests that adding a third boxer to a ring raises an error.
  - Tests that a fight with less than 2 boxers raises an error. 
"""

from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture()
def boxer1():
    """Fixture to create a Boxer instance for testing."""
    return Boxer(id=1, name="Boxer 1", age=20, weight=165, height=57, reach=50)

@pytest.fixture()
def boxer2():
    """Fixture to create another Boxer instance for testing."""
    return Boxer(id=2, name="Boxer 2", age=22, weight=185, height=60, reach=60)

@pytest.fixture()
def boxer3():
    """Fixture to create a third Boxer instance for testing."""
    return Boxer(id=3, name="Boxer 3", age=20, weight=138, height=40, reach=55)

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

##################################################
# Ring Test Cases
##################################################

def test_add_boxer_to_ring(ring_model, boxer1):
    """Test adding a boxer to the ring."""
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "Boxer 1"

def test_type_error(ring_model):
    """Test that adding not a boxer raises a TypeError"""
    with pytest.raises(TypeError):
        ring_model.enter_ring("boxer")

def test_add_third_boxer_to_ring_error(ring_model, boxer1, boxer2, boxer3):
    """Test error when trying to add a third boxer to the ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(boxer3)

def test_clear_ring(ring_model, boxer1, boxer2):
    """Test that the ring is cleared after a fight."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    assert len(ring_model.ring) == 2
    ring_model.clear_ring()    
    assert len(ring_model.ring) == 0  

##################################################
# Fight Test Cases
##################################################

def test_fight(ring_model, boxer1, boxer2, mock_update_boxer_stats):
    """Test conducting a fight between two boxers."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    assert len(ring_model.ring) == 2

    ring_model.fight()

    mock_update_boxer_stats.assert_called()
    assert len(ring_model.ring) == 0 
    
def test_fight_with_less_than_two_boxers(ring_model, boxer1):
    """Test error when trying to conduct a fight with less than two boxers."""
    ring_model.enter_ring(boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()
    

##################################################
# Skill Calculation Test Case
##################################################

def test_get_fighting_skill(ring_model, boxer1):
    """Test that the fighting skill is correctly calculated."""
    
    age_modifier = -1 if boxer1.age < 25 else (-2 if boxer1.age > 35 else 0)
    skill = ring_model.get_fighting_skill(boxer1)
    expected_skill = (boxer1.weight * len(boxer1.name)) + (boxer1.reach / 10) + age_modifier  
    assert skill == expected_skill

##################################################
# Get Boxer Tests
##################################################

def test_get_boxers(ring_model, boxer1, boxer2):
    """Tests that get_boxers retuns the correct list."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    in_ring = ring_model.get_boxers()
    assert len(in_ring) == 2
    assert boxer1 in in_ring
    assert boxer2 in in_ring

def test_get_boxers_empty(ring_model, boxer1, boxer2):
    """Tests that get_boxers retuns an empty list when there is an empty ring."""
    in_ring = ring_model.get_boxers()
    assert len(in_ring) == 0