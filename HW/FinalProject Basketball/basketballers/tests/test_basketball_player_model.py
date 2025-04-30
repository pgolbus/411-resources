import time

import pytest

from basketballers.models.basketball_player_model import BasketballPlayer
from basketballers.models.basketball_general_model import GameModel


@pytest.fixture
def game_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return GameModel()

@pytest.fixture
def sample_basketball1(session):
    bballer = BasketballPlayer(name="Stephen Curry", position="G",team="Warriors", height_feet=6, height_inches=2, weight_pounds=185)
    session.add(bballer)
    session.commit()
    return bballer

@pytest.fixture
def sample_basketball2(session):
    bballer = BasketballPlayer(name="Giannis Antetokounmpo", position="F",team="Bucks", height_feet=6, height_inches=11, weight_pounds=243)
    session.add(bballer)
    session.commit()
    return bballer

@pytest.fixture
def sample_basketballers(sample_bballer1, sample_bballer2):
    return [sample_bballer1, sample_bballer2]

### --- Ring Clear ---

def test_clear_game(game_model):
    """Test that clear_game empties both teams."""
    game_model.team_1 = [1, 3]
    game_model.team_2 = [2, 4]
    game_model.clear_game()
    assert len(game_model.team_1) == 0
    assert len(game_model.team_2) == 0


def test_clear_game_empty(game_model, caplog):
    """Test that clear_game logs a warning when already empty."""
    with caplog.at_level("WARNING"):
        game_model.clear_game()
    assert len(game_model.team_1) == 0
    assert len(game_model.team_2) == 0
    assert "Attempted to clear an empty game" in caplog.text

"""
def test_get_boxers_empty(ring_model, caplog):
    #Test get_boxers logs when empty.
    with caplog.at_level("WARNING"):
        boxers = ring_model.get_boxers()
    assert boxers == []
    assert "Retrieving boxers from an empty ring." in caplog.text
    

def test_get_boxers_with_data(app, ring_model, sample_boxers):
    """Test get_boxers with two sample boxers."""
    ring_model.ring.extend([b.id for b in sample_boxers])
    boxers = ring_model.get_boxers()
    assert boxers == sample_boxers

def test_get_boxers_uses_cache(ring_model, sample_boxer1, mocker):
     ring_model.ring.append(sample_boxer1.id)
     ring_model._boxer_cache[sample_boxer1.id] = sample_boxer1
     ring_model._ttl[sample_boxer1.id] = time.time() + 100
     mock_get = mocker.patch("boxing.models.ring_model.Boxers.get_boxer_by_id")
     boxers = ring_model.get_boxers()
     assert boxers[0] == sample_boxer1
     mock_get.assert_not_called()
     
def test_get_boxers_refreshes_on_expired_ttl(ring_model, sample_boxer1, mocker):
     ring_model.ring.append(sample_boxer1.id)
     ring_model._boxer_cache[sample_boxer1.id] = mocker.Mock()
     ring_model._ttl[sample_boxer1.id] = time.time() - 1
     mock_get = mocker.patch("boxing.models.ring_model.Boxers.get_boxer_by_id", return_value=sample_boxer1)
     boxers = ring_model.get_boxers()
     assert boxers[0] == sample_boxer1
     mock_get.assert_called_once_with(sample_boxer1.id)
     

def test_cache_populated_on_get_boxers(ring_model, sample_boxer1, mocker):
     mock_get = mocker.patch("boxing.models.ring_model.Boxers.get_boxer_by_id", return_value=sample_boxer1)
     ring_model.ring.append(sample_boxer1.id)
     boxers = ring_model.get_boxers()
     assert sample_boxer1.id in ring_model._boxer_cache
     assert sample_boxer1.id in ring_model._ttl
     assert boxers[0] == sample_boxer1

def test_enter_ring(ring_model, sample_boxers, app):
     ring_model.enter_ring(sample_boxers[0].id)
     assert ring_model.ring == [sample_boxers[0].id]
     ring_model.enter_ring(sample_boxers[1].id)
     assert ring_model.ring == [sample_boxers[0].id, sample_boxers[1].id]
"""
def test_enter_game_full(game_model):
    """Test that enter_game raises an error when team is full."""
    game_model.team_1 = [1, 2]
    with pytest.raises(ValueError, match="Team 1 is already full."):
        game_model.enter_game(5, team=1)

# --- Fight Logic ---

def test_get_fighting_skill(ring_model, sample_boxers):
     expected_1 = 210 * 12 + (78 / 10)
     expected_2 = 220 * 10 + (71 / 10) - 1
     assert ring_model.get_fighting_skill(sample_boxers[0]) == expected_1
     assert ring_model.get_fighting_skill(sample_boxers[1]) == expected_2

def test_fight(ring_model, sample_boxers, caplog, mocker):
     ring_model.ring.extend(sample_boxers)
     mocker.patch("boxing.models.ring_model.RingModel.get_fighting_skill", side_effect=[2526.8, 2206.1])
     mocker.patch("boxing.models.ring_model.get_random", return_value=0.42)
     mocker.patch("boxing.models.ring_model.RingModel.get_boxers", return_value=sample_boxers)
     mock_update = mocker.patch("boxing.models.ring_model.Boxers.update_stats")
     winner = ring_model.fight()
     assert winner == "Muhammad Ali"
     mock_update.assert_any_call("win")
     mock_update.assert_any_call("loss")
     assert ring_model.ring == []

def test_play_game_with_empty_teams(game_model):
    """Test that play_game raises an error when teams are empty."""
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()
         
def test_play_game_with_one_player_each(game_model):
    """Test that play_game raises an error when teams have only one player each."""
    game_model.team_1 = [1]
    game_model.team_2 = [2]
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()

def test_clear_cache(game_model, sample_basketball1):
    """Test that clear_cache empties the player cache."""
    game_model._player_cache[sample_basketball1.id] = sample_basketball1
    game_model._ttl[sample_basketball1.id] = time.time() + 100
    game_model.clear_cache()
    assert game_model._player_cache == {}
    assert game_model._ttl == {}
