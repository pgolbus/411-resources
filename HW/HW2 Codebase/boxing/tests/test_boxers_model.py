import pytest
import sqlite3
import re

from contextlib import contextmanager
from unittest.mock import patch
from boxing.models.boxers_model import (
    create_boxer, delete_boxer, get_leaderboard,
    get_boxer_by_id, get_boxer_by_name, get_weight_class, update_boxer_stats
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)
    return mock_cursor

def test_create_boxer_success(mock_cursor):
    """Test successfully creating a new boxer in the database."""

    create_boxer("Mike Tyson", 220, 71, 71.0, 30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Mike Tyson", 220, 71, 71.0, 30)
    assert actual_arguments == expected_arguments, (
        f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    )

def test_create_boxer_invalid_weight():
    """Test that creating a boxer with an invalid weight raises an error."""
    with pytest.raises(ValueError, match="Invalid weight: 100. Must be at least 125."):
        create_boxer("Tiny Boxer", 100, 65, 60.0, 25)

def test_create_boxer_existing(mock_cursor):
    """Test that attempting to create an existing boxer raises an error."""
    mock_cursor.fetchone.return_value = (1,)
    with pytest.raises(ValueError, match="Boxer with name 'Mike Tyson' already exists"):
        create_boxer("Mike Tyson", 220, 71, 71.0, 30)

def test_delete_boxer_success(mock_cursor):
    """Test successfully deleting an existing boxer."""
    mock_cursor.fetchone.return_value = (1,)
    delete_boxer(1)
    mock_cursor.execute.assert_called_with("DELETE FROM boxers WHERE id = ?", (1,))

def test_delete_boxer_not_found(mock_cursor):
    """Test that attempting to delete a non-existent boxer raises an error."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)

def test_get_leaderboard_success(mock_cursor):
    """Test retrieving the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [(1, "Mike Tyson", 220, 71, 71.0, 30, 50, 45, 0.9)]
    result = get_leaderboard("wins")
    assert result[0]['name'] == "Mike Tyson"
    assert result[0]['win_pct'] == 90.0

def test_get_boxer_by_id_success(mock_cursor):
    """Test retrieving a boxer by ID successfully."""
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 30)
    boxer = get_boxer_by_id(1)
    assert boxer.name == "Mike Tyson"

def test_get_boxer_by_id_not_found(mock_cursor):
    """Test that retrieving a non-existent boxer by ID raises an error."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        get_boxer_by_id(99)

def test_get_boxer_by_name_success(mock_cursor):
    """Test retrieving a boxer by name successfully."""
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 30)
    boxer = get_boxer_by_name("Mike Tyson")
    assert boxer.name == "Mike Tyson"

def test_get_weight_class():
    """Test determining a boxer's weight class."""
    assert get_weight_class(220) == "HEAVYWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    with pytest.raises(ValueError, match="Invalid weight: 100. Weight must be at least 125."):
        get_weight_class(100)

def test_update_boxer_stats_win(mock_cursor):
    """Test updating a boxer's statistics after a win."""
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, "win")
    mock_cursor.execute.assert_called_with(
        "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,)
    )
