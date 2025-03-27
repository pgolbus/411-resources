from dataclasses import asdict

import pytest

from boxing.models.boxers_model import BoxersModel
from boxing.models.boxer import Boxer


@pytest.fixture()
def boxers_model():
    """Fixture to provide a new instance of BoxersModel for each test."""
    return BoxersModel()

@pytest.fixture
def mock_update_stats(mocker):
    """Mock the update_stats function for testing purposes."""
    return mocker.patch("boxing.models.boxers_model.update_stats")

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Wesley', 175, 71, 76.0, 32, 'MIDDLEWEIGHT')

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Michelle', 135, 58, 70.0, 30, 'LIGHTWEIGHT')


##################################################
# Boxer Management Test Cases
##################################################


def test_create_boxer(boxers_model, mocker):
    """Test creating a boxer.
    
    This test verifies that a boxer can be successfully created
    and added to the database.
    """
    # Mock the database insert function
    mock_insert = mocker.patch("boxing.models.boxers_model.insert_boxer")
    mock_insert.return_value = 1  # Return boxer ID 1
    
    boxer_id = boxers_model.create_boxer("Wesley", 175, 71, 76.0, 32)
    
    assert boxer_id == 1
    mock_insert.assert_called_once()
    # Verify the correct parameters were passed to insert_boxer
    args = mock_insert.call_args[0]
    assert args[0] == "Wesley"
    assert args[1] == 175
    assert args[2] == 71
    assert args[3] == 76.0
    assert args[4] == 32


def test_create_boxer_with_invalid_data(boxers_model):
    """Test creating a boxer with invalid data.
    
    This test verifies that attempting to create a boxer with invalid
    data raises the appropriate exceptions.
    """
    # Test negative weight
    with pytest.raises(ValueError, match="Weight must be positive"):
        boxers_model.create_boxer("Wesley", -10, 71, 76.0, 32)
    
    # Test negative height
    with pytest.raises(ValueError, match="Height must be positive"):
        boxers_model.create_boxer("Wesley", 175, -5, 76.0, 32)
    
    # Test negative reach
    with pytest.raises(ValueError, match="Reach must be positive"):
        boxers_model.create_boxer("Wesley", 175, 71, -2.0, 32)
    
    # Test negative age
    with pytest.raises(ValueError, match="Age must be positive"):
        boxers_model.create_boxer("Wesley", 175, 71, 76.0, -1)


def test_delete_boxer(boxers_model, mocker):
    """Test deleting a boxer.
    
    This test verifies that a boxer can be successfully deleted
    from the database.
    """
    # Mock the database delete function
    mock_delete = mocker.patch("boxing.models.boxers_model.delete_boxer_by_id")
    
    # Mock get_boxer_by_id to return a boxer
    mock_get = mocker.patch("boxing.models.boxers_model.get_boxer_by_id")
    mock_get.return_value = {"id": 1, "name": "Wesley"}
    
    boxers_model.delete_boxer(1)
    
    mock_delete.assert_called_once_with(1)


def test_delete_nonexistent_boxer(boxers_model, mocker):
    """Test deleting a boxer that doesn't exist.
    
    This test verifies that attempting to delete a boxer that
    doesn't exist raises the appropriate exception.
    """
    # Mock get_boxer_by_id to return None (boxer not found)
    mock_get = mocker.patch("boxing.models.boxers_model.get_boxer_by_id")
    mock_get.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID 1 not found"):
        boxers_model.delete_boxer(1)


##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxer_by_id(boxers_model, mocker, sample_boxer1):
    """Test retrieving a boxer by ID.
    
    This test verifies that a boxer can be successfully retrieved
    from the database by ID.
    """
    # Mock the database query function
    mock_get = mocker.patch("boxing.models.boxers_model.get_boxer_by_id_from_db")
    mock_get.return_value = asdict(sample_boxer1)
    
    boxer = boxers_model.get_boxer_by_id(1)
    
    assert boxer["id"] == 1
    assert boxer["name"] == "Wesley"
    assert boxer["weight"] == 175
    assert boxer["height"] == 71
    assert boxer["reach"] == 76.0
    assert boxer["age"] == 32
    assert boxer["weight_class"] == "MIDDLEWEIGHT"
    mock_get.assert_called_once_with(1)


def test_get_boxer_by_name(boxers_model, mocker, sample_boxer1):
    """Test retrieving a boxer by name.
    
    This test verifies that a boxer can be successfully retrieved
    from the database by name.
    """
    # Mock the database query function
    mock_get = mocker.patch("boxing.models.boxers_model.get_boxer_by_name_from_db")
    mock_get.return_value = asdict(sample_boxer1)
    
    boxer = boxers_model.get_boxer_by_name("Wesley")
    
    assert boxer["id"] == 1
    assert boxer["name"] == "Wesley"
    mock_get.assert_called_once_with("Wesley")


