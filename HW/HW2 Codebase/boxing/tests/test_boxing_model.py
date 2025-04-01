from contextlib import contextmanager
import re
import sqlite3

import pytest


from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)
#from boxing.utils.sql_utils import get_db_connection


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


def test_create_boxer(mock_cursor):
    """Test successful boxer creation"""
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist

    create_boxer("Mike Tyson", 220, 71, 71.5, 30)

    # Update the expected query to match the actual format
    mock_cursor.execute.assert_any_call(
        '\n                INSERT INTO boxers (name, weight, height, reach, age)\n                VALUES (?, ?, ?, ?, ?)\n            ',
        ("Mike Tyson", 220, 71, 71.5, 30)
    )



def test_create_boxer_already_exists(mock_cursor):
    """Test creating a boxer that already exists"""
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists

    with pytest.raises(ValueError, match="Boxer with name 'Mike Tyson' already exists"):
        create_boxer("Mike Tyson", 220, 71, 71.5, 30)


def test_delete_boxer_success(mock_cursor):
    """Test deleting an existing boxer"""
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists

    delete_boxer(1)

    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))


def test_delete_boxer_not_found(mock_cursor):
    """Test deleting a non-existent boxer"""
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist

    with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
        delete_boxer(1)


def test_get_leaderboard_success(mock_cursor):
    """Test getting the leaderboard sorted by wins"""
    mock_cursor.fetchall.return_value = [
        (1, "Ali", 200, 74, 76.0, 30, 50, 45, 0.9),
        (2, "Tyson", 220, 71, 71.5, 32, 58, 50, 0.86)
    ]

    leaderboard = get_leaderboard(sort_by="wins")
    
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == "Ali"
    assert leaderboard[1]['name'] == "Tyson"


def test_get_boxer_by_id_success(mock_cursor):
    """Test retrieving a boxer by ID"""
    mock_cursor.fetchone.return_value = (1, "Ali", 200, 74, 76.0, 30)

    boxer = get_boxer_by_id(1)

    assert boxer.id == 1
    assert boxer.name == "Ali"


def test_get_boxer_by_id_not_found(mock_cursor):
    """Test retrieving a boxer with an invalid ID"""
    mock_cursor.fetchone.return_value = None  # No boxer found

    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        get_boxer_by_id(99)


def test_get_boxer_by_name_success(mock_cursor):
    """Test retrieving a boxer by name"""
    mock_cursor.fetchone.return_value = (2, "Mike Tyson", 220, 71, 71.5, 32)

    boxer = get_boxer_by_name("Mike Tyson")

    assert boxer.id == 2
    assert boxer.name == "Mike Tyson"


def test_get_boxer_by_name_not_found(mock_cursor):
    """Test retrieving a boxer with an invalid name"""
    mock_cursor.fetchone.return_value = None  # No boxer found

    with pytest.raises(ValueError, match="Boxer 'Unknown' not found."):
        get_boxer_by_name("Unknown")


def test_get_weight_class():
    """Test weight class determination"""
    assert get_weight_class(210) == "HEAVYWEIGHT"
    assert get_weight_class(170) == "MIDDLEWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    assert get_weight_class(130) == "FEATHERWEIGHT"


def test_get_weight_class_invalid():
    """Test invalid weight class determination"""
    with pytest.raises(ValueError, match="Invalid weight: 100. Weight must be at least 125."):
        get_weight_class(100)


def test_update_boxer_stats_win(mock_cursor):
    """Test updating boxer stats for a win"""
    mock_cursor.fetchone.return_value = (1,)

    update_boxer_stats(1, "win")

    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))


def test_update_boxer_stats_loss(mock_cursor):
    """Test updating boxer stats for a loss"""
    mock_cursor.fetchone.return_value = (1,)

    update_boxer_stats(1, "loss")

    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))


def test_update_boxer_stats_invalid_result(mock_cursor):
    """Test updating boxer stats with invalid result"""
    mock_cursor.fetchone.return_value = (1,)

    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, "draw")


def test_update_boxer_stats_not_found(mock_cursor):
    """Test updating stats for a non-existent boxer"""
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist

    with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
        update_boxer_stats(1, "win")
