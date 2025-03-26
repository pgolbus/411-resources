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

######################################################
#
#    Fixtures
#
######################################################

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

######################################################
#
#    Add and delete
#
######################################################

# test create boxer
def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog.

    """
    create_boxer(name = "Boxer Name", weight = 190, height = 175, reach = 180.0, age = 23 )
    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 190, 175, 180.0, 23)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

#test create duplicate boxer

#test create boxer invalid weight

#test create boxer invalid age

#test delete boxer

#test delete boxer invalid id 

#test get boxer by id

#test get boxer by id invalid id 

#test get boxer by name
def test_get_boxer_by_name(mock_cursor):
    """Test retrieving a boxer by name."""
    mock_cursor.fetchone.return_value = (1, "John Smith", 165, 72, 72.0, 28)

    result = get_boxer_by_name("John Doe")

    expected = Boxer(id=1, name="John Doe", weight=165, height=72, reach=72.0, age=28)
    assert result == expected, f"Expected {expected}, got {result}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age
        FROM boxers WHERE name = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    actual_args = mock_cursor.execute.call_args[0][1]

    assert actual_query == expected_query
    assert actual_args == ("John Smith",)


#test get boxer by invalid name 
def test_get_boxer_by_invalid_name(mock_cursor):
    """Test retrieving a non-existent boxer by name."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer 'Nonexistent' not found."):
        get_boxer_by_name("Nonexistent")

######################################################
#
#    Leaderboard
#
######################################################

#test get leaderboard
def test_get_leaderboard(mock_cursor):
    """Test getting leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 150, 70, 72.0, 25, 10, 8, 0.8),
        (2, "Boxer B", 170, 72, 75.0, 30, 20, 15, 0.75),
    ]

    leaderboard = get_leaderboard()

    expected = [
        {
            'id': 1, 'name': "Boxer A", 'weight': 150, 'height': 70,
            'reach': 72.0, 'age': 25, 'weight_class': 'LIGHTWEIGHT',
            'fights': 10, 'wins': 8, 'win_pct': 80.0
        },
        {
            'id': 2, 'name': "Boxer B", 'weight': 170, 'height': 72,
            'reach': 75.0, 'age': 30, 'weight_class': 'MIDDLEWEIGHT',
            'fights': 20, 'wins': 15, 'win_pct': 75.0
        }
    ]

    assert leaderboard == expected

#test get leaderboard invalid string
def test_get_leaderboard_invalid_sort(mock_cursor):
    """Test leaderboard sort_by parameter validation."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")

#test get leaderboard no boxers
def test_get_leaderboard_empty(mock_cursor):
    """Test leaderboard when no boxers are present."""
    mock_cursor.fetchall.return_value = []

    result = get_leaderboard()
    assert result == []


######################################################
#
#    Weight Class
#
######################################################

#test get weight class
def test_get_weight_class():
    """Test that get_weight_class correctly categorizes weights into weight classes."""
    assert get_weight_class(210) == "HEAVYWEIGHT"
    assert get_weight_class(180) == "MIDDLEWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    assert get_weight_class(125) == "FEATHERWEIGHT"

#test get weight class invalid weight
def test_get_weight_class_invalid_weight():
    """Test that get_weight_class raises an error for weights below the minimum threshold."""
    with pytest.raises(ValueError, match="Invalid weight: 100. Weight must be at least 125."):
        get_weight_class(100)

######################################################
#
#    Update Stats
#
######################################################

#test update boxer stats on win
def test_update_boxer_stats_win(mock_cursor):
    """Test that updating stats with a win increments both fights and wins by 1."""
    mock_cursor.fetchone.return_value = True
    update_boxer_stats(1, "win")

    update_query = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    actual_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_query == update_query
    assert actual_args == (1,)

#test update boxer stats on loss
def test_update_boxer_stats_loss(mock_cursor):
    """Test that updating stats with a loss increments only the fights by 1."""
    mock_cursor.fetchone.return_value = True
    update_boxer_stats(1, "loss")

    update_query = normalize_whitespace("UPDATE boxers SET fights = fights + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    actual_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_query == update_query
    assert actual_args == (1,)

#test update boxer with invalid result
def test_update_boxer_stats_invalid_result():
    """Test that an invalid fight result raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, "draw")

#test update boxer stats invalid id
def test_update_boxer_stats_invalid_id(mock_cursor):
    """Test that trying to update stats for a non-existent boxer raises a ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        update_boxer_stats(999, "win")
