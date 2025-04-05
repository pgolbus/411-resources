from contextlib import contextmanager
import re
import sqlite3

import pytest
from pytest_mock import mocker

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

##################################################
#   Pytest fixtures                              #
##################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mock db connection for tests.
@pytest.fixture
def mock_db_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor.
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries.
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils.
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test.

##################################################
#   Create boxer test cases                      #
##################################################

def test_create_boxer_with_valid_inputs(mock_db_cursor):
    """Test to successfully create and store a new boxer with all valid inputs.

    """
    create_boxer(name='Mark', weight=127, height=62, reach=63, age=22)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_db_cursor.execute.call_args[0][0])

    assert expected_query == actual_query, "The SQL query did not match the expected query"

    # Check the actual arguments of the SQL query.
    actual_arguments = mock_db_cursor.execute.call_args[0][1]
    expected_arguments = ("Mark", 127, 62, 63, 22)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_fail_create_boxer_with_invalid_weight():
    """Test to check failure if invalid inputs are provided to create boxer.

    """
    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match=f"Invalid weight: 118. Must be at least 125."):
        create_boxer("Bobby", 118, 52, 52, 25)

def test_fail_create_boxer_with_invalid_height():
    """Test to check failure if invalid inputs are provided to create boxer.

    """
    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match=f"Invalid height: -45. Must be greater than 0."):
        create_boxer("George", 145, -45, 52, 29)

def test_fail_create_duplicate_boxer(mock_db_cursor):
    """Test to check failure if boxer cannot be created because name already exists.
    
    """
    mock_db_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name,")

    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match="Boxer with name 'Duke' already exists."):
        create_boxer(name="Duke", weight=198, height= 74, reach=73.5, age= 33)

##################################################
#   Delete boxer test cases                      #
##################################################

def test_delete_boxer_with_valid_id(mock_db_cursor):
    """Test to successfully delete boxer using their valid boxer_id.

    """

    # Simulate the existence of a song with ID = 123456
    # We can use any value other than None

    mock_db_cursor.fetchone.return_value = True
    
    delete_boxer(123456)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_db_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_db_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."
    
    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (123456,)
    expected_delete_args = (123456,)


    actual_select_args = mock_db_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_db_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

def test_fail_boxer_does_not_exists(mock_db_cursor):
    """Test to check failure if there's no boxer with provided boxer_id.
    
    """
    # Simulate that no boxer exists with the given ID
    mock_db_cursor.fetchone.return_value = None
    
    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match="Boxer with ID 456 not found."):
        delete_boxer(456)
    
##################################################
#   Get leaderboard test cases                   #
##################################################

def test_get_leaderboard_by_default(mock_db_cursor):
    """Test to successfully get leaderboard of boxers sorted by default ('wins').
    
    """
    mock_db_cursor.fetchall.return_value = [
        (1234, 'Marco', 180, 72, 71.8, 28, 12, 7, 0.583),
        (5678, 'Duke', 184, 71, 72.2, 31, 10, 6, 0.6)
    ]

    leaderboard = get_leaderboard("wins")

    # Check contents of leaderboard.
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == 'Marco'
    assert leaderboard[0]['wins'] == 7
    assert leaderboard[1]['name'] == 'Duke'
    assert leaderboard[1]['wins'] == 6

def test_get_leaderboard_by_win_pct(mock_db_cursor):
    """Test to successfully get leaderboard of boxers sorted by win percentage.
    
    """
    mock_db_cursor.fetchall.return_value = [
        (1234, 'Marco', 180, 72, 71.8, 28, 12, 7, 0.583),
        (5678, 'Duke', 184, 71, 72.2, 31, 10, 6, 0.6)
    ]

    leaderboard = get_leaderboard("win_pct")

    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == 'Marco'
    assert leaderboard[0]['win_pct'] == 58.3
    assert leaderboard[1]['name'] == 'Duke'
    assert leaderboard[1]['win_pct'] == 60.

def test_fail_invalid_sort_by_parameter():
    """Test to check failure when sort_by parameter is invalid.
    
    """
    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match="Invalid sort_by parameter: fights."):
        get_leaderboard("fights")

##################################################
#   Get boxer by ID test cases                 #
##################################################

def test_get_boxer_using_id(mock_db_cursor):
    """Test to get boxer using valid ID.

    """
    mock_db_cursor.fetchone.return_value = (5678, 'Duke', 184, 71, 72.2, 31)

    actual_result = get_boxer_by_id(5678)
    expected_result = Boxer(id=5678, name='Duke', weight=184, height=71, reach=72.2, age=31)

    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_db_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    actual_arguments = mock_db_cursor.execute.call_args[0][1]
    expected_arguments = (5678, )
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_fail_get_boxer_using_invalid_id(mock_db_cursor):
    """Test to check failure if boxer id is not associated with a boxer.

    """
    mock_db_cursor.fetchone.result = None

    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match=f"Boxer with ID 7777 not found."):
        get_boxer_by_id(7777)
    
##################################################
#   Get boxer by name test cases                 #
##################################################

def test_get_boxer_using_name(mock_db_cursor):
    """Test to get boxer using valid name.

    """
    mock_db_cursor.fetchall.return_value = [
        (1234, "Marco", 180, 72, 71.8, 28, 12, 7, 0.583),
        (5678, "Duke", 184, 71, 72.2, 31, 10, 6, 0.6)
    ]

def test_fail_get_boxer_using_invalid_name(mock_db_cursor):
    """Test to check failure is boxer with given name does not exist.

    """
    mock_db_cursor.fetchone.result = None
    
    boxer_name = 'Jarvis'

    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match=f"Boxer '{boxer_name}' not found."):
        get_boxer_by_name(boxer_name)

##################################################
#   Get weight class by weight test cases        #
##################################################

def test_get_weight_class_by_weight(mock_db_cursor):
    """Test to get correct weight class given weight.
    
    """
    expected_result = 'MIDDLEWEIGHT'
    actual_result = get_weight_class(187)

    # Check to see if ValueError and message is raised.
    assert expected_result == actual_result, f"Expected {expected_result}, got {actual_result}."

def test_fail_invalid_weight():
    """"Test to check failure if invalid weight is provided.

    """
    weight = 100
    
    # Check to see if ValueError and message is raised.
    with pytest.raises(ValueError, match=f"Invalid weight: {weight}. Weight must be at least 125."):
        get_weight_class(weight)

##################################################
#   Update boxer stats test cases                #
##################################################

def test_update_boxer_stat_after_win(mock_db_cursor):
    """Test to update a boxer's stats after winning a fight.

    """
    mock_db_cursor.fetchone.return_value = True

    boxer_id = 789
    fight_result = 'win'

    update_boxer_stats(boxer_id, fight_result)

    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_db_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    actual_arguments = mock_db_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_fail_invalid_fight_result():
    """Test to check failure if invalid result is provided to update a boxer's stats.

    """
    boxer_id = 234
    fight_result = "tie"
    with pytest.raises(ValueError, match=f"Invalid result: {fight_result}. Expected 'win' or 'loss'."):
        update_boxer_stats(boxer_id, fight_result)

def test_fail_invalid_boxer_id(mock_db_cursor):
    """Test to check failure if boxer id is not associated with a boxer.
    
    """

    mock_db_cursor.fetchone.result = None

    boxer_id = 333
    fight_result = "win"

    with pytest.raises(ValueError, match=f"Boxer with ID {boxer_id} not found."):
        update_boxer_stats(boxer_id,fight_result)