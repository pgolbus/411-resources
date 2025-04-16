import time
import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxers


@pytest.fixture
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()


@pytest.fixture
def sample_boxer1(session):
    boxer = Boxers(name="Muhammad Ali", weight=210, height=191, reach=78, age=32)
    session.add(boxer)
    session.commit()
    return boxer


@pytest.fixture
def sample_boxer2(session):
    boxer = Boxers(name="Mike Tyson", weight=220, height=178, reach=71, age=24)
    session.add(boxer)
    session.commit()
    return boxer


@pytest.fixture
def sample_boxers(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


# --- Ring Clear ---

def test_clear_ring(ring_model):
    """Test that clear_ring empties the ring."""
    ring_model.ring = [1, 2]
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0


def test_clear_ring_empty(ring_model, caplog):
    """Test that clear_ring logs a warning when already empty."""
    with caplog.at_level("WARNING"):
        ring_model.clear_ring()
    assert len(ring_model.ring) == 0
    assert "Attempted to clear an empty ring." in caplog.text


def test_get_boxers_empty(ring_model, caplog):
    """Test get_boxers logs when empty."""
    with caplog.at_level("WARNING"):
        boxers = ring_model.get_boxers()
    assert boxers == []
    assert "Retrieving boxers from an empty ring." in caplog.text


def test_get_boxers_with_data(app, ring_model, sample_boxers):
    """Test get_boxers with two sample boxers."""
    ring_model.ring.extend([b.id for b in sample_boxers])
    boxers = ring_model.get_boxers()
    assert boxers == sample_boxers


def test_get_boxers_refreshes_on_expired_ttl(ring_model, sample_boxer1, mocker):
    ring_model.ring.append_
