import pytest
import boxing.models.boxers_model as boxer_model
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_connection(mocker):
    # Create mock objects for connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Set up return values for cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Create mock context manager
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_conn
    mock_context.__exit__.return_value = False

    # Patch get_db_connection to return our context manager
    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=mock_context)

    return mock_cursor


def test_create_boxer_success(mock_db_connection):
    """Test creating a valid boxer works without error."""
    boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)

    insert_query = "INSERT INTO boxers (name, weight, height, reach, age)"
    called_sql = mock_db_connection.execute.call_args[0][0]
    assert insert_query in called_sql


def test_create_boxer_duplicate_name(mock_db_connection):
    """Test that creating a boxer with an existing name raises an error."""
    mock_db_connection.fetchone.return_value = True

    with pytest.raises(ValueError, match="already exists"):
        boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)
def test_delete_boxer_success(mock_db_connection):
    """Test that delete_boxer deletes a boxer if ID exists."""
    # Mock boxer exists
    mock_db_connection.fetchone.return_value = (1,)

    boxer_model.delete_boxer(1)

    calls = [call[0][0] for call in mock_db_connection.execute.call_args_list]
    assert "DELETE FROM boxers WHERE id = ?" in calls


def test_delete_boxer_not_found(mock_db_connection):
    """Test that delete_boxer raises error when boxer ID not found."""
    mock_db_connection.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        boxer_model.delete_boxer(999)
def test_update_boxer_stats_win(mock_db_connection):
    """Test updating stats with a win increments fights and wins."""
    mock_db_connection.fetchone.return_value = (1,)

    boxer_model.update_boxer_stats(1, "win")

    executed_queries = [call[0][0] for call in mock_db_connection.execute.call_args_list]
    assert any("UPDATE boxers SET fights = fights + 1, wins = wins + 1" in q for q in executed_queries)


def test_update_boxer_stats_invalid_result(mock_db_connection):
    """Test invalid result string raises ValueError."""
    with pytest.raises(ValueError, match="Invalid result"):
        boxer_model.update_boxer_stats(1, "draw")


def test_update_boxer_stats_boxer_not_found(mock_db_connection):
    """Test when boxer ID doesn't exist."""
    mock_db_connection.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        boxer_model.update_boxer_stats(999, "win")
def test_get_boxer_by_id_success(mock_db_connection):
    """Test retrieving a boxer by valid ID."""
    mock_db_connection.fetchone.return_value = (1, "Ali", 180, 70, 72.5, 28)

    boxer = boxer_model.get_boxer_by_id(1)

    assert boxer.name == "Ali"
    assert boxer.weight == 180
    assert boxer.age == 28


def test_get_boxer_by_id_not_found(mock_db_connection):
    """Test retrieving a boxer with invalid ID raises error."""
    mock_db_connection.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        boxer_model.get_boxer_by_id(999)
