from dataclasses import asdict

import pytest
from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    get_leaderboard,
    get_weight_class,
    update_boxer_stats
)
from boxing.models.ring_model import RingModel

#fixtures for the boxer samples
@pytest.fixture
def mock_db_connection(mocker):
    """Mock the database connection for testing."""
    return mocker.patch("boxing.models.boxers_model.get_db_connection")

@pytest.fixture
def sample_boxer1():
    """Fixture providing a sample boxer for testing."""
    return Boxer(1, 'Wesley', 175, 71, 76.0, 32)

@pytest.fixture
def sample_boxer2():
    """Fixture providing another sample boxer for testing."""
    return Boxer(2, 'Michelle', 135, 58, 70.0, 30)


##################################################
# Boxer Management Test Cases
##################################################


def test_create_boxer(mock_db_connection, mocker):
    """_test creating a boxer_

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
    Raises:
        ValueError: If boxer doesn't exist yet
        
    """
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  
    
    # Call the function
    create_boxer("Wesley", 175, 71, 76.0, 32)
    
    # Verify  
    mock_cursor.execute.assert_any_call(
        "SELECT 1 FROM boxers WHERE name = ?", 
        ("Wesley",)
    )
    query_string = """
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """
    mock_cursor.execute.assert_any_call(
        query_string,
        ("Wesley", 175, 71, 76.0, 32)
    )


def test_create_boxer_with_invalid_data():
    """test creating a boxer with invalid data

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
    
    Expected Errors:
        ValueError: Invalid weight: 120. Must be at least 125.
        ValueError: Invalid height: 0. Must be greater than 0.
        ValueError: Invalid age: 15. Must be between 18 and 40.
    """
    # Test invalid weight
    with pytest.raises(ValueError, match="Invalid weight: 120. Must be at least 125."):
        create_boxer("Wesley", 120, 71, 76.0, 32)
    
    # Test invalid height
    with pytest.raises(ValueError, match="Invalid height: 0. Must be greater than 0."):
        create_boxer("Wesley", 175, 0, 76.0, 32)
    
    # Test invalid age
    with pytest.raises(ValueError, match="Invalid age: 15. Must be between 18 and 40."):
        create_boxer("Wesley", 175, 71, 76.0, 15)


def test_delete_boxer(mock_db_connection, mocker):
    """test deleting a boxer

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
        
    """
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists
    
    # Call the function
    delete_boxer(1)
    
    # Verify database operations
    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))


def test_delete_nonexistent_boxer(mock_db_connection, mocker):
    """Test deleting a boxer that doesn't exist."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)






##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxer_by_id(mock_db_connection, mocker):
    """Test retrieving a boxer by ID."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, 'Wesley', 175, 71, 76.0, 32)
    
    # Call the function
    boxer = get_boxer_by_id(1)
    
    # Verify result
    assert boxer.id == 1
    assert boxer.name == 'Wesley'
    assert boxer.weight == 175
    assert boxer.height == 71
    assert boxer.reach == 76.0
    assert boxer.age == 32
    assert boxer.weight_class == 'MIDDLEWEIGHT'

def test_get_boxer_by_name(mock_db_connection, mocker):
    """Test retrieving a boxer by name."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, 'Wesley', 175, 71, 76.0, 32)
    
    # Call the function
    boxer = get_boxer_by_name('Wesley')
    
    # Verify result
    assert boxer.id == 1
    assert boxer.name == 'Wesley'


def test_get_nonexistent_boxer(mock_db_connection, mocker):
    """Test retrieving a boxer that doesn't exist."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Boxer doesn't exist
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        get_boxer_by_id(999)

##################################################
# Leaderboard Test Cases
##################################################


def test_get_leaderboard_by_wins(mock_db_connection, mocker):
    """Test retrieving the leaderboard sorted by wins."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    
    # Sample data for the leaderboard
    mock_cursor.fetchall.return_value = [
        (1, 'Wesley', 175, 71, 76.0, 32, 12, 10, 0.833),
        (2, 'Michelle', 135, 58, 70.0, 30, 6, 5, 0.833)
    ]
    
    # Call the function
    leaderboard = get_leaderboard("wins")
    
    # Verify result
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == 'Wesley'
    assert leaderboard[0]['wins'] == 10
    assert leaderboard[1]['name'] == 'Michelle'
    assert leaderboard[1]['wins'] == 5


def test_get_leaderboard_by_win_pct(mock_db_connection, mocker):
    """Test retrieving the leaderboard sorted by win percentage."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    
    # Sample data for the leaderboard
    mock_cursor.fetchall.return_value = [
        (1, 'Wesley', 175, 71, 76.0, 32, 12, 10, 0.833),
        (2, 'Michelle', 135, 58, 70.0, 30, 6, 5, 0.833)
    ]
    
    # Call the function
    leaderboard = get_leaderboard("win_pct")
    
    # Verify result
    assert len(leaderboard) == 2


def test_get_leaderboard_invalid_sort():
    """Test retrieving the leaderboard with an invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard("invalid")



##################################################
# Weight Class Test Cases
##################################################


def test_get_weight_class():
    """Test determining a boxer's weight class."""
    assert get_weight_class(125) == "FEATHERWEIGHT"
    assert get_weight_class(135) == "LIGHTWEIGHT"
    assert get_weight_class(175) == "MIDDLEWEIGHT"
    assert get_weight_class(203) == "HEAVYWEIGHT"
    
    with pytest.raises(ValueError, match="Invalid weight: 120. Weight must be at least 125."):
        get_weight_class(120)

##################################################
# Stats Update Tests
##################################################

def test_update_boxer_stats(mock_db_connection, mocker):
    """Test updating boxer stats."""
    # Set up mock connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists
    
    # Call the function for a win
    update_boxer_stats(1, 'win')
    
    # Verify database operations for a win
    mock_cursor.execute.assert_any_call(
        "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", 
        (1,)
    )
    
    # Reset the mock
    mock_cursor.reset_mock()
    mock_cursor.fetchone.return_value = (1,)  # Boxer exists
    
    # Call the function for a loss
    update_boxer_stats(1, 'loss')
    
    # Verify database operations for a loss
    mock_cursor.execute.assert_any_call(
        "UPDATE boxers SET fights = fights + 1 WHERE id = ?", 
        (1,)
    )