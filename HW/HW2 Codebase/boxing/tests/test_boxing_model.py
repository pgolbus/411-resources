import pytest
from unittest import mock
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


# Fixtures for the boxer samples
@pytest.fixture
def mock_db_connection(mocker):
    """Mock the database connection for testing."""
    return mocker.patch("boxing.models.boxers_model.get_db_connection")


@pytest.fixture
def sample_boxer1():
    """Fixture providing a boxer instance for each test."""
    return Boxer(1, 'David', 130, 55, 50, 35)


@pytest.fixture
def sample_boxer2():
    """Fixture providing a boxer instance for each test."""
    return Boxer(2, 'Goliath', 400, 100, 99, 35)

##################################################
# Boxer Management Test Cases
##################################################

def test_create_boxer(mock_db_connection, mocker):
    # Test successful boxer creation
    # Boxer format: Name, weight, height, reach, age
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = []
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    create_boxer('Mike', 150, 75, 80, 30)
    
    mock_cursor.execute.assert_called_with(
        "INSERT INTO boxers (name, weight, height, reach, age) VALUES (?, ?, ?, ?, ?)",
        ('Mike', 150, 75, 80, 30)
    )


def test_create_boxer_with_invalid_age(mock_db_connection):
    # Test creating a boxer with an invalid age
    with pytest.raises(ValueError, match="Invalid age: 50. Must be between 18 and 40."):
        create_boxer('The Elderly', 150, 75, 80, 50)


def test_create_boxer_with_existing_name(mock_db_connection, mocker):
    # Test creating a boxer with an existing name
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [1]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    with pytest.raises(ValueError, match="Boxer with name 'Mike' already exists"):
        create_boxer('Mike', 150, 75, 80, 30)


def test_delete_boxer(mock_db_connection, mocker, sample_boxer1):
    # Test deleting an existing boxer
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [sample_boxer1.id]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    delete_boxer(sample_boxer1.id)
    
    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (sample_boxer1.id,))


def test_delete_nonexistent_boxer(mock_db_connection, mocker):
    # Test deleting a non-existent boxer
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    with pytest.raises(ValueError, match="Boxer with ID 666 not found."):
        delete_boxer(666)


def test_get_boxer_by_id(mock_db_connection, mocker, sample_boxer1):
    # Test retrieving a boxer by ID
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [sample_boxer1.id, sample_boxer1.name, sample_boxer1.weight,
                                         sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    boxer = get_boxer_by_id(sample_boxer1.id)
    
    assert boxer.id == sample_boxer1.id
    assert boxer.name == sample_boxer1.name


def test_get_boxer_by_nonexistent_id(mock_db_connection, mocker):
    # Test retrieving a boxer by a non-existent ID
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    with pytest.raises(ValueError, match="Boxer with ID 666 not found."):
        get_boxer_by_id(666)


def test_get_boxer_by_name(mock_db_connection, mocker, sample_boxer1):
    # Test retrieving a boxer by name
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [sample_boxer1.id, sample_boxer1.name, sample_boxer1.weight,
                                         sample_boxer1.height, sample_boxer1.reach, sample_boxer1.age]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    boxer = get_boxer_by_name(sample_boxer1.name)
    
    assert boxer.name == sample_boxer1.name
    assert boxer.id == sample_boxer1.id


def test_get_boxer_by_nonexistent_name(mock_db_connection, mocker):
    # Test retrieving a boxer by a non-existent name
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    with pytest.raises(ValueError, match="Boxer 'Unknown' not found."):
        get_boxer_by_name('Unknown')


def test_get_leaderboard(mock_db_connection, mocker):
    # Test retrieving the leaderboard
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        (1, 'David', 130, 55, 50, 35, 10, 8, 0.8),
        (2, 'Goliath', 400, 100, 99, 35, 20, 18, 0.9)
    ]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    leaderboard = get_leaderboard("wins")
    
    assert len(leaderboard) == 2
    assert leaderboard[0]['name'] == 'Goliath'
    assert leaderboard[1]['win_pct'] == 80.0


def test_get_weight_class():
    # Test weight class assignment
    assert get_weight_class(250) == 'HEAVYWEIGHT'
    assert get_weight_class(150) == 'MIDDLEWEIGHT'
    assert get_weight_class(130) == 'LIGHTWEIGHT'
    assert get_weight_class(125) == 'FEATHERWEIGHT'
    
    # Test invalid weight
    with pytest.raises(ValueError, match="Invalid weight: 100. Weight must be at least 125."):
        get_weight_class(100)


def test_update_boxer_stats(mock_db_connection, mocker, sample_boxer1):
    # Test updating boxer's stats
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = [sample_boxer1.id]
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    
    update_boxer_stats(sample_boxer1.id, 'win')
    
    mock_cursor.execute.assert_any_call(
        "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (sample_boxer1.id,)
    )


def test_update_boxer_stats_invalid_result(mock_db_connection, mocker, sample_boxer1):
    # Test updating boxer's stats with invalid result
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(sample_boxer1.id, 'draw')
