import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

#ring and 2 boxer fixtures to be used as parameters in later unit tests

@pytest.fixture
def ring_model():
    """Provides a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def boxer1():
    return Boxer(id=1, name="testboxer1", weight=300, age=30, reach=75)

@pytest.fixture
def boxer2():
    return Boxer(id=2, name="testboxer2", weight=250, age=25, reach=80)

##################################################
# Entering and Clearing Ring Test Cases
##################################################

def test_enter_boxer_into_ring(ring_model, boxer1):
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "testboxer1"




