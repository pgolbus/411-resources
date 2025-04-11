import sqlite3
import pytest
from contextlib import contextmanager
from boxing.models import boxers_model
from boxing.models.boxers_model import Boxer


@pytest.fixture
def mock_cursor(mocker):
    """Fixture to mock database cursor for testing.

    Args:
        mocker: Pytest mocker fixture for creating mock objects.

    Returns:
        Mock: A mock database cursor object.
    """
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)
    return mock_cursor


import textwrap
def test_create_boxer_success(mock_cursor):
    """Test successful creation of a boxer in the database."""
    mock_cursor.fetchone.return_value = None

    boxers_model.create_boxer("Ali", 150, 70, 72.5, 25)

    # Check if any call matches our expected args and contains the right SQL
    found = False
    for call_args in mock_cursor.execute.call_args_list:
        sql, args = call_args[0]
        if "INSERT INTO boxers" in sql and args == ("Ali", 150, 70, 72.5, 25):
            found = True
            break
    assert found, "Expected INSERT INTO boxers call with correct arguments"

def test_create_boxer_duplicate(mock_cursor):
    """Test creation of a duplicate boxer raises ValueError."""
    mock_cursor.fetchone.return_value = True

    with pytest.raises(ValueError, match="Boxer with name 'Ali' already exists"):
        boxers_model.create_boxer("Ali", 150, 70, 72.5, 25)

def test_create_boxer_invalid_data():
    """Test creation of boxer with invalid data raises ValueError."""
    with pytest.raises(ValueError):
        boxers_model.create_boxer("Ali", 120, 70, 72.5, 25)
    with pytest.raises(ValueError):
        boxers_model.create_boxer("Ali", 150, 0, 72.5, 25)
    with pytest.raises(ValueError):
        boxers_model.create_boxer("Ali", 150, 70, 0, 25)
    with pytest.raises(ValueError):
        boxers_model.create_boxer("Ali", 150, 70, 72.5, 10)


def test_delete_boxer_success(mock_cursor):
    """Test successful deletion of a boxer from the database."""
    mock_cursor.fetchone.return_value = (1,)
    boxers_model.delete_boxer(1)

    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))

def test_delete_boxer_not_found(mock_cursor):
    """Test deletion of non-existent boxer raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 99 not found"):
        boxers_model.delete_boxer(99)


def test_get_leaderboard_success(mock_cursor):
    """Test successful retrieval of boxer leaderboard."""
    mock_cursor.fetchall.return_value = [
        (1, "Ali", 150, 70, 72.5, 25, 10, 8, 0.8)
    ]
    result = boxers_model.get_leaderboard(sort_by="wins")

    assert result[0]['name'] == "Ali"
    assert result[0]['win_pct'] == 80.0


def test_get_leaderboard_invalid_sort():
    """Test leaderboard retrieval with invalid sort parameter raises ValueError."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter"):
        boxers_model.get_leaderboard(sort_by="losses")


def test_get_boxer_by_id_success(mock_cursor):
    """Test successful retrieval of boxer by ID."""
    mock_cursor.fetchone.return_value = (1, "Ali", 150, 70, 72.5, 25)
    boxer = boxers_model.get_boxer_by_id(1)

    assert boxer.name == "Ali"
    assert boxer.weight_class == "LIGHTWEIGHT"


def test_get_boxer_by_id_not_found(mock_cursor):
    """Test retrieval of non-existent boxer by ID raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 99 not found"):
        boxers_model.get_boxer_by_id(99)


def test_get_boxer_by_name_success(mock_cursor):
    """Test successful retrieval of boxer by name."""
    mock_cursor.fetchone.return_value = (1, "Ali", 150, 70, 72.5, 25)
    boxer = boxers_model.get_boxer_by_name("Ali")

    assert boxer.name == "Ali"


def test_get_boxer_by_name_not_found(mock_cursor):
    """Test retrieval of non-existent boxer by name raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer 'Rocky' not found"):
        boxers_model.get_boxer_by_name("Rocky")


def test_get_weight_class():
    """Test weight class determination based on weight."""
    assert boxers_model.get_weight_class(125) == "FEATHERWEIGHT"
    assert boxers_model.get_weight_class(140) == "LIGHTWEIGHT"
    assert boxers_model.get_weight_class(170) == "MIDDLEWEIGHT"
    assert boxers_model.get_weight_class(210) == "HEAVYWEIGHT"

    with pytest.raises(ValueError, match="Invalid weight: 100"):
        boxers_model.get_weight_class(100)


def test_update_boxer_stats_win(mock_cursor):
    """Test successful update of boxer stats for a win."""
    mock_cursor.fetchone.return_value = (1,)
    boxers_model.update_boxer_stats(1, "win")
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))

def test_update_boxer_stats_loss(mock_cursor):
    """Test successful update of boxer stats for a loss."""
    mock_cursor.fetchone.return_value = (1,)
    boxers_model.update_boxer_stats(1, "loss")
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))

def test_update_boxer_stats_invalid_result():
    """Test update of boxer stats with invalid result raises ValueError."""
    with pytest.raises(ValueError, match="Invalid result: draw"):
        boxers_model.update_boxer_stats(1, "draw")


def test_update_boxer_stats_boxer_not_found(mock_cursor):
    """Test update of stats for non-existent boxer raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 1 not found"):
        boxers_model.update_boxer_stats(1, "win")