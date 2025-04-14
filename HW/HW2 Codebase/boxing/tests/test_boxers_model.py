import sqlite3
import pytest
from dataclasses import asdict
from boxing.utils.sql_utils import get_db_connection

# Import the functions and the Boxer dataclass from your module
from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats,
)

#############################################
# Fixtures for Fake DB Connection and Cursor
#############################################

@pytest.fixture
def fake_db(mocker):
    """
    Create a fake database connection with a fake cursor.
    This fixture patches get_db_connection and returns both the fake connection and cursor.
    """
    fake_conn = mocker.MagicMock()
    fake_cursor = mocker.MagicMock()
    # Simulate context manager behavior:
    fake_conn.__enter__.return_value = fake_conn
    fake_conn.cursor.return_value = fake_cursor

    patcher = mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=fake_conn)
    return {"conn": fake_conn, "cursor": fake_cursor, "patcher": patcher}


#############################################
# Tests for Boxer Dataclass and get_weight_class
#############################################

def test_boxer_post_init_assigns_weight_class():
    """Test that a Boxer instance automatically computes its weight class."""
    boxer = Boxer(id=1, name="Test Boxer", weight=140, height=70, reach=72.5, age=25)
    # For weight 140, the expected weight class is LIGHTWEIGHT (since 140 >= 133 and < 166)
    assert boxer.weight_class == "LIGHTWEIGHT"

@pytest.mark.parametrize("weight,expected", [
    (125, "FEATHERWEIGHT"),
    (133, "LIGHTWEIGHT"),
    (166, "MIDDLEWEIGHT"),
    (203, "HEAVYWEIGHT"),
    (250, "HEAVYWEIGHT"),
])
def test_get_weight_class_valid(weight, expected):
    """Test get_weight_class returns the proper weight class for valid weights."""
    result = get_weight_class(weight)
    assert result == expected