def test_get_nonexistent_boxer(boxers_model, mocker):
    """Test retrieving a boxer that doesn't exist.
    
    This test verifies that attempting to retrieve a boxer that
    doesn't exist returns None.
    """
    # Mock the database query function to return None
    mock_get = mocker.patch("boxing.models.boxers_model.get_boxer_by_id_from_db")
    mock_get.return_value = None
    
    boxer = boxers_model.get_boxer_by_id(999)
    
    assert boxer is None
    mock_get.assert_called_once_with(999)


##################################################
# Leaderboard Test Cases
##################################################


def test_get_leaderboard_by_wins(boxers_model, mocker):
    """Test retrieving the leaderboard sorted by wins.
    
    This test verifies that the leaderboard can be successfully
    retrieved and sorted by the number of wins.
    """
    # Sample leaderboard data
    leaderboard_data = [
        {"name": "Wesley", "wins": 10, "losses": 2, "win_pct": 0.83},
        {"name": "Michelle", "wins": 5, "losses": 1, "win_pct": 0.83}
    ]
    
    # Mock the database query function
    mock_get = mocker.patch("boxing.models.boxers_model.get_leaderboard_from_db")
    mock_get.return_value = leaderboard_data
    
    leaderboard = boxers_model.get_leaderboard("wins")
    
    assert len(leaderboard) == 2
    assert leaderboard[0]["name"] == "Wesley"
    assert leaderboard[0]["wins"] == 10
    assert leaderboard[1]["name"] == "Michelle"
    mock_get.assert_called_once_with("wins")


def test_get_leaderboard_by_win_pct(boxers_model, mocker):
    """Test retrieving the leaderboard sorted by win percentage.
    
    This test verifies that the leaderboard can be successfully
    retrieved and sorted by win percentage.
    """
    # Sample leaderboard data - Michelle first since equal win_pct but fewer fights
    leaderboard_data = [
        {"name": "Michelle", "wins": 5, "losses": 1, "win_pct": 0.83},
        {"name": "Wesley", "wins": 10, "losses": 2, "win_pct": 0.83}
    ]
    
    # Mock the database query function
    mock_get = mocker.patch("boxing.models.boxers_model.get_leaderboard_from_db")
    mock_get.return_value = leaderboard_data
    
    leaderboard = boxers_model.get_leaderboard("win_pct")
    
    assert len(leaderboard) == 2
    assert leaderboard[0]["name"] == "Wesley"
    assert leaderboard[0]["win_pct"] == 0.83
    assert leaderboard[1]["name"] == "Michelle"
    mock_get.assert_called_once_with("win_pct")


def test_get_leaderboard_invalid_sort(boxers_model):
    """Test retrieving the leaderboard with an invalid sort parameter.
    
    This test verifies that attempting to retrieve the leaderboard with
    an invalid sort parameter raises the appropriate exception.
    """
    with pytest.raises(ValueError, match="Invalid sort parameter"):
        boxers_model.get_leaderboard("invalid_sort")


##################################################
# Weight Class Test Cases
##################################################


def test_determine_weight_class():
    """Test determining a boxer's weight class.
    
    This test verifies that a boxer's weight class is correctly
    determined based on their weight.
    """
    from boxing.models.boxers_model import determine_weight_class
    
    assert determine_weight_class(135) == "LIGHTWEIGHT"
    assert determine_weight_class(160) == "MIDDLEWEIGHT"
    assert determine_weight_class(175) == "LIGHT_HEAVYWEIGHT"
    assert determine_weight_class(200) == "HEAVYWEIGHT"
    assert determine_weight_class(112) == "FLYWEIGHT"
    assert determine_weight_class(118) == "BANTAMWEIGHT"
    assert determine_weight_class(126) == "FEATHERWEIGHT"
    assert determine_weight_class(147) == "WELTERWEIGHT"


def test_validate_boxer_data():
    """Test validation of boxer data.
    
    This test verifies that boxer data is properly validated
    before being inserted into the database.
    """
    from boxing.models.boxers_model import validate_boxer_data
    
    # Valid data
    try:
        validate_boxer_data("Wesley", 175, 71, 76.0, 32)
    except ValueError:
        pytest.fail("validate_boxer_data raised ValueError unexpectedly for valid data")
    
    # Invalid data
    with pytest.raises(ValueError, match="Boxer name cannot be empty"):
        validate_boxer_data("", 175, 71, 76.0, 32)
    
    with pytest.raises(ValueError, match="Weight must be positive"):
        validate_boxer_data("Wesley", 0, 71, 76.0, 32)
    
    with pytest.raises(ValueError, match="Height must be positive"):
        validate_boxer_data("Wesley", 175, 0, 76.0, 32)
    
    with pytest.raises(ValueError, match="Reach must be positive"):
        validate_boxer_data("Wesley", 175, 71, 0, 32)
    
    with pytest.raises(ValueError, match="Age must be positive"):
        validate_boxer_data("Wesley", 175, 71, 76.0, 0)
