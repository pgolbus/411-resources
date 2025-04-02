from contextlib import contextmanager
import re
import sqlite3
import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    get_leaderboard,
    update_boxer_stats
)

######################################################
#
#    Helper: Normalize SQL whitespace
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    """
    Replaces multiple whitespace characters with a single space.
    """
    return re.sub(r'\s+', ' ', sql_query).strip()

######################################################
#
#    Fixture: Mock DB cursor
#
######################################################

@pytest.fixture
def mock_cursor(mocker):
    """
    Creates a mock database connection and cursor.
    """
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Setup default behavior for cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    # Patch the get_db_connection function used in the boxing model
    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

######################################################
#
#    Boxer Creation & Deletion Tests
#
######################################################

def test_create_boxer(mock_cursor):
    """
    Test creating a new boxer.
    """
    create_boxer(name="John Doe", weight=160, height=66, reach=24, age=21)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "SQL query structure does not match expected."

    expected_args = ("John Doe", 160, 66, 24, 21)
    actual_args = mock_cursor.execute.call_args[0][1]
    assert actual_args == expected_args, f"Expected {expected_args}, got {actual_args}."

def test_create_boxer_duplicate(mock_cursor):
    """
    Test that creating a boxer with a duplicate name raises an error.
    """
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")
    with pytest.raises(ValueError, match="Boxer with name 'John Doe' already exists"):
        create_boxer(name="John Doe", weight=160, height=66, reach=24, age=21)

def test_create_boxer_invalid_weight():
    """
    Test error when creating a boxer with an invalid weight.
    """
    with pytest.raises(ValueError, match=r"Invalid weight: -10. Must be at least 125."):
        create_boxer(name="John Doe", weight=-10, height=66, reach=24, age=21)
    with pytest.raises(ValueError, match=r"Invalid weight: 80. Must be at least 125."):
        create_boxer(name="John Doe", weight=80, height=66, reach=24, age=21)

def test_create_boxer_invalid_height():
    """
    Test error when creating a boxer with an invalid height.
    """
    with pytest.raises(ValueError, match=r"Invalid height: -2. Must be greater than 0."):
        create_boxer(name="John Doe", weight=160, height=-2, reach=24, age=21)

def test_create_boxer_invalid_reach():
    """
    Test error when creating a boxer with an invalid reach.
    """
    with pytest.raises(ValueError, match=r"Invalid reach: -2. Must be greater than 0."):
        create_boxer(name="John Doe", weight=160, height=66, reach=-2, age=21)

def test_create_boxer_invalid_age():
    """
    Test error when creating a boxer with an invalid age.
    """
    with pytest.raises(ValueError, match=r"Invalid age: 16. Must be between 18 and 40."):
        create_boxer(name="John Doe", weight=160, height=66, reach=24, age=16)
    with pytest.raises(ValueError, match=r"Invalid age: 50. Must be between 18 and 40."):
        create_boxer(name="John Doe", weight=160, height=66, reach=24, age=50)

def test_delete_boxer(mock_cursor):
    """
    Test deleting an existing boxer.
    """
    # Simulate that the boxer exists
    mock_cursor.fetchone.return_value = True
    delete_boxer(1)

    expected_select = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    actual_select = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_select == expected_select, "SELECT query structure mismatch."
    assert actual_delete == expected_delete, "DELETE query structure mismatch."

    expected_select_args = (1,)
    expected_delete_args = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_select_args == expected_select_args, f"Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"Expected {expected_delete_args}, got {actual_delete_args}."

def test_delete_boxer_bad_id(mock_cursor):
    """
    Test error when deleting a non-existent boxer.
    """
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)

######################################################
#
#    Get Boxer Tests
#
######################################################