def test_get_weight_class_invalid():
    """Test that get_weight_class raises a ValueError for an invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight: 120"):
        get_weight_class(120)


#############################################
# Tests for create_boxer
#############################################

def test_create_boxer_success(fake_db):
    """Test successfully creating a boxer."""
    # Fake that no boxer exists by having SELECT return None.
    fake_db["cursor"].fetchone.return_value = None
    print("here")

    create_boxer("Mike Tyson", 220, 70, 75.0, 30)

    # Ensure that a check for duplicate was executed.
    fake_db["cursor"].execute.assert_any_call("SELECT 1 FROM boxers WHERE name = ?", ("Mike Tyson",))
    # Ensure that the INSERT statement was executed with the right parameters.
    fake_db["cursor"].execute.assert_any_call(
        """
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """,
        ("Mike Tyson", 220, 70, 75.0, 30)
    )
    # Ensure commit was called.
    fake_db["conn"].commit.assert_called_once()

@pytest.mark.parametrize("name,weight,height,reach,age,err_msg", [
    ("Boxer", 120, 70, 75.0, 25, "Invalid weight: 120"),
    ("Boxer", 130, 0, 75.0, 25, "Invalid height: 0"),
    ("Boxer", 130, 70, 0, 25, "Invalid reach: 0"),
    ("Boxer", 130, 70, 75.0, 17, "Invalid age: 17"),
    ("Boxer", 130, 70, 75.0, 41, "Invalid age: 41"),
])
def test_create_boxer_invalid_parameters(name, weight, height, reach, age, err_msg):
    """Test create_boxer raises ValueError on invalid parameters."""
    with pytest.raises(ValueError, match=err_msg):
        create_boxer(name, weight, height, reach, age)

def test_create_boxer_duplicate_name(fake_db):
    """Test create_boxer raises an error when a boxer with the same name already exists."""
    # Simulate that the SELECT returns a row (i.e. duplicate exists)
    fake_db["cursor"].fetchone.return_value = (1,)
    with pytest.raises(ValueError, match="Boxer with name 'Muhammad Ali' already exists"):
        create_boxer("Muhammad Ali", 180, 72, 74.0, 30)

def test_create_boxer_integrity_error(fake_db):
    """Test that an sqlite3.IntegrityError is caught and re-raised as ValueError for duplicates."""
    # Make fetchone return None so that the INSERT is attempted.
    fake_db["cursor"].fetchone.return_value = None
    # Simulate an IntegrityError on INSERT.
    fake_db["cursor"].execute.side_effect = [None, sqlite3.IntegrityError]
    with pytest.raises(ValueError, match="Boxer with name 'Floyd Mayweather' already exists"):
        create_boxer("Floyd Mayweather", 150, 68, 70.0, 28)

def test_create_boxer_sqlite_error(fake_db):
    """Test that a generic sqlite3.Error is propagated."""
    fake_db["cursor"].fetchone.return_value = None
    fake_db["cursor"].execute.side_effect = sqlite3.Error("DB failure")
    with pytest.raises(sqlite3.Error, match="DB failure"):
        create_boxer("Sugar Ray Leonard", 160, 72, 73.0, 30)


#############################################
# Tests for delete_boxer
#############################################

def test_delete_boxer_success(fake_db):
    """Test successfully deleting a boxer."""
    # Simulate that a boxer with given id exists.
    fake_db["cursor"].fetchone.return_value = (1,)
    delete_boxer(1)
    fake_db["cursor"].execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    fake_db["cursor"].execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))
    fake_db["conn"].commit.assert_called_once()

def test_delete_boxer_not_found(fake_db):
    """Test delete_boxer raises ValueError if the boxer does not exist."""
    # Simulate that the boxer is not found.
    fake_db["cursor"].fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)

def test_delete_boxer_sqlite_error(fake_db):
    """Test that an sqlite3.Error during deletion is propagated."""
    fake_db["cursor"].fetchone.return_value = (1,)
    fake_db["cursor"].execute.side_effect = sqlite3.Error("Delete failure")
    with pytest.raises(sqlite3.Error, match="Delete failure"):
        delete_boxer(1)


#############################################
# Tests for get_leaderboard
#############################################

def test_get_leaderboard_sort_by_wins(fake_db):
    """Test retrieving leaderboard sorted by wins."""
    # Prepare fake rows: id, name, weight, height, reach, age, fights, wins, win_pct calculation
    fake_db["cursor"].fetchall.return_value = [
        (1, "Boxer A", 150, 70, 70.0, 25, 10, 8, 0.8),
        (2, "Boxer B", 180, 72, 74.0, 28, 20, 15, 0.75),
    ]
    leaderboard = get_leaderboard(sort_by="wins")
    # Check that win_pct is converted to percentage correctly
    assert leaderboard[0]["win_pct"] == 80.0
    assert leaderboard[1]["win_pct"] == 75.0
    # Check that weight_class is computed
    assert leaderboard[0]["weight_class"] == get_weight_class(150)
    fake_db["cursor"].execute.assert_called_once()
    # The ORDER BY clause should be "ORDER BY wins DESC" for sort_by wins.

def test_get_leaderboard_sort_by_win_pct(fake_db):
    """Test retrieving leaderboard sorted by win percentage."""
    fake_db["cursor"].fetchall.return_value = [
        (3, "Boxer C", 170, 71, 72.0, 26, 15, 12, 0.8),
        (4, "Boxer D", 160, 68, 69.0, 24, 10, 8, 0.8),
    ]
    leaderboard = get_leaderboard(sort_by="win_pct")
    # Both have 80.0% win percentage after rounding.
    for boxer in leaderboard:
        assert boxer["win_pct"] == 80.0
    fake_db["cursor"].execute.assert_called_once()

def test_get_leaderboard_invalid_sort(fake_db):
    """Test get_leaderboard raises ValueError when sort_by parameter is invalid."""
    with pytest.raises(ValueError, match="Invalid sort parameter: invalid"):
        get_leaderboard(sort_by="invalid")

def test_get_leaderboard_sqlite_error(fake_db):
    """Test that an sqlite3.Error during leaderboard retrieval is propagated."""
    fake_db["cursor"].execute.side_effect = sqlite3.Error("Query failure")
    with pytest.raises(sqlite3.Error, match="Query failure"):
        get_leaderboard()


#############################################
# Tests for get_boxer_by_id and get_boxer_by_name
#############################################

def test_get_boxer_by_id_success(fake_db):
    """Test that get_boxer_by_id returns a valid Boxer object."""
    # Fake a returned row from the database
    fake_db["cursor"].fetchone.return_value = (5, "Lennox Lewis", 240, 80, 82.0, 32)
    boxer = get_boxer_by_id(5)
    assert isinstance(boxer, Boxer)
    assert boxer.id == 5
    assert boxer.name == "Lennox Lewis"
    assert boxer.weight == 240
    # Weight class should be computed by get_weight_class (for 240, expected HEAVYWEIGHT)
    assert boxer.weight_class == "HEAVYWEIGHT"

def test_get_boxer_by_id_not_found(fake_db):
    """Test get_boxer_by_id raises ValueError if the boxer does not exist."""
    fake_db["cursor"].fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with id 42 not found."):
        get_boxer_by_id(42)

def test_get_boxer_by_name_success(fake_db):
    """Test that get_boxer_by_name returns a valid Boxer object."""
    fake_db["cursor"].fetchone.return_value = (7, "Evander Holyfield", 210, 75, 77.0, 34)
    boxer = get_boxer_by_name("Evander Holyfield")
    assert isinstance(boxer, Boxer)
    assert boxer.id == 7
    assert boxer.name == "Evander Holyfield"
    assert boxer.weight == 210
    assert boxer.weight_class == get_weight_class(210)

def test_get_boxer_by_name_not_found(fake_db):
    """Test that get_boxer_by_name raises an error when the boxer does not exist."""
    fake_db["cursor"].fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer 'Nonexistent Boxer' not found."):
        get_boxer_by_name("Nonexistent Boxer")

def test_get_boxer_by_id_sqlite_error(fake_db):
    """Test that an sqlite3.Error during get_boxer_by_id is propagated."""
    fake_db["cursor"].execute.side_effect = sqlite3.Error("Select failure")
    with pytest.raises(sqlite3.Error, match="Select failure"):
        get_boxer_by_id(1)


#############################################
# Tests for update_boxer_stats
#############################################

@pytest.mark.parametrize("result,expected_update", [
    ("win", "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?"),
    ("loss", "UPDATE boxers SET fights = fights + 1 WHERE id = ?")
])
def test_update_boxer_stats_success(fake_db, result, expected_update):
    """Test successfully updating boxer stats for both win and loss."""
    # Simulate that the boxer exists.
    fake_db["cursor"].fetchone.return_value = (10,)
    update_boxer_stats(10, result)
    # Verify that the boxer existence was checked.
    fake_db["cursor"].execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (10,))
    # Verify that the correct UPDATE query was executed.
    fake_db["cursor"].execute.assert_any_call(expected_update, (10,))
    fake_db["conn"].commit.assert_called_once()

def test_update_boxer_stats_invalid_result():
    """Test that update_boxer_stats raises ValueError when given an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: draw"):
        update_boxer_stats(5, "draw")

def test_update_boxer_stats_boxer_not_found(fake_db):
    """Test that update_boxer_stats raises ValueError when the boxer is not found."""
    fake_db["cursor"].fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        update_boxer_stats(99, "win")

def test_update_boxer_stats_sqlite_error(fake_db):
    """Test that an sqlite3.Error during update_boxer_stats is propagated."""
    fake_db["cursor"].fetchone.return_value = (1,)
    fake_db["cursor"].execute.side_effect = sqlite3.Error("Update failure")
    with pytest.raises(sqlite3.Error, match="Update failure"):
        update_boxer_stats(1, "loss")
