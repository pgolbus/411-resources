import pytest
from unittest.mock import patch

from hypothesis import given, strategies as st
from boxing.models.boxers_model import (
    Boxer, 
    get_weight_class,  
    create_boxer,       
    get_boxer_by_id, 
    delete_boxer
)
from boxing.models.ring_model import RingModel

#Property based testing to find edge cases
@given(st.integers(min_value=125, max_value=500))
def test_weight_class_property(weight):
    """Test that any valid weight has a weight class."""
    weight_class = get_weight_class(weight)
    assert weight_class in ["FEATHERWEIGHT", "LIGHTWEIGHT", "MIDDLEWEIGHT", "HEAVYWEIGHT"]

@pytest.fixture
def ring():
    """Fixture providing a clean RingModel for each test."""
    return RingModel()

@pytest.fixture
def sample_boxer1():
    """Fixture providing a sample boxer for testing."""
    return Boxer(1, 'Rocky', 175, 71, 76.0, 32)

@pytest.fixture
def sample_boxer2():
    """Fixture providing another sample boxer for testing."""
    return Boxer(2, 'Apollo', 185, 74, 78.0, 30)

""" 
ring = ring for boxers
sample_boxer1 = first boxer
sample_boxer 2 = second boxer 
mock_update_stats = sample score for win/lose for boxers
mock_get_random = sample score to make certain boxer win
"""
def test_enter_ring(ring, sample_boxer1):
    """Test adding a boxer to the ring."""
    ring.enter_ring(sample_boxer1)
    
    """Get boxers for the ring"""
    boxers = ring.get_boxers()
    assert len(boxers) == 1
    assert boxers[0].id == sample_boxer1.id
    assert boxers[0].name == sample_boxer1.name


def test_enter_ring_full(ring, sample_boxer1, sample_boxer2):
    """Test adding a boxer to a full ring."""
    ring.enter_ring(sample_boxer1)
    ring.enter_ring(sample_boxer2)
    
    # Try to add a third boxer
    with pytest.raises(ValueError, match="Ring is full"):
        ring.enter_ring(sample_boxer1)


def test_clear_ring(ring, sample_boxer1, sample_boxer2):
    """Test clearing the ring."""
    ring.enter_ring(sample_boxer1)
    ring.enter_ring(sample_boxer2)
    
    ring.clear_ring()
    
    boxers = ring.get_boxers()
    assert len(boxers) == 0


def test_get_fighting_skill(ring, sample_boxer1, sample_boxer2):
    """Test calculating fighting skill."""
    skill1 = ring.get_fighting_skill(sample_boxer1)
    skill2 = ring.get_fighting_skill(sample_boxer2)
    
    # Verify skills are calculated as expected
    assert skill1 > 0
    assert skill2 > 0
    assert isinstance(skill1, float)
    assert isinstance(skill2, float)


@patch('boxing.models.ring_model.get_random')
@patch('boxing.models.ring_model.update_boxer_stats')
def test_fight(mock_update_stats, mock_get_random, ring, sample_boxer1, sample_boxer2):
    """Test a boxing match."""
    mock_get_random.return_value = 0.3  # Set a value that ensures boxer1 wins
    
    ring.enter_ring(sample_boxer1)
    ring.enter_ring(sample_boxer2)
    
    winner = ring.fight()
    
    # Verify winner and that stats were updated
    assert winner == sample_boxer1.name
    
    # Verify stats were updated
    mock_update_stats.assert_any_call(sample_boxer1.id, 'win')
    mock_update_stats.assert_any_call(sample_boxer2.id, 'loss')
    
    # Verify ring was cleared
    assert len(ring.get_boxers()) == 0


def test_fight_not_enough_boxers(ring, sample_boxer1):
    """Test fighting with insufficient boxers."""
    ring.enter_ring(sample_boxer1)
    
    with pytest.raises(ValueError, match="There must be two boxers"):
        ring.fight()
        
        
#integration testing
@pytest.mark.xfail(reason="Integration test: Create boxers and have them fight.")
def test_create_boxer_and_fight(monkeypatch):
    """Integration test: Create boxers and have them fight."""
    # Mock the DB functions
    db_boxer1 = None
    db_boxer2 = None
    
    def mock_create_boxer(name, weight, height, reach, age):
        nonlocal db_boxer1, db_boxer2
        if not db_boxer1:
            db_boxer1 = (1, name, weight, height, reach, age)
            return 1
        else:
            db_boxer2 = (2, name, weight, height, reach, age)
            return 2
    
    def mock_get_boxer_by_id(boxer_id):
        from boxing.models.boxers_model import Boxer
        if boxer_id == 1 and db_boxer1:
            return Boxer(db_boxer1[0], db_boxer1[1], db_boxer1[2], db_boxer1[3], db_boxer1[4], db_boxer1[5])
        elif boxer_id == 2 and db_boxer2:
            return Boxer(db_boxer2[0], db_boxer2[1], db_boxer2[2], db_boxer2[3], db_boxer2[4], db_boxer2[5])
        return None
    
    def mock_update_stats(boxer_id, result):
        # Just a stub - no actual update needed for this test
        pass
    
    monkeypatch.setattr("boxing.models.boxers_model.create_boxer", mock_create_boxer)
    monkeypatch.setattr("boxing.models.boxers_model.get_boxer_by_id", mock_get_boxer_by_id)
    monkeypatch.setattr("boxing.models.boxers_model.update_boxer_stats", mock_update_stats)
    
    # Create two boxers
    boxer1_id = create_boxer("Rocky", 175, 71, 76.0, 32)
    boxer2_id = create_boxer("Apollo", 185, 74, 78.0, 30)
    
    # Get the boxers
    boxer1 = get_boxer_by_id(boxer1_id)
    boxer2 = get_boxer_by_id(boxer2_id)
    
    # Create a ring and have them fight
    ring = RingModel()
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    
    # Mock the random value to make the result deterministic
    monkeypatch.setattr("boxing.models.ring_model.get_random", lambda: 0.2)
    
    winner = ring.fight()
    
    # Assert the winner is one of the two boxers
    assert winner in [boxer1.name, boxer2.name]