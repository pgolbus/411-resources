import sqlite3
from unittest.mock import patch

import pytest, re

from boxing.models.boxers_model import Boxer, create_boxer, delete_boxer, get_leaderboard, get_boxer_by_id, get_boxer_by_name, get_weight_class, update_boxer_stats

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_get_db_connection():
    """Mocks the get_db_connection function."""
    with patch("boxing.models.boxers_model.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value.cursor.return_value
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Default return for queries
        mock_cursor.fetchall.return_value = []
        mock_cursor.commit.return_value = None
        yield mock_conn, mock_cursor

@pytest.fixture
def sample_boxer1():
    """Fixture providing a sample Boxer instance."""
    return Boxer(id=1, name="Test Boxer 1", weight=160, height=70, reach=72.5, age=25)

@pytest.fixture
def sample_boxer2():
    """Fixture providing another sample Boxer instance."""
    return Boxer(id=2, name="Test Boxer 2", weight=140, height=68, reach=70.0, age=30)

@pytest.fixture
def sample_leaderboard_data():
    """Fixture providing sample leaderboard data."""
    return [
        (1, "Boxer A", 160, 70, 72.5, 25, 5, 4, 0.8),
        (2, "Boxer B", 140, 68, 70.0, 30, 3, 2, 0.6666666666666666),
    ]

##################################################
# Create Boxer Test Cases
##################################################

def test_create_boxer_success(mock_get_db_connection):
    """Tests successful creation of a boxer."""
    mock_conn, mock_cursor = mock_get_db_connection
    create_boxer("New Boxer", 170, 71, 73.0, 28)
    mock_cursor.execute.assert_any_call(
        "SELECT 1 FROM boxers WHERE name = ?", ("New Boxer",)
    )
    mock_cursor.execute.assert_any_call("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """,
            ("New Boxer", 170, 71, 73.0, 28),
    )
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()

def test_create_boxer_invalid_weight(mock_get_db_connection):
    """Tests ValueError for invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight: 120. Must be at least 125."):
        create_boxer("Light Boxer", 120, 65, 68.0, 22)

def test_create_boxer_invalid_height(mock_get_db_connection):
    """Tests ValueError for invalid height."""
    with pytest.raises(ValueError, match="Invalid height: 0. Must be greater than 0."):
        create_boxer("Short Boxer", 150, 0, 70.0, 27)

def test_create_boxer_invalid_reach(mock_get_db_connection):
    """Tests ValueError for invalid reach."""
    with pytest.raises(ValueError, match="Invalid reach: 0. Must be greater than 0."):
        create_boxer("Short Reach Boxer", 165, 72, 0, 29)

def test_create_boxer_invalid_age(mock_get_db_connection):
    """Tests ValueError for invalid age."""
    with pytest.raises(ValueError, match="Invalid age: 17. Must be between 18 and 40."):
        create_boxer("Young Boxer", 145, 69, 71.5, 17)
    with pytest.raises(ValueError, match="Invalid age: 41. Must be between 18 and 40."):
        create_boxer("Old Boxer", 180, 73, 74.0, 41)

def test_create_boxer_duplicate_name(mock_get_db_connection):
    """Tests ValueError when adding a boxer with a duplicate name."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer with the name already exists
    with pytest.raises(ValueError, match="Boxer with name 'Existing Boxer' already exists"):
        create_boxer("Existing Boxer", 160, 70, 72.0, 25)

def test_create_boxer_database_error(mock_get_db_connection):
    """Tests handling of database errors during creation."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error occurred")
    with pytest.raises(sqlite3.Error, match="Database error occurred"):
        create_boxer("Error Boxer", 155, 67, 69.0, 32)

##################################################
# Delete Boxer Test Cases
##################################################

def test_delete_boxer_success(mock_get_db_connection):
    """Tests successful deletion of a boxer."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer with the ID exists
    delete_boxer(1)
    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()

def test_delete_boxer_not_found(mock_get_db_connection):
    """Tests ValueError when trying to delete a non-existent boxer."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = None  # Simulate boxer with the ID not found
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        delete_boxer(99)

def test_delete_boxer_database_error(mock_get_db_connection):
    """Tests handling of database errors during deletion."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error during delete")
    with pytest.raises(sqlite3.Error, match="Database error during delete"):
        delete_boxer(5)

##################################################
# Get Leaderboard Test Cases
##################################################

def test_get_leaderboard_sort_by_wins(mock_get_db_connection, sample_leaderboard_data):
    """Tests getting the leaderboard sorted by wins (default)."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchall.return_value = sample_leaderboard_data
    leaderboard = get_leaderboard()
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == "Boxer A"
    assert leaderboard[1]['name'] == "Boxer B"
    mock_cursor.execute.assert_called_once_with(
        """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
     ORDER BY wins DESC"""
    )

def test_get_leaderboard_sort_by_win_pct(mock_get_db_connection, sample_leaderboard_data):
    """Tests getting the leaderboard sorted by win percentage."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchall.return_value = sample_leaderboard_data
    leaderboard = get_leaderboard(sort_by="win_pct")
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == "Boxer A"
    assert leaderboard[1]['name'] == "Boxer B"
    mock_cursor.execute.assert_called_once_with(
        """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
     ORDER BY win_pct DESC"""
    )

def test_get_leaderboard_invalid_sort_by(mock_get_db_connection):
    """Tests ValueError for invalid sort_by parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")

def test_get_leaderboard_database_error(mock_get_db_connection):
    """Tests handling of database errors during leaderboard retrieval."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error during leaderboard retrieval")
    with pytest.raises(sqlite3.Error, match="Database error during leaderboard retrieval"):
        get_leaderboard()

##################################################
# Get Boxer by ID Test Cases
##################################################

def test_get_boxer_by_id_success(mock_get_db_connection, sample_boxer1):
    """Tests successful retrieval of a boxer by ID."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (
        sample_boxer1.id,
        sample_boxer1.name,
        sample_boxer1.weight,
        sample_boxer1.height,
        sample_boxer1.reach,
        sample_boxer1.age,
    )
    boxer = get_boxer_by_id(1)
    assert boxer.id == sample_boxer1.id
    assert boxer.name == sample_boxer1.name
    mock_cursor.execute.assert_called_once_with(
        """
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (1,)
    )

def test_get_boxer_by_id_not_found(mock_get_db_connection):
    """Tests ValueError when trying to retrieve a non-existent boxer by ID."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        get_boxer_by_id(99)

def test_get_boxer_by_id_database_error(mock_get_db_connection):
    """Tests handling of database errors during boxer retrieval by ID."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error during get by ID")
    with pytest.raises(sqlite3.Error, match="Database error during get by ID"):
        get_boxer_by_id(5)

##################################################
# Get Boxer by Name Test Cases
##################################################

def test_get_boxer_by_name_success(mock_get_db_connection, sample_boxer2):
    """Tests successful retrieval of a boxer by name."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (
        sample_boxer2.id,
        sample_boxer2.name,
        sample_boxer2.weight,
        sample_boxer2.height,
        sample_boxer2.reach,
        sample_boxer2.age,
    )
    boxer = get_boxer_by_name("Test Boxer 2")
    assert boxer.id == sample_boxer2.id
    assert boxer.name == sample_boxer2.name
    mock_cursor.execute.assert_called_once_with(
        """
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, ("Test Boxer 2",)
    )

def test_get_boxer_by_name_not_found(mock_get_db_connection):
    """Tests ValueError when trying to retrieve a non-existent boxer by name."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer 'NonExistent' not found."):
        get_boxer_by_name("NonExistent")

def test_get_boxer_by_name_database_error(mock_get_db_connection):
    """Tests handling of database errors during boxer retrieval by name."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error during get by name")
    with pytest.raises(sqlite3.Error, match="Database error during get by name"):
        get_boxer_by_name("Error Name")

##################################################
# Get Weight Class Test Cases
##################################################

def test_get_weight_class_heavyweight():
    """Tests getting the 'HEAVYWEIGHT' weight class."""
    assert get_weight_class(210) == 'HEAVYWEIGHT'
    assert get_weight_class(203) == 'HEAVYWEIGHT'

def test_get_weight_class_middleweight():
    """Tests getting the 'MIDDLEWEIGHT' weight class."""
    assert get_weight_class(180) == 'MIDDLEWEIGHT'
    assert get_weight_class(166) == 'MIDDLEWEIGHT'

def test_get_weight_class_lightweight():
    """Tests getting the 'LIGHTWEIGHT' weight class."""
    assert get_weight_class(150) == 'LIGHTWEIGHT'
    assert get_weight_class(133) == 'LIGHTWEIGHT'

def test_get_weight_class_featherweight():
    """Tests getting the 'FEATHERWEIGHT' weight class."""
    assert get_weight_class(130) == 'FEATHERWEIGHT'
    assert get_weight_class(125) == 'FEATHERWEIGHT'

def test_get_weight_class_invalid_weight():
    """Tests ValueError for invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight: 124. Weight must be at least 125."):
        get_weight_class(124)

##################################################
# Update Boxer Stats Test Cases
##################################################

def test_update_boxer_stats_win(mock_get_db_connection):
    """Tests updating boxer stats for a win."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer with the ID exists
    update_boxer_stats(1, 'win')
    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call(
        "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,)
    )
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()

def test_update_boxer_stats_loss(mock_get_db_connection):
    """Tests updating boxer stats for a loss."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer with the ID exists
    update_boxer_stats(1, 'loss')
    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call(
        "UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,)
    )
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()

def test_update_boxer_stats_invalid_result(mock_get_db_connection):
    """Tests ValueError for invalid result parameter."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, 'draw')

def test_update_boxer_stats_not_found(mock_get_db_connection):
    """Tests ValueError when trying to update stats for a non-existent boxer."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.fetchone.return_value = None  # Simulate boxer with the ID not found
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        update_boxer_stats(99, 'win')

def test_update_boxer_stats_database_error(mock_get_db_connection):
    """Tests handling of database errors during stats update."""
    mock_conn, mock_cursor = mock_get_db_connection
    mock_cursor.execute.side_effect = sqlite3.Error("Database error during stats update")
    with pytest.raises(sqlite3.Error, match="Database error during stats update"):
        update_boxer_stats(5, 'loss')
