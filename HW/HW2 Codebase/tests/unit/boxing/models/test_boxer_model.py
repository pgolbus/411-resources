import pytest
import sqlite3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../../../../'))

from boxing.boxing.models.boxer_model import create_boxerimport pytest
import sqlite3
from boxing.boxing.models.boxer_model import create_boxer

def test_create_boxer_success(mocker):
    """Test successful boxer creation."""
    # Mock the database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # No boxer with this name exists
    
    # Mock the database connection function
    mocker.patch('boxing.boxing.models.boxer_model.get_db_connection', 
                return_value=mock_conn)
    
    # Call the function - using valid values for all parameters
    create_boxer("Mike Tyson", 220, 71, 71.0, 25)
    
    # Assert that the function tried to insert the boxer
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()

def test_create_boxer_invalid_weight(mocker):
    """Test creating a boxer with invalid weight."""
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 120, 71, 71.0, 25)
    
    assert "Invalid weight: 120. Must be at least 125." in str(excinfo.value)

def test_create_boxer_invalid_height(mocker):
    """Test creating a boxer with invalid height."""
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 0, 71.0, 25)
    
    assert "Invalid height: 0. Must be greater than 0." in str(excinfo.value)

def test_create_boxer_invalid_reach(mocker):
    """Test creating a boxer with invalid reach."""
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 0.0, 25)
    
    assert "Invalid reach: 0.0. Must be greater than 0." in str(excinfo.value)

def test_create_boxer_invalid_age_too_young(mocker):
    """Test creating a boxer with age too young."""
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 71.0, 17)
    
    assert "Invalid age: 17. Must be between 18 and 40." in str(excinfo.value)

def test_create_boxer_invalid_age_too_old(mocker):
    """Test creating a boxer with age too old."""
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 71.0, 41)
    
    assert "Invalid age: 41. Must be between 18 and 40." in str(excinfo.value)

def test_create_boxer_existing_name(mocker):
    """Test creating a boxer with a name that already exists."""
    # Mock the database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)  # Boxer with this name exists
    
    # Mock the database connection function
    mocker.patch('boxing.boxing.models.boxer_model.get_db_connection', 
                return_value=mock_conn)
    
    # Call the function and expect it to raise ValueError
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 71.0, 25)
    
    assert "Boxer with name 'Mike Tyson' already exists" in str(excinfo.value)

def test_create_boxer_database_error(mocker):
    """Test database error handling when creating a boxer."""
    # Mock the database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    
    # Mock the database connection function
    mocker.patch('boxing.boxing.models.boxer_model.get_db_connection', 
                return_value=mock_conn)
    
    # Call the function and expect it to raise the database error
    with pytest.raises(sqlite3.Error) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 71.0, 25)
    
    assert "Database error" in str(excinfo.value)

def test_create_boxer_integrity_error(mocker):
    """Test database integrity error handling."""
    # Mock the database connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("Integrity error")
    
    # Mock the database connection function
    mocker.patch('boxing.boxing.models.boxer_model.get_db_connection', 
                return_value=mock_conn)
    
    # Call the function and expect it to raise ValueError
    with pytest.raises(ValueError) as excinfo:
        create_boxer("Mike Tyson", 220, 71, 71.0, 25)
    
    assert "Boxer with name 'Mike Tyson' already exists" in str(excinfo.value)
