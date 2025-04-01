import pytest
from unittest.mock import MagicMock
from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

# Fixtures
@pytest.fixture()
def boxer1():
    """Fixture to create a new Boxer instance for testing."""
    return Boxer(id=1, name="Boxer One", weight=130, reach=70, age=30, height=180)

@pytest.fixture()
def boxer2():
    """Fixture to create another Boxer instance for testing."""
    return Boxer(id=2, name="Boxer Two", weight=170, reach=72, age=32, height=170)

@pytest.fixture()
def ring_model():
    """Fixture to create a new RingModel instance for testing."""
    return RingModel()


##################################################
# Ring Management Test Cases
##################################################

def test_enter_ring(ring_model, boxer1):
    """Test adding a boxer to the ring."""
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "Boxer One"

def test_enter_ring_full(ring_model, boxer1, boxer2):
    """Test attempting to add a boxer when the ring is full."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(Boxer(id=3, name="Boxer Three", weight=175, reach=68, age=28, height=160))


def test_enter_ring_invalid_type(ring_model):
    """Test adding an invalid type to the ring."""
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'dict'"):
        ring_model.enter_ring({"name": "Invalid Boxer"})

def test_clear_ring(ring_model, boxer1, boxer2):
    """Test clearing the ring after a fight."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    assert len(ring_model.ring) == 2

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0

def test_clear_ring_empty(ring_model):
    """Test clearing an empty ring should raise an error."""
    with pytest.raises(ValueError, match="Attempted to clear an empty ring."):
        ring_model.clear_ring()


##################################################
# Fight Test Cases
##################################################

def test_fight_successful(ring_model, boxer1, boxer2, mocker):
    """Test a successful fight between two boxers."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    # Mocking external function calls if necessary
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.5)  # Simulate a random outcome
    mocker.patch("boxing.models.ring_model.update_boxer_stats", return_value=None)

    winner = ring_model.fight()

    # Check if the fight was resolved and stats were updated
    assert winner in ["Boxer One", "Boxer Two"]
    assert len(ring_model.ring) == 0  # The ring should be empty after the fight

def test_fight_not_enough_boxers(ring_model, boxer1):
    """Test attempting to fight with fewer than two boxers in the ring."""
    ring_model.enter_ring(boxer1)

    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()


##################################################
# Skill Calculation Test Cases
##################################################

def test_get_fighting_skill(ring_model, boxer1, boxer2):
    """Test the calculation of a boxer's fighting skill."""
    skill1 = ring_model.get_fighting_skill(boxer1)
    skill2 = ring_model.get_fighting_skill(boxer2)

    assert isinstance(skill1, float)
    assert isinstance(skill2, float)
    assert skill1 != skill2  # Skill should differ between the two boxers


##################################################
# Utility Test Cases
##################################################

def test_get_boxers(ring_model, boxer1, boxer2):
    """Test getting the boxers currently in the ring."""
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert boxers[0].name == "Boxer One"
    assert boxers[1].name == "Boxer Two"

def test_get_boxers_empty_ring(ring_model):
    """Test getting boxers from an empty ring."""
    boxers = ring_model.get_boxers()
    assert len(boxers) == 0


