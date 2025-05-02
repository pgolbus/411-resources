import time
import pytest
from basketballers.models.basketball_player_model import BasketballPlayer
from basketballers.models.basketball_game_model import GameModel


@pytest.fixture
def game_model():
    """Fixture to provide a new instance of GameModel for each test."""
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


def test_clear_game(game_model):
    """Test that clear_game empties the game.

    """
    game_model.team_1 = [1, 2]
    game_model.team_2 = [3, 4]
    game_model.clear_game()
    assert game_model.team_1 == []
    assert game_model.team_2 == []

def test_clear_game_empty(game_model, caplog):
    """Test that calling clear_game on an empty game logs a warning and keeps the game empty.

    """
    with caplog.at_level("WARNING"):
        game_model.clear_game()
    assert game_model.team_1 == []
    assert game_model.team_2 == []
    assert "Attempted to clear an empty game" in caplog.text
    

def test_get_players_empty(game_model, caplog):
    """Test that get_players returns an empty list when there are no players and logs a warning.

    """
    with caplog.at_level("WARNING"):
        players = game_model.get_players()
    assert players == []
    assert "Retrieving players from an empty game." in caplog.text

def test_get_players_with_data(game_model, sample_players):
    """Test that get_players returns the correct list when there are players.



    """
    game_model.team_1 = [sample_players[0].id]
    game_model.team_2 = [sample_players[1].id]
    game_model._player_cache[sample_players[0].id] = sample_players[0]
    game_model._player_cache[sample_players[1].id] = sample_players[1]
    game_model._ttl[sample_players[0].id] = time.time() + 100
    game_model._ttl[sample_players[1].id] = time.time() + 100

    players = game_model.get_players()
    assert sample_players[0] in players
    assert sample_players[1] in players

def test_get_players_uses_cache(game_model, sample_players, mocker):
    """Test that get_players uses the cache if the TTL is not expired.

    """
    p = sample_players[0]
    game_model.team_1 = [p.id]
    game_model._player_cache[p.id] = p
    game_model._ttl[p.id] = time.time() + 100
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id")
    players = game_model.get_players()
    assert players[0] == p
    mock_get.assert_not_called()
    
def test_get_players_refreshes_on_expired_ttl(game_model, sample_players, mocker):
    """Test that get_players refreshes the cache if the TTL is expired.

    """
    p = sample_players[0]
    game_model.team_1 = [p.id]
    game_model._player_cache[p.id] = mocker.Mock()
    game_model._ttl[p.id] = time.time() - 1
    mock_get = mocker.patch("basketballers.models.basketball_player_model.BasketballPlayer.get_player_by_id", return_value=p)
    players = game_model.get_players()
    assert players[0] == p
    mock_get.assert_called_once_with(p.id)

def test_clear_cache(game_model, sample_players):
    """Test that clear_cache empties the player cache and TTL.

    """
    p = sample_players[0]
    game_model._player_cache[p.id] = p
    game_model._ttl[p.id] = time.time() + 100
    game_model.clear_cache()
    assert game_model._player_cache == {}
    assert game_model._ttl == {}

def test_enter_game(game_model, sample_players):
    """Test that a player is correctly added to the game.

    """
    game_model.enter_game(sample_players[0].id, team=1)
    game_model.enter_game(sample_players[1].id, team=1)
    game_model.enter_game(sample_players[2].id, team=2)
    game_model.enter_game(sample_players[3].id, team=2)
    assert len(game_model.team_1) == 2
    assert len(game_model.team_2) == 2

def test_enter_game_full(game_model, sample_players):
    """Test that enter_game raises an error when the game is full.

    """
    game_model.team_1 = [sample_players[0].id, sample_players[1].id]
    with pytest.raises(ValueError, match="Team 1 is already full."):
        game_model.enter_game(sample_players[2].id, team=1)

##########################################################
# Game Logic
##########################################################

def test_get_player_skill(game_model, sample_players):
    """Test the get_player_skill method.

    """
    p = sample_players[0]
    total_height = p.height_feet * 12 + p.height_inches
    factor = {"G": 1.0, "F": 1.2, "C": 1.4}.get(p.position[:1].upper(), 1.0)
    expected_skill = p.weight_pounds + total_height * factor
    assert game_model.get_player_skill(p) == expected_skill

def test_get_team_skill(game_model, sample_players):
    """Test that get_team_skill sums individual player skills correctly."""
    team_ids = [sample_players[0].id, sample_players[1].id]
    game_model._player_cache = {
        sample_players[0].id: sample_players[0],
        sample_players[1].id: sample_players[1],
    }
    game_model._ttl = {
        sample_players[0].id: time.time() + 100,
        sample_players[1].id: time.time() + 100,
    }
    expected = sum(game_model.get_player_skill(p) for p in [sample_players[0], sample_players[1]])
    assert game_model.get_team_skill(team_ids) == expected

def test_play_game(game_model, sample_players, mocker, caplog):
    """Test the play game method with sample players.

    """
    game_model.team_1 = [sample_players[0].id, sample_players[1].id]
    game_model.team_2 = [sample_players[2].id, sample_players[3].id]

    for p in sample_players:
        game_model._player_cache[p.id] = p
        game_model._ttl[p.id] = time.time() + 100

    mocker.patch("basketballers.models.basketball_game_model.get_random", return_value=0.3)

    with caplog.at_level("INFO"):
        winner = game_model.play_game()

    assert winner in ["Team 1", "Team 2"]
    assert "Game started between Team 1 and Team 2" in caplog.text
    assert "The winner is:" in caplog.text

def test_update_team_stats(game_model, caplog):
    with caplog.at_level("INFO"):
        game_model.update_team_stats("Team 1")
        game_model.update_team_stats("Team 2")
    assert "Team 1 wins!" in caplog.text
    assert "Team 2 wins!" in caplog.text

def test_play_game_with_empty_teams(game_model):
    """Test that the play game method raises a ValueError when there are fewer than two players on each team.

    """
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()

def test_play_game_with_one_player_each(game_model, sample_players):
    """Test that the play game method raises a ValueError when there's only one player on each team.

    """
    game_model.team_1 = [sample_players[0].id]
    game_model.team_2 = [sample_players[1].id]
    with pytest.raises(ValueError, match="Each team must have 2 players to start a game."):
        game_model.play_game()

