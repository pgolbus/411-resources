#Comment: Copy of song_model
from contextlib import contextmanager
import re
import sqlite3

import pytest

#Change 1: 'music_collection.models.song_model' --> 'meal_max.models.kitchen_model' + all of the methods in the middle
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
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

    #Change 2: 'music_collection...get_db_connection' --> 'meal_max.models.kitchen_model.get_db_connection'
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

#Change 3: unit test for create_meal
def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""

    # Call the function to create a new meal
    create_meal(meal="Meal Name", cuisine="Cuisine Name", price=0.5, difficulty='MED')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Name", 0.5, 'MED')
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.name")
    meal = "Meal Name"
    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match=f"Meal with name '{meal}' already exists"):
        create_meal(meal, cuisine="Cuisine Name", price=0.5, difficulty='MED')

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty"""
    # Attempt to create a meal with difficulty = 'HARD'
    difficulty = 'HARD'
    with pytest.raises(ValueError, match=f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=0.5, difficulty='HARD')

    # Attempt to create a meal with a non-string difficulty
    difficulty=20
    with pytest.raises(ValueError, match=f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=0.5, difficulty=20)

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., less than 0 or non-float/non-int)."""

    # Attempt to create a meal with a price less than 0
    price = -1
    with pytest.raises(ValueError, match=f"Invalid price: {price}. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=-1, difficulty='MED')

    # Attempt to create a meal with a non-float/non-integer price
    price='invalid'
    with pytest.raises(ValueError, match=f"Invalid price: {price}. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price="invalid", difficulty='MED')


def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])
    meal_id=999
    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match=f"Meal with ID {meal_id} has been deleted"):
        delete_meal(999)

######################################################
#
#    Get Meal and Leaderboard
#
######################################################

def test_get_leaderboard(mock_cursor):
    """Test retrieving all meals that are not marked as deleted."""

    # Simulate that there are multiple meals in the database
    #Comment: Do you need to add win_pct in arguments or does it calculate for you?
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 1.0, "LOW", 10, 5, 0.5, False),
        (2, "Meal B", "Cuisine B", 5.0, "MED", 10, 2, 0.2, False),
        (3, "Meal C", "Cuisine C", 10.0, "HIGH", 10, 1, 0.1, False)
    ]

    # Call the get_leaderboard function
    leaderboard = get_leaderboard()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 1.0, "difficulty": "LOW", "battles": 10, "wins": 5, "win_pct": 50},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 5.0, "difficulty": "MED", "battles": 10, "wins": 2, "win_pct": 20},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 10.0, "difficulty": "HIGH", "battles": 10, "wins": 1, "win_pct": 10}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    # Ensure the SQL query was executed correctly
    #Comment: Do you need 'ORDER BY wins DESC' for default case?
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_ordered_by_win_pct(mock_cursor):
    """Test retrieving leaderboard ordered by win."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (2, "Meal B", "Cuisine B", 5.0, "MED", 40, 2, 0.05),
        (1, "Meal A", "Cuisine A", 1.0, "LOW", 10, 1, 0.1),
        (3, "Meal C", "Cuisine C", 10.0, "HIGH", 5, 5, 1.0)
    ]

    # Call the get_leaderboard function with sort_by_play_count = True
    leaderboard = get_leaderboard(sort_by="win_pct")

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 5.0, "difficulty": "MED", "battles": 40, "wins": 2, "win_pct": 5.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 1.0, "difficulty": "LOW", "battles": 10, "wins": 1, "win_pct": 10.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 10.0, "difficulty": "HIGH", "battles": 5, "wins": 5, "win_pct": 100.0}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals 
        WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_ordered_by_invalid(mock_cursor):
    """Test retrieving leaderboard ordered by invalid method (i.e. "Invalid")."""

    sort_by="Invalid"
    with pytest.raises(ValueError, match="Invalid sort_by parameter: %s" % sort_by):
        get_leaderboard(sort_by="Invalid")


def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine Name", 0.5, 'MED', False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Cuisine Name", 0.5, 'MED')

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (name = "Meal Name")
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine Name", 0.5, 'MED', False)

    # Call the function and check the result
    result = get_meal_by_name("Meal Name")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Cuisine Name", 0.5, 'MED')

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given name
    mock_cursor.fetchone.return_value = None
    meal_name="Invalid"
    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match=f"Meal with name {meal_name} not found"):
        get_meal_by_name("Invalid")

def test_update_meal_stats_win(mock_cursor):
    """Test updating the play count of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    update_meal_stats(meal_id, "win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    #Comment: Make sure the argument 'mock_cursor.execute.call_args_list[1][0][0]' is correct --> What does this line do?
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_loss(mock_cursor):
    """Test updating the stats of meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    update_meal_stats(meal_id, "loss")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    #Comment: Make sure the argument 'mock_cursor.execute.call_args_list[1][0][0]' is correct --> What does this line do?
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


### Test for Updating a Deleted Meal:
def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))

### Test for Updating a bad ID Meal:
def test_update_meal_stats_bad_id(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "win")

### Test for Updating a Meal with invalid result:
def test_update_meal_stats_invalid_result(mock_cursor):
    """Test error when trying to update play count for a deleted song."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = [False]
    result = "invalid"

    # Expect a ValueError when attempting to update a meal with invalid result
    with pytest.raises(ValueError, match=f"Invalid result: {result}. Expected 'win' or 'loss'."):
        update_meal_stats(1, "invalid")