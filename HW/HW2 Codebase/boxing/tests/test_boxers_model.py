from contextlib import contextmanager
import logging
import re
import sqlite3

import pytest

from boxing.models.boxers_model import create_boxer, delete_boxer, get_leaderboard, get_boxer_by_id, get_boxer_by_name, get_weight_class, Boxer, update_boxer_stats


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
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

@pytest.fixture
def sample_boxer_dict():
    return {
        "id": 1,
        "name": "Muhammad Ali",
        "weight": 210,
        "height": 191,
        "reach": 78,
        "age": 32,
        "fights": 10,
        "wins": 7
    }

@pytest.fixture
def sample_boxer2_dict():
    return {
        "id": 2,
        "name": "Mike Tyson",
        "weight": 220,
        "height": 178,
        "reach": 71,
        "age": 35,
        "fights": 8,
        "wins": 5
    }


######################################################
#
#    Add and Delete Boxers
#
######################################################


def test_add_boxer(mock_cursor, sample_boxer_dict):
    """Test adding a boxer to the database.

    """
    create_boxer(
        sample_boxer_dict["name"],
        sample_boxer_dict["weight"],
        sample_boxer_dict["height"],
        sample_boxer_dict["reach"],
        sample_boxer_dict["age"]
    )

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (
        sample_boxer_dict["name"],
        sample_boxer_dict["weight"],
        sample_boxer_dict["height"],
        sample_boxer_dict["reach"],
        sample_boxer_dict["age"]
    )

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_add_boxer_duplicate_name(mock_cursor, sample_boxer_dict):
    """Test adding a boxer with a duplicate name

    """
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")

    with pytest.raises(ValueError, match=f"Boxer with name '{sample_boxer_dict['name']}' already exists"):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )

def test_add_boxer_invalid_weight(sample_boxer_dict):
    """Test error when trying to create a boxer with an invalid weight (below 125).

    """
    sample_boxer_dict["weight"] = 120  # Invalid weight

    with pytest.raises(ValueError, match=f"Invalid weight: {sample_boxer_dict['weight']}. Must be at least 125."):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )


def test_add_boxer_invalid_height(sample_boxer_dict):
    """Test error when trying to create a boxer with an invalid height (zero or negative).

    """
    sample_boxer_dict["height"] = 0  # Invalid height

    with pytest.raises(ValueError, match=f"Invalid height: {sample_boxer_dict['height']}. Must be greater than 0."):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )


def test_add_boxer_invalid_reach(sample_boxer_dict):
    """Test error when trying to create a boxer with an invalid reach (zero or negative).

    """
    sample_boxer_dict["reach"] = -1  # Invalid reach

    with pytest.raises(ValueError, match=f"Invalid reach: {sample_boxer_dict['reach']}. Must be greater than 0."):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )


def test_add_boxer_invalid_age(sample_boxer_dict):
    """Test error when trying to create a boxer with an invalid age (outside 18-40 range).

    """
    # Too young
    sample_boxer_dict["age"] = 17
    with pytest.raises(ValueError, match=f"Invalid age: {sample_boxer_dict['age']}. Must be between 18 and 40."):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )

    # Too old
    sample_boxer_dict["age"] = 41
    with pytest.raises(ValueError, match=f"Invalid age: {sample_boxer_dict['age']}. Must be between 18 and 40."):
        create_boxer(
            sample_boxer_dict["name"],
            sample_boxer_dict["weight"],
            sample_boxer_dict["height"],
            sample_boxer_dict["reach"],
            sample_boxer_dict["age"]
        )


def test_delete_boxer(mock_cursor, sample_boxer_dict):
    """Test deleting a boxer by ID.

    """
    mock_cursor.fetchone.return_value = True  # Before we delete, we need to ensure the boxer exists.
                                              # Any value other than None will suffice

    delete_boxer(sample_boxer_dict["id"])

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The DELETE query did not match the expected structure."

    expected_select_args = (sample_boxer_dict["id"],)
    expected_delete_args = (sample_boxer_dict["id"],)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The DELETE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

