import time

import pytest

from basketballers.models.basketball_player_model import BasketballPlayer
from basketballers.models.basketball_game_model import GameModel


@pytest.fixture
def game_model():
# Fixture to provide a new instance of GameModel for each test.
    return GameModel()

# Fixture providing sample players
@pytest.fixture
def sample_players(session):
    """Creates 4 basketball players in the DB."""
    players = [
        BasketballPlayer(full_name="Stephen Curry", position="G", team="Warriors", height_feet=6, height_inches=2, weight_pounds=185),
        BasketballPlayer(full_name="LeBron James", position="F", team="Lakers", height_feet=6, height_inches=9, weight_pounds=250),
        BasketballPlayer(full_name="Kevin Durant", position="F", team="Suns", height_feet=6, height_inches=10, weight_pounds=240),
        BasketballPlayer(full_name="Joel Embiid", position="C", team="76ers", height_feet=7, height_inches=0, weight_pounds=280),
    ]
    session.add_all(players)
    session.commit()
    return players

@pytest.fixture
def sample_player1(sample_players):
    return sample_players[0]


### --- Game Management ---

def test_clear_game(game_model):
    #Test that clear_game empties both teams.
    game_model.team_1 = [1, 3]
    game_model.team_2 = [2, 4]
    game_model.clear_game()
    assert len(game_model.team_1) == 0
    assert len(game_model.team_2) == 0

def test_clear_game_empty(game_model, caplog):
    #Test that clear_game logs a warning when already empty.
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
    # Test that get_players uses the cache if TTL is valid.
    game_model.team_1.append(sample_player1.id)
    game_model._player_cache[sample_player1.id] = sample_player1
    game_model._ttl[sample_player1.id] = time.time() + 100
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id")
    players = game_model.get_players()
    assert players[0] == sample_player1
    mock_get.assert_not_called()

def test_get_players_refreshes_on_expired_ttl(game_model, sample_player1, mocker):
    # Test that get_players refreshes the cache if TTL is expired.
    game_model.team_2.append(sample_player1.id)
    game_model._player_cache[sample_player1.id] = mocker.Mock()
    game_model._ttl[sample_player1.id] = time.time() - 1
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id", return_value=sample_player1)
    players = game_model.get_players()
    assert players[0] == sample_player1
    mock_get.assert_called_once_with(sample_player1.id)

def test_enter_game(game_model, sample_players):
    #Test that enter_game adds a player to the specified team.
    game_model.enter_game(sample_players[0].id, team=1)
    assert game_model.team_1 == [sample_players[0].id]
    game_model.enter_game(sample_players[1].id, team=2)
    assert game_model.team_2 == [sample_players[1].id]

def test_enter_game_full(game_model, sample_players):
    #Test that enter_game raises an error when team is full.
    game_model.team_1 = [sample_players[0].id, sample_players[1].id]
    with pytest.raises(ValueError, match="Team 1 is already full."):
        game_model.enter_game(5, team=1)

# --- Game Logic ---

def test_get_player_skill(game_model, sample_players):
    #Test that get_player_skill calculates the skill correctly.
    # Skill = (weight in pounds) + (height in inches) * (position factor)

    player = sample_players[0]
    height_inches = player.height_feet * 12 + player.height_inches
    position_factor = {"G": 1.0, "F": 1.2, "C": 1.4}.get(player.position[:1].upper(), 1.0)
    expected_skill = player.weight_pounds + height_inches * position_factor

    assert game_model.get_player_skill(player) == expected_skill


def test_play_game(game_model, sample_players, mocker, caplog):
    # Setup: add 2 players to each team
    game_model.team_1 = [sample_players[0].id, sample_players[1].id]
    game_model.team_2 = [sample_players[2].id, sample_players[3].id]

    # Mock players returned from DB
    mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id", side_effect=sample_players)
    
    # Mock skill calculation
    mocker.patch(
        "basketballers.models.basketball_game_model.GameModel.get_player_skill",
        return_value=300.0
        )    
    # Mock randomness
    mocker.patch("basketballers.models.basketball_game_model.get_random", return_value=0.3)

    # Run the game
    with caplog.at_level("INFO"):
        winner = game_model.play_game()

    assert winner in ["Team 1", "Team 2"]
    assert "Game started between Team 1 and Team 2" in caplog.text
    assert "The winner is:" in caplog.text


def test_play_game_with_empty_teams(game_model):
    #Test that play_game raises an error when teams are empty.
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()
         
def test_play_game_with_one_player_each(game_model):
    #Test that play_game raises an error when teams have only one player each.
    game_model.team_1 = [1]
    game_model.team_2 = [2]
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()

def test_clear_cache(game_model, sample_player1):
    #Test that clear_cache empties the player cache.
    game_model._player_cache[sample_player1.id] = sample_player1
    game_model._ttl[sample_player1.id] = time.time() + 100
    game_model.clear_cache()
    assert game_model._player_cache == {}
    assert game_model._ttl == {}
