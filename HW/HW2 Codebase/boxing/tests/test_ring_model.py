import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture
def ring():
    return RingModel()

@pytest.fixture
def boxer1():
    return Boxer(
        id=1,
        name="Mike Tyson",
        weight=220,
        height=178,
        reach=71.0,
        age=25
    )

@pytest.fixture
def boxer2():
    return Boxer(
        id=2,
        name="Muhammad Ali",
        weight=210,
        height=191,
        reach=78.0,
        age=30
    )

@pytest.fixture
def boxer3():
    return Boxer(
        id=3,
        name="Floyd Mayweather",
        weight=150,
        height=173,
        reach=72.0,
        age=38
    )

def test_ring_model_init():
    ring = RingModel()
    assert ring is not None
    assert isinstance(ring, RingModel)
    assert ring.ring == []

def test_enter_ring_success(ring, boxer1):
    ring.enter_ring(boxer1)
    assert len(ring.ring) == 1
    assert ring.ring[0] == boxer1

def test_enter_ring_two_boxers(ring, boxer1, boxer2):
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    assert len(ring.ring) == 2
    assert ring.ring[0] == boxer1
    assert ring.ring[1] == boxer2

def test_enter_ring_full(ring, boxer1, boxer2, boxer3):
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring.enter_ring(boxer3)

def test_enter_ring_invalid_type(ring):
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'str'"):
        ring.enter_ring("Not a boxer")

def test_clear_ring_with_boxers(ring, boxer1, boxer2):
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    ring.clear_ring()
    assert len(ring.ring) == 0

def test_clear_empty_ring(ring):
    ring.clear_ring()
    assert len(ring.ring) == 0

def test_get_boxers_empty(ring):
    boxers = ring.get_boxers()
    assert isinstance(boxers, list)
    assert len(boxers) == 0

def test_get_boxers_with_one(ring, boxer1):
    ring.enter_ring(boxer1)
    boxers = ring.get_boxers()
    assert len(boxers) == 1
    assert boxers[0] == boxer1

def test_get_boxers_with_two(ring, boxer1, boxer2):
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    boxers = ring.get_boxers()
    assert len(boxers) == 2
    assert boxers[0] == boxer1
    assert boxers[1] == boxer2

def test_get_fighting_skill_young_boxer(ring, boxer1):
    # boxer1 is 25 years old
    skill = ring.get_fighting_skill(boxer1)
    assert isinstance(skill, float)
    # Test the formula: (weight * len(name)) + (reach / 10) + age_modifier
    expected_skill = (220 * len("Mike Tyson")) + (71.0 / 10) + 0  # age_modifier is 0 for age 25
    assert skill == expected_skill

def test_get_fighting_skill_old_boxer(ring, boxer3):
    # boxer3 is 38 years old
    skill = ring.get_fighting_skill(boxer3)
    assert isinstance(skill, float)
    # Test the formula with age penalty
    expected_skill = (150 * len("Floyd Mayweather")) + (72.0 / 10) - 2  # age_modifier is -2 for age > 35
    assert skill == expected_skill

def test_fight_not_enough_boxers(ring, boxer1):
    ring.enter_ring(boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring.fight()

def test_fight_success(ring, boxer1, boxer2, mocker):
    # Mock the random number generator to make the fight deterministic
    mocker.patch('boxing.models.ring_model.get_random', return_value=0.3)
    
    # Mock the update_boxer_stats function
    mock_update = mocker.patch('boxing.models.ring_model.update_boxer_stats')
    
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    
    winner_name = ring.fight()
    
    # Verify the ring is cleared after the fight
    assert len(ring.ring) == 0
    
    # Verify update_boxer_stats was called correctly
    assert mock_update.call_count == 2
    
    # Verify the winner is one of the boxers
    assert winner_name in [boxer1.name, boxer2.name]

def test_fight_clears_ring(ring, boxer1, boxer2, mocker):
    mocker.patch('boxing.models.ring_model.get_random', return_value=0.5)
    mocker.patch('boxing.models.ring_model.update_boxer_stats')
    
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    ring.fight()
    
    assert len(ring.ring) == 0

def test_fight_updates_stats(ring, boxer1, boxer2, mocker):
    mocker.patch('boxing.models.ring_model.get_random', return_value=0.5)
    mock_update = mocker.patch('boxing.models.ring_model.update_boxer_stats')
    
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    winner_name = ring.fight()
    
    # Check that update_boxer_stats was called for both boxers
    assert mock_update.call_count == 2
    
    # Get the actual calls made to update_boxer_stats
    calls = mock_update.call_args_list
    
    # Find which boxer won and lost based on the winner_name
    if winner_name == boxer1.name:
        winner_id, loser_id = boxer1.id, boxer2.id
    else:
        winner_id, loser_id = boxer2.id, boxer1.id
    
    # Verify the winner and loser stats were updated correctly
    assert any(call.args == (winner_id, 'win') for call in calls)
    assert any(call.args == (loser_id, 'loss') for call in calls)