def test_get_boxer_by_id(mock_cursor):
    """
    Test retrieving a boxer by ID.
    """
    mock_cursor.fetchone.return_value = (1, "John Doe", 160, 66, 24, 21)
    result = get_boxer_by_id(1)
    expected_boxer = Boxer(1, "John Doe", 160, 66, 24, 21)
    assert result == expected_boxer, f"Expected {expected_boxer}, got {result}."

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "SQL query structure does not match expected."

def test_get_boxer_by_id_bad_id(mock_cursor):
    """
    Test error when retrieving a non-existent boxer by ID.
    """
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

def test_get_boxer_by_name(mock_cursor):
    """
    Test retrieving a boxer by name.
    """
    mock_cursor.fetchone.return_value = (1, "John Doe", 160, 66, 24, 21)
    result = get_boxer_by_name("John Doe")
    expected_boxer = Boxer(1, "John Doe", 160, 66, 24, 21)
    assert result == expected_boxer, f"Expected {expected_boxer}, got {result}."

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "SQL query structure does not match expected."

def test_get_boxer_by_name_bad_name(mock_cursor):
    """
    Test error when retrieving a non-existent boxer by name.
    """
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer 'Jane Doe' not found."):
        get_boxer_by_name("Jane Doe")

######################################################
#
#    Leaderboard & Stats Tests
#
######################################################

def test_get_leaderboard_wins(mock_cursor):
    """
    Test retrieving leaderboard sorted by wins.
    """
    mock_cursor.fetchall.return_value = [
        (2, "Jane Doe", 150, 63, 22, 20, 3, 2, 0.67),
        (1, "John Doe", 160, 66, 24, 21, 1, 1, 1)
    ]
    result = get_leaderboard("wins")
    expected = [
        {"id": 2, "name": "Jane Doe", "weight": 150, "height": 63, "reach": 22, "age": 20, "weight_class": "LIGHTWEIGHT", "fights": 3, "wins": 2, "win_pct": 67},
        {"id": 1, "name": "John Doe", "weight": 160, "height": 66, "reach": 24, "age": 21, "weight_class": "LIGHTWEIGHT", "fights": 1, "wins": 1, "win_pct": 100}
    ]
    assert result == expected, f"Expected {expected}, got {result}."

def test_get_leaderboard_win_pct(mock_cursor):
    """
    Test retrieving leaderboard sorted by win percentage.
    """
    mock_cursor.fetchall.return_value = [
        (1, "John Doe", 160, 66, 24, 21, 1, 1, 1),
        (2, "Jane Doe", 150, 63, 22, 20, 3, 2, 0.67)
    ]
    result = get_leaderboard("win_pct")
    expected = [
        {"id": 1, "name": "John Doe", "weight": 160, "height": 66, "reach": 24, "age": 21, "weight_class": "LIGHTWEIGHT", "fights": 1, "wins": 1, "win_pct": 100},
        {"id": 2, "name": "Jane Doe", "weight": 150, "height": 63, "reach": 22, "age": 20, "weight_class": "LIGHTWEIGHT", "fights": 3, "wins": 2, "win_pct": 67}
    ]
    assert result == expected, f"Expected {expected}, got {result}."

def test_update_boxer_stats_win(mock_cursor):
    """
    Test updating boxer stats for a win.
    """
    mock_cursor.fetchone.return_value = True
    boxer_id = 1
    update_boxer_stats(boxer_id, "win")

    expected_query = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "SQL query structure does not match expected for win update."

    expected_args = (boxer_id,)
    actual_args = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_args == expected_args, f"Expected {expected_args}, got {actual_args}."

def test_update_boxer_stats_loss(mock_cursor):
    """
    Test updating boxer stats for a loss.
    """
    mock_cursor.fetchone.return_value = True
    boxer_id = 1
    update_boxer_stats(boxer_id, "loss")

    expected_query = normalize_whitespace("UPDATE boxers SET fights = fights + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "SQL query structure does not match expected for loss update."

    expected_args = (boxer_id,)
    actual_args = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_args == expected_args, f"Expected {expected_args}, got {actual_args}."