def test_delete_boxer_bad_id(mock_cursor):
    """Test deleting a boxer that does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get
#
######################################################


def test_get_boxer_by_id(mock_cursor, sample_boxer_dict):
    """Test retrieving a boxer by ID.

    """
    mock_cursor.fetchone.return_value = tuple(sample_boxer_dict.values())

    # Extract only the fields required for the Boxer dataclass
    expected_data = {key: sample_boxer_dict[key] for key in ["id", "name", "weight", "height", "reach", "age"]}

    result = get_boxer_by_id(1)
    expected_result = Boxer(**expected_data)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test retrieving a boxer by an invalid ID.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

def test_get_boxer_by_name(mock_cursor, sample_boxer_dict):
    """Test retrieving a boxer by name.

    """
    mock_cursor.fetchone.return_value = tuple(sample_boxer_dict.values())

    # Extract only the fields required for the Boxer dataclass
    expected_data = {key: sample_boxer_dict[key] for key in ["id", "name", "weight", "height", "reach", "age"]}

    result = get_boxer_by_name("Muhammad Ali")
    expected_result = Boxer(**expected_data)
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Muhammad Ali",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test retrieving a boxer by a name that does not exist.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer 'Joe Frazier' not found"):
        get_boxer_by_name("Joe Frazier")

def test_get_weight_class():
    """Test weight class assignment for valid weights.

    """
    assert get_weight_class(210) == "HEAVYWEIGHT"
    assert get_weight_class(203) == "HEAVYWEIGHT"
    assert get_weight_class(180) == "MIDDLEWEIGHT"
    assert get_weight_class(166) == "MIDDLEWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    assert get_weight_class(133) == "LIGHTWEIGHT"
    assert get_weight_class(126) == "FEATHERWEIGHT"
    assert get_weight_class(125) == "FEATHERWEIGHT"

def test_get_weight_class_invalid(caplog):
    """Test invalid weight raises ValueError.

    """
    caplog.set_level(logging.ERROR)

    with pytest.raises(ValueError, match="Invalid weight: 124. Weight must be at least 125."):
        get_weight_class(124)

    assert "Invalid weight: 124. Weight must be at least 125." in caplog.text


######################################################
#
#    Update Boxer Stats
#
######################################################


def test_update_boxer_stats_win(mock_cursor):
    """Test updating the boxer stats for a win.

    """
    mock_cursor.fetchone.return_value = True

    update_boxer_stats(1, 'win')

    expected_sql = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")
    actual_sql = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_sql == expected_sql, "The SQL query did not match the expected structure."

    expected_args = (1,)
    actual_args = mock_cursor.execute.call_args[0][1]
    assert actual_args == expected_args, f"The SQL arguments did not match. Expected {expected_args}, got {actual_args}."

def test_update_boxer_stats_loss(mock_cursor):
    """Test updating the boxer stats for a loss.

    """
    mock_cursor.fetchone.return_value = True

    update_boxer_stats(1, 'loss')

    expected_sql = normalize_whitespace("UPDATE boxers SET fights = fights + 1 WHERE id = ?")
    actual_sql = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_sql == expected_sql, "The SQL query did not match the expected structure."

    expected_args = (1,)
    actual_args = mock_cursor.execute.call_args[0][1]
    assert actual_args == expected_args, f"The SQL arguments did not match. Expected {expected_args}, got {actual_args}."

def test_update_boxer_stats_bad_id(mock_cursor):
    """Test updating boxer stats for a boxer that does not exist.

    """
    mock_cursor.fetchone.return_value = None  # Boxer not found

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        update_boxer_stats(999, 'win')


######################################################
#
#    Leaderboard
#
######################################################


def test_get_leaderboard(mock_cursor, sample_boxer_dict, sample_boxer2_dict):
    """Test retrieving the leaderboard sorted by wins.

    """
    mock_cursor.fetchall.return_value = [
        (sample_boxer_dict["id"], sample_boxer_dict["name"], sample_boxer_dict["weight"],
         sample_boxer_dict["height"], sample_boxer_dict["reach"], sample_boxer_dict["age"],
         sample_boxer_dict["fights"], sample_boxer_dict["wins"],
         sample_boxer_dict["wins"] / sample_boxer_dict["fights"]),

        (sample_boxer2_dict["id"], sample_boxer2_dict["name"], sample_boxer2_dict["weight"],
         sample_boxer2_dict["height"], sample_boxer2_dict["reach"], sample_boxer2_dict["age"],
         sample_boxer2_dict["fights"], sample_boxer2_dict["wins"],
         sample_boxer2_dict["wins"] / sample_boxer2_dict["fights"])
    ]

    result = get_leaderboard()
    expected_result = [
        {**sample_boxer_dict, "weight_class": "HEAVYWEIGHT", "win_pct": round(sample_boxer_dict["wins"] / sample_boxer_dict["fights"] * 100, 1)},
        {**sample_boxer2_dict, "weight_class": "HEAVYWEIGHT", "win_pct": round(sample_boxer2_dict["wins"] / sample_boxer2_dict["fights"] * 100, 1)}
    ]

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_sql = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers WHERE fights > 0 ORDER BY wins DESC
    """)
    actual_sql = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_sql == expected_sql, "The SQL query did not match the expected structure."


def test_get_leaderboard_sort_pct(mock_cursor, sample_boxer_dict, sample_boxer2_dict):
    """Test retrieving the leaderboard sorted by win percentage.

    """
    mock_cursor.fetchall.return_value = [
        (sample_boxer_dict["id"], sample_boxer_dict["name"], sample_boxer_dict["weight"],
         sample_boxer_dict["height"], sample_boxer_dict["reach"], sample_boxer_dict["age"],
         sample_boxer_dict["fights"], sample_boxer_dict["wins"],
         sample_boxer_dict["wins"] / sample_boxer_dict["fights"]),

        (sample_boxer2_dict["id"], sample_boxer2_dict["name"], sample_boxer2_dict["weight"],
         sample_boxer2_dict["height"], sample_boxer2_dict["reach"], sample_boxer2_dict["age"],
         sample_boxer2_dict["fights"], sample_boxer2_dict["wins"],
         sample_boxer2_dict["wins"] / sample_boxer2_dict["fights"])
    ]

    result = get_leaderboard(sort_by="win_pct")
    expected_result = [
        {**sample_boxer_dict, "weight_class": "HEAVYWEIGHT", "win_pct": round(sample_boxer_dict["wins"] / sample_boxer_dict["fights"] * 100, 1)},
        {**sample_boxer2_dict, "weight_class": "HEAVYWEIGHT", "win_pct": round(sample_boxer2_dict["wins"] / sample_boxer2_dict["fights"]* 100, 1)}
    ]

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_sql = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers WHERE fights > 0 ORDER BY win_pct DESC
    """)
    actual_sql = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_sql == expected_sql, "The SQL query did not match the expected structure."


def test_get_leaderboard_bad_sort():
    """Test retrieving the leaderboard with an invalid sort option.

    """
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")
