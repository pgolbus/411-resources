import pytest
from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel
from boxing.utils.api_utils import get_random
from boxing.models.boxers_model import Boxer, create_boxer, get_boxer_by_name


@pytest.fixture()
def boxer1():
    """Fixture for Boxer 1."""
    return Boxer(id=1, name='Boxer 1', weight=125, height=70, reach=180, age=28)

@pytest.fixture()
def boxer2():
    """Fixture for Boxer 2."""
    return Boxer(id=2, name='Boxer 2', weight=130, height=72, reach=175, age=25)

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()


def test_fight_success(monkeypatch, ring_model, boxer1, boxer2):
    """
    Test the fight function.
    We control randomness by patching get_random to return a fixed value.
    We also patch update_boxer_stats to avoid side effects.
    """
    monkeypatch.setattr("boxing.models.ring_model.get_random", lambda: 0.0)
   
    monkeypatch.setattr("boxing.models.ring_model.update_boxer_stats", lambda boxer_id, result: None)

   
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    winner_name = ring_model.fight()
    assert winner_name == boxer1.name
    
    assert len(ring_model.ring) == 0


def test_fight_with_less_than_two_boxers(ring_model, boxer1):
    """Test trying to start a fight with fewer than two boxers."""
    ring_model.enter_ring(boxer1)

    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_with_full_ring(ring_model, boxer1, boxer2):
    """Test trying to enter a third boxer into a full ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(Boxer(id=3, name='Boxer 3', weight=135, height=73, reach=185, age=27))

def test_fight_while_ring_is_empty(ring_model):
    """Test trying to start a fight with an empty ring."""
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_skill_computation(ring_model, boxer1, boxer2):
    """Test the calculation of fighting skill (a value that should affect the fight result)."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    skill_1 = ring_model.get_fighting_skill(boxer1)
    skill_2 = ring_model.get_fighting_skill(boxer2)

    assert skill_1 != skill_2, "Boxer skills should differ based on attributes."
    assert isinstance(skill_1, float) and isinstance(skill_2, float), "Fighting skills should be floats."

def test_clear_ring(ring_model, boxer1, boxer2):
    """Test clearing the ring after a fight."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    assert len(ring_model.ring) == 2, "Ring should contain 2 boxers before clearing."
    
    ring_model.clear_ring()
    
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing."

def test_enter_ring_invalid_type(ring_model, boxer1):
    """Test entering a non-boxer type into the ring."""
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'dict'"):
        ring_model.enter_ring({'name': 'Invalid Boxer', 'weight': 80})

def test_enter_ring_full(ring_model, boxer1, boxer2):
    """Test entering a boxer into a full ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(Boxer(id=3, name='Boxer 3', weight=135, height=73, reach=185, age=27))


def test_get_fighting_skill(ring_model, boxer1, boxer2):
    """Test fighting skill computation based on boxer's attributes."""
    skill1 = ring_model.get_fighting_skill(boxer1)
    skill2 = ring_model.get_fighting_skill(boxer2)

    assert isinstance(skill1, float), "Fighting skill should be a float."
    assert isinstance(skill2, float), "Fighting skill should be a float."
    assert skill1 != skill2, "Fighting skills should differ for different boxers."
    

def test_get_boxers(ring_model, boxer1, boxer2):
    """Test retrieving boxers currently in the ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    boxers_in_ring = ring_model.get_boxers()

    assert len(boxers_in_ring) == 2, "There should be exactly two boxers in the ring."
    assert boxers_in_ring[0].name in ['Boxer 1', 'Boxer 2'], "First boxer should be Boxer 1 or Boxer 2."
    assert boxers_in_ring[1].name in ['Boxer 1', 'Boxer 2'], "Second boxer should be Boxer 1 or Boxer 2."

def test_get_boxers_empty_ring(ring_model):
    """Test retrieving boxers from an empty ring."""
    boxers_in_ring = ring_model.get_boxers()
    assert len(boxers_in_ring) == 0, "Ring should be empty."
