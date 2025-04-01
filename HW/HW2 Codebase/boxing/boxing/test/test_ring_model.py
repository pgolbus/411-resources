import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer, update_boxer_stats


@pytest.fixture
def ring_model():
    return RingModel()

@pytest.fixture
def sample_boxers():
    boxer1 = Boxer(1, "Ali", 180, 185, 75.0, 28)
    boxer2 = Boxer(2, "Tyson", 200, 178, 72.0, 32)
    return boxer1, boxer2

def test_enter_ring_adds_boxers(ring_model, sample_boxers):
    boxer1, _ = sample_boxers
    ring_model.enter_ring(boxer1)
    assert len(ring_model.ring) == 1

def test_enter_ring_invalid_type(ring_model):
    with pytest.raises(TypeError):
        ring_model.enter_ring("not a boxer")

def test_enter_ring_full_ring(ring_model, sample_boxers):
    boxer1, boxer2 = sample_boxers
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)
    with pytest.raises(ValueError):
        ring_model.enter_ring(Boxer(3, "New Guy", 150, 170, 68.0, 30))

def test_clear_ring(ring_model, sample_boxers):
    boxer1, _ = sample_boxers
    ring_model.enter_ring(boxer1)
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0

def test_get_boxers_success(ring_model, sample_boxers):
    boxer1, _ = sample_boxers
    ring_model.enter_ring(boxer1)
    assert ring_model.get_boxers()[0].name == "Ali"

def test_get_boxers_empty_ring():
    ring = RingModel()
    # No boxers entered
    with pytest.raises(ValueError, match="No boxers in the ring"):
        ring.get_boxers()

def test_fight_simulation(ring_model, sample_boxers, mocker):
    boxer1, boxer2 = sample_boxers
    ring_model.enter_ring(boxer1)
    ring_model.enter_ring(boxer2)

    mocker.patch("boxing.models.ring_model.get_random", return_value=0.4)
    mock_update = mocker.patch("boxing.models.ring_model.update_boxer_stats")

    winner_name = ring_model.fight()
    assert winner_name in [boxer1.name, boxer2.name]
    assert len(ring_model.ring) == 0
    assert mock_update.call_count == 2