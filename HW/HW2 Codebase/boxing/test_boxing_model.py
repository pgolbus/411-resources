from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxer_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    get_all_boxers,
    get_random_boxer,
    update_win_count
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

    mocker.patch("boxing.models.boxer_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog."""
    create_boxer(name="Boxer Name", age=30, weight_class="Heavyweight", nationality="American", win_count=10)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, age, weight_class, nationality, win_count)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 30, "Heavyweight", "American", 10)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"


def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error)."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name' already exists."):
        create_boxer(name="Boxer Name", age=30, weight_class="Heavyweight", nationality="American", win_count=10)


def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the catalog by boxer ID."""
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The DELETE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The DELETE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent boxer."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get Boxer
#
######################################################


def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id."""
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 30, "Heavyweight", "American", 10)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Boxer Name", 30, "Heavyweight", "American", 10)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, age, weight_class, nationality, win_count FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)


def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name."""
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 30, "Heavyweight", "American", 10)

    result = get_boxer_by_name("Boxer Name")

    expected_result = Boxer(1, "Boxer Name", 30, "Heavyweight", "American", 10)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, age, weight_class, nationality, win_count FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name",)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"


def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent boxer by name."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name' not found"):
        get_boxer_by_name("Boxer Name")


def test_get_all_boxers(mock_cursor):
    """Test retrieving all boxers."""
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 28, "Lightweight", "American", 20),
        (2, "Boxer B", 32, "Middleweight", "British", 25),
        (3, "Boxer C", 26, "Heavyweight", "Canadian", 15)
    ]

    boxers = get_all_boxers()

    expected_result = [
        {"id": 1, "name": "Boxer A", "age": 28, "weight_class": "Lightweight", "nationality": "American", "win_count": 20},
        {"id": 2, "name": "Boxer B", "age": 32, "weight_class": "Middleweight", "nationality": "British", "win_count": 25},
        {"id": 3, "name": "Boxer C", "age": 26, "weight_class": "Heavyweight", "nationality": "Canadian", "win_count": 15}
    ]

    assert boxers == expected_result, f"Expected {expected_result}, but got {boxers}"

    expected_query = normalize_whitespace("""
        SELECT id, name, age, weight_class, nationality, win_count
        FROM boxers
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_random_boxer(mock_cursor, mocker):
    """Test retrieving a random boxer from the catalog."""
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 28, "Lightweight", "American", 20),
        (2, "Boxer B", 32, "Middleweight", "British", 25),
        (3, "Boxer C", 26, "Heavyweight", "Canadian", 15)
    ]

    mock_random = mocker.patch("boxing.models.boxer_model.get_random", return_value=2)

    result = get_random_boxer()

    expected_result = Boxer(2, "Boxer B", 32, "Middleweight", "British", 25)
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    mock_random.assert_called_once_with(3)

    expected_query = normalize_whitespace("SELECT id, name, age, weight_class, nationality, win_count FROM boxers")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_update_win_count(mock_cursor):
   

