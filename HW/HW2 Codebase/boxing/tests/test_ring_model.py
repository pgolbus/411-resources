from dataclasses import asdict
import pytest
from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

@pytest.fixture()
def ring_model():
    """Provides a fresh instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_stats(mocker):
    """Mocks update_boxer_stats for testing."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats", autospec=True)

@pytest.fixture
def sample_boxer1():
    """Creates a sample boxer with predefined attributes."""
    return Boxer(1, "Boxer 1", 135, 68, 13, 30)

@pytest.fixture
def sample_boxer2():
    """Creates another sample boxer with different attributes."""
    return Boxer(2, "Boxer 2", 130, 83, 15, 29)

@pytest.fixture
def sample_boxer3():
    return Boxer(3, 'Boxer 3', 190, 65, 3.5, 28)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    """Provides a list of two sample boxers."""
    return [sample_boxer1, sample_boxer2]

def test_enter_ring_valid_boxers(ring_model, sample_boxer1, sample_boxer2):
    """Ensures valid boxers can enter the ring."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    assert len(ring_model.ring) == 2

def test_enter_ring_invalid_type(ring_model):
    """Ensures entering non-boxer objects raises a TypeError."""
    with pytest.raises(TypeError):
        ring_model.enter_ring("not_a_boxer")

def test_enter_ring_over_capacity(ring_model, sample_boxer1, sample_boxer2):
    """Ensures entering more than two boxers raises a ValueError."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError):
        ring_model.enter_ring(sample_boxer3)

def test_fight_too_few_boxers(ring_model, sample_boxer1):
    """Ensures a fight cannot start with less than two boxers."""
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError):
        ring_model.fight()

def test_get_boxers_returns_boxers(ring_model, sample_boxer1):
    """Verifies the retrieval of boxers from the ring."""
    ring_model.enter_ring(sample_boxer1)
    boxers = ring_model.get_boxers()
    assert len(boxers) == 1
    assert boxers[0].name == "Boxer 1"

def test_clear_ring(ring_model, sample_boxer1):
    """Ensures the ring is cleared properly."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.clear_ring()
    assert ring_model.ring == []

def test_clear_ring_empty_raises(ring_model):
    """Ensures clearing an already empty ring raises a ValueError."""
    with pytest.raises(ValueError):
        ring_model.clear_ring()

def test_get_fighting_skill(ring_model, sample_boxer1):
    """Tests skill calculation for a boxer."""
    skill = ring_model.get_fighting_skill(sample_boxer1)
    
    name_length = len(sample_boxer1.name)
    reach_component = sample_boxer1.reach / 10
    age_adjustment = 0 
    
    expected_skill = (130 * name_length) + reach_component + age_adjustment
    assert skill == expected_skill

def test_fight_outcome_and_stat_update(ring_model, sample_boxer1, sample_boxer2, mocker):
    """Tests fight outcomes and verifies stat updates are called."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    mock_update = mocker.patch("boxing.models.ring_model.update_boxer_stats", autospec=True)
    mock_random = mocker.patch("boxing.models.ring_model.get_random", return_value=0.9, autospec=True)

    winner = ring_model.fight()
    
    assert winner in [sample_boxer1.name, sample_boxer2.name]
    assert mock_update.call_count == 2
