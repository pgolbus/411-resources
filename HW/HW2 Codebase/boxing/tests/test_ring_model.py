import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer
#ring and 2 boxer fixtures to be used as parameters in later unit tests

@pytest.fixture
def ring_model():
    return RingModel()

@pytest.fixture
def boxer1():
    return Boxer(id=1, name="testboxer1", weight=300, age=30, reach=75)

@pytest.fixture
def boxer2():
    return Boxer(id=2, name="testboxer2", weight=250, age=25, reach=80)

##################################################
# Enter/Clear Ring Test Cases
##################################################

def test_enter_boxer_into_ring(ring_model, boxer1):
    """test adding boxer to ring
    """
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "testboxer1"

def test_enter_boxer_in_full_ring(ring_model, boxer1, boxer2):
    """test enter_ring raises error for more than two boxers in ring
    """
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    with pytest.raises(ValueError, match="Ring is full"):
        ring_model.enter_ring(Boxer(id=3, name="testboxer3", weight=350, age=35, reach=85))

def test_clear_ring(ring_model, boxer1):
    """ test clearing ring
    """
    ring_model.enter_ring(boxer1)
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0

def test_clear_empty_ring(ring_model):
    """test clear_ring when the ring is already clear
    """
    ring_model.clear_ring()  
    assert ring_model.ring == []

##################################################
# Fight Test Cases
##################################################

    
def test_fight(ring_model, boxer1, boxer2, mock_update_boxer_stats, mock_get_random):
    """tests that fight returns a winner, updates boxer stats, and clears ring
    """
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    winner = ring_model.fight()

    assert winner in [boxer1.name, boxer2.name]
    mock_update_boxer_stats.assert_any_call(boxer1.id, "win")
    mock_update_boxer_stats.assert_any_call(boxer2.id, "loss")
    assert mock_update_boxer_stats.call_count == 2
    
    assert len(ring_model.ring) == 0	

    
def test_fight_without_two_boxers(ring_model, boxer1):
    """
    test fight raises error if fight initiated with fewer than two boxers in the ring
    """
    ring_model.enter_ring(boxer1)
    with pytest.raises(ValueError, match="There must be two boxers"):
        ring_model.fight()

##################################################
# Get Boxer Test Cases
##################################################

def test_get_boxers(ring_model, boxer1, boxer2):
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert boxers[0].name == "testboxer1"
    assert boxers[1].name == "testboxer2"


