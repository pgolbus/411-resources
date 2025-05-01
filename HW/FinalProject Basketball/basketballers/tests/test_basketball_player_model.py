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

def test_get_players_empty(game_model, caplog):
    # Test get_players logs when both teams are empty.
    with caplog.at_level("WARNING"):
        players = game_model.get_players()
    assert players == []
    assert "Retrieving players from an empty game." in caplog.text


def test_get_players_with_data(game_model, sample_players):
    # Add sample players to both teams
    game_model.team_1.append(sample_players[0].id)
    game_model.team_2.append(sample_players[1].id)
    game_model._player_cache[sample_players[0].id] = sample_players[0]
    game_model._player_cache[sample_players[1].id] = sample_players[1]
    game_model._ttl[sample_players[0].id] = time.time() + 100
    game_model._ttl[sample_players[1].id] = time.time() + 100

    players = game_model.get_players()
    assert sample_players[0] in players
    assert sample_players[1] in players


def test_get_players_uses_cache(game_model, sample_player1, mocker):
    game_model.team_1.append(sample_player1.id)
    game_model._player_cache[sample_player1.id] = sample_player1
    game_model._ttl[sample_player1.id] = time.time() + 100
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id")
    players = game_model.get_players()
    assert players[0] == sample_player1
    mock_get.assert_not_called()

def test_get_players_refreshes_on_expired_ttl(game_model, sample_player1, mocker):
    game_model.team_2.append(sample_player1.id)
    game_model._player_cache[sample_player1.id] = mocker.Mock()
    game_model._ttl[sample_player1.id] = time.time() - 1
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id", return_value=sample_player1)
    players = game_model.get_players()
    assert players[0] == sample_player1
    mock_get.assert_called_once_with(sample_player1.id)

def test_enter_game(game_model, sample_players):
    game_model.enter_game(sample_players[0].id, team=1)
    assert game_model.team_1 == [sample_players[0].id]
    game_model.enter_game(sample_players[1].id, team=2)
    assert game_model.team_2 == [sample_players[1].id]
"""    
     

def test_cache_populated_on_get_boxers(ring_model, sample_boxer1, mocker):
     mock_get = mocker.patch("boxing.models.ring_model.Boxers.get_boxer_by_id", return_value=sample_boxer1)
     ring_model.ring.append(sample_boxer1.id)
     boxers = ring_model.get_boxers()
     assert sample_boxer1.id in ring_model._boxer_cache
     assert sample_boxer1.id in ring_model._ttl
     assert boxers[0] == sample_boxer1

"""
def test_enter_game_full(game_model):
    """Test that enter_game raises an error when team is full."""
    game_model.team_1 = [1, 2]
    with pytest.raises(ValueError, match="Team 1 is already full."):
        game_model.enter_game(5, team=1)

"""
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

     """

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
