from dataclasses import asdict

import pytest

from boxing.models.boxers_model import *
from boxing.models.ring_model import *

@pytest.fixture()
def fight_test(ring):
    return ring.fight()

@pytest.fixture()
def test_lessthan2Boxers():
    return true

@pytest.fixture()
def test_clearRing():
    return true

@pytest.fixture()
def test_enterRing():
    return true

@pytest.fixture()
def test_enterRingButBNotBoxers():
    return true

@pytest.fixture()
def test_addtoFullRing(full_ring, sample_boxer1):
    """Test error when adding a boxer to a full ring.

    """
    with pytest.raises(ValueError, match="Full ring"): 
            ring_model.enter_ring(sample_boxer1)

@pytest.fixture()
def test_getBoxers():
    return true

@pytest.fixture()
def test_getFightingSkills():
    return true
