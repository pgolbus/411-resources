import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture
def ring_model():
    """Fixture to provide a new instance of RingModel for each test.

    """
    return RingModel()

# Fixtures providing sample boxers
@pytest.fixture
def sample_boxer1():
    boxer = Boxer(
        id=1,
        name="Muhammad Ali",
        weight=210,
        height=191,
        reach=78,
        age=32
    )
    return boxer

@pytest.fixture
def sample_boxer2():
    boxer = Boxer(
        id=2,
        name="Mike Tyson",
        weight=220,
        height=178,
        reach=71,
        age=24
    )
    return boxer

@pytest.fixture
def sample_boxers(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


##########################################################
# Boxer Prep
##########################################################


def test_clear_ring(ring_model, sample_boxers):
    """Test that clear_rimg empties the ring.

    """
    ring_model.ring.extend(sample_boxers)

    ring_model.clear_ring()

    assert len(ring_model.ring) == 0, "Ring should be empty after calling clear_ring."

def test_clear_ring_empty(ring_model, caplog):
    """Test that calling clear_ring on an empty ring logs a warning and keeps the ring empty.

    """
    with caplog.at_level("WARNING"):
        ring_model.clear_ring()

    assert len(ring_model.ring) == 0, "Ring should remain empty if it was already empty."

    assert "Attempted to clear an empty ring." in caplog.text, "Expected a warning when clearing an empty ring."

def test_get_boxers_empty(ring_model, caplog):
    """Test that get_boxers returns an empty list when there are no boxers and logs a warning.

    """
    with caplog.at_level("WARNING"):
        boxers = ring_model.get_boxers()

    assert boxers == [], "Expected get_boxers to return an empty list when there are no boxers."

    assert "Retrieving boxers from an empty ring." in caplog.text, "Expected a warning when getting boxers from an empty ring."

def test_get_boxers_with_data(ring_model, sample_boxers):
    """Test that get_boxers returns the correct list when there are boxers.

    """
    ring_model.ring.extend(sample_boxers)

    boxers = ring_model.get_boxers()
    assert boxers == ring_model.ring, "Expected get_boxers to return the correct boxers list."

def test_enter_ring(ring_model, sample_boxers):
    """Test that a boxer is correctly added to the ring.

    """
    ring_model.enter_ring(sample_boxers[0])

    assert len(ring_model.ring) == 1, "Ring should contain one boxer after calling enter_ring."
    assert ring_model.ring[0].name == "Muhammad Ali", "Expected 'Muhammad Ali' in the ring."

    ring_model.enter_ring(sample_boxers[1])
    assert len(ring_model.ring) == 2, "Ring should contain two boxers after calling enter_ring."
    assert ring_model.ring[1].name == "Mike Tyson", "Expected 'Mike Tyson' in the ring."

def test_enter_ring_full(ring_model, sample_boxers):
    """Test that enter_ring raises an error when the ring is full.

    """
    ring_model.ring.extend(sample_boxers)

    new_boxer = Boxer(id=3, name="Joe Frazier", weight=205, height=182, reach=76, age=30)

    with pytest.raises(ValueError, match="Ring is full"):
        ring_model.enter_ring(new_boxer)

    assert len(ring_model.ring) == 2, "Ring should still contain only 2 boxers after trying to add a third."

def test_enter_ring_invalid_type(ring_model):
    """Test that enter_ring raises a TypeError when given a non-Boxer object."""
    invalid_inputs = ["Mike Tyson", 123, {"name": "Ali", "weight": 210}, None]

    for invalid_input in invalid_inputs:
        with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
            ring_model.enter_ring(invalid_input)

    assert len(ring_model.ring) == 0, "Ring should remain empty when invalid inputs are provided."


##########################################################
# Fight
##########################################################


def test_get_fighting_skill(ring_model, sample_boxer1, sample_boxer2):
    """Test the get_fighting_skill method.

    """
    boxer_1, boxer_2 = sample_boxer1, sample_boxer2
    expected_score_1 = (210 * 12) + (78 / 10)  # 210 * 12 + 7.8 = 2527.8
    assert ring_model.get_fighting_skill(boxer_1) == expected_score_1, f"Expected score: {expected_score_1}, got {ring_model.get_fighting_skill(boxer_1)}"

    expected_score_2 = (220 * 10) + (71 / 10) - 1  # 220 * 10 + 7.1 - 1 = 2206.1
    assert ring_model.get_fighting_skill(boxer_2) == expected_score_2, f"Expected score: {expected_score_2}, got {ring_model.get_fighting_skill(boxer_2)}"

def test_fight(ring_model, sample_boxers, caplog, mocker):
    """Test the fight method with sample boxers.

    """
    ring_model.ring.extend(sample_boxers)

    mocker.patch("boxing.models.ring_model.RingModel.get_fighting_skill", side_effect=[2526.8, 2206.1])
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.42)
    mock_update_stats = mocker.patch("boxing.models.ring_model.update_boxer_stats")

    winner_name = ring_model.fight()

    assert winner_name == "Muhammad Ali", f"Expected boxer 1 to win, but got {winner_name}"

    mock_update_stats.assert_any_call(1, 'win')  # boxer_1 is the winner
    mock_update_stats.assert_any_call(2, 'loss')  # boxer_2 is the loser

    assert len(ring_model.ring) == 0, "Ring should be empty after the fight."

    assert "The winner is: Muhammad Ali" in caplog.text, "Expected winner log message not found."

def test_fight_with_empty_ring(ring_model):
    """Test that the fight method raises a ValueError when there are fewer than two boxers.

    """
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_with_one_boxer(ring_model, sample_boxer1):
    """Test that the fight method raises a ValueError when there's only one boxer.

    """
    ring_model.ring.append(sample_boxer1)

    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()
