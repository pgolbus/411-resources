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
    return Boxer(id=1, name="Boxer 1", age=20, weight=165, reach=50)


@pytest.fixture()
def boxer2():
    """Fixture to create another Boxer instance for testing."""
    return Boxer(id=2, name="Boxer 2", age=22, weight=185, reach=60)


