from dataclasses import asdict


#using indivudual testing instead of class based testing
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


#needed for the tests
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

#fixtuere for the ring
@pytest.fixture
def ring():
    """Fixture providing RingModel for each test."""
    return RingModel()


def test_create_boxer_with_duplicate_name(mock_db_connection, mocker):
    """_test creating a boxer with a duplicate name_

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
        
    """
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor

    
    # First attempt - boxer doesn't exist
    mock_cursor.fetchone.return_value = None
    create_boxer("Wesley", 175, 71, 76.0, 32)
    
    # Second attempt - boxer now exists
    mock_cursor.fetchone.return_value = (1,)
    
    with pytest.raises(ValueError, match="Boxer with name 'Wesley' already exists"):
        create_boxer("Wesley", 180, 72, 77.0, 33)


def test_update_boxer_stats_invalid_result():
    """_test updating boxer stats with an invalid resul like tie_

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
        
    """
    with pytest.raises(ValueError, match="Invalid result: tie. Expected 'win' or 'loss'."):
        update_boxer_stats(1, "tie")

def test_get_boxer_by_name_not_found(mock_db_connection, mocker):
    """_test getting a boxer by name that doesn't exist_

    Args:
        mock_db_connection (_type_): mock the database connection for testing
        mocker (_type_): mock the database connection for testing
        
    """
    mock_cursor = mocker.MagicMock()
    mock_conn = mock_db_connection.return_value.__enter__.return_value
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = None

      
    with pytest.raises(ValueError, match="Boxer 'lskdfjlsdkf' not found."):
        get_boxer_by_name("lskdfjlsdkf")


def test_enter_ring_invalid_type(ring):
    """Test adding a non-Boxer object to the ring."""
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
        ring.enter_ring("Not a boxer")

