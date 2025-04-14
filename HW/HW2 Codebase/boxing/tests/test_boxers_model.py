"""
Unit tests for the boxing.models.boxers_model module.

This file tests the following functions and features:
  - create_boxer: Validates boxer creation with valid and invalid inputs.
  - delete_boxer: Ensures deletion works when the boxer exists and fails when not.
  - get_leaderboard: Verifies leaderboard retrieval with both valid and invalid sort parameters.
  - get_boxer_by_id / get_boxer_by_name: Tests retrieval of a boxer by ID and name.
  - get_weight_class: Confirms weight class determination for various weight inputs.
  - update_boxer_stats: Checks that boxer statistics are updated correctly for wins and losses.
External dependencies such as database connections are mocked via a FakeConnection.
"""
import math
import pytest
import sqlite3
from boxing.models.boxers_model import (
    Boxer, create_boxer, delete_boxer, get_leaderboard,
    get_boxer_by_id, get_boxer_by_name, get_weight_class, update_boxer_stats
)

# --- Fake Connection for database operations ---
class FakeConnection:
    def __init__(self):
        self.queries = []
        self.commit_called = False
        self.fetchone_value = None

    def cursor(self):
        return self

    def execute(self, query, params=None):
        self.queries.append((query, params))
        if "SELECT 1 FROM boxers" in query:
            # Simulate that a boxer exists only if the name is "Existing Boxer"
            self.fetchone_value = (1,) if params and params[0] == "Existing Boxer" else None
        elif "SELECT id FROM boxers" in query:
            # For deletion and update tests, assume boxer with id 1 exists.
            self.fetchone_value = (1,) if params and params[0] == 1 else None
        elif "SELECT id, name, weight, height, reach, age" in query:
            if params and params[0] in (1, "Test Boxer"):
                self.fetchone_value = (1, "Test Boxer", 150, 70, 72.0, 25)
            else:
                self.fetchone_value = None
        elif "SELECT id, name, weight, height, reach, age, fights, wins" in query:
            self.fetchone_value = None
        return

    def fetchone(self):
        return self.fetchone_value

    def fetchall(self):
        # Return a fake leaderboard row: (id, name, weight, height, reach, age, fights, wins, win_pct)
        return [(1, "Test Boxer", 150, 70, 72.0, 25, 10, 6, 0.6)]

    def commit(self):
        self.commit_called = True

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Fixture for database functions ---
@pytest.fixture
def fake_db(mocker):
    fake_conn = FakeConnection()
    # Patch get_db_connection in the boxers_model module
    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=fake_conn)
    return fake_conn


def test_create_boxer_success(fake_db) -> None:
    """Test that create_boxer successfully inserts a new boxer record.

    Mocks a database connection and verifies that an INSERT statement is executed
    and the commit is called when valid inputs are provided.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    create_boxer("New Boxer", 130, 68, 70.0, 25)
    assert fake_db.commit_called is True
    assert any("INSERT INTO boxers" in q[0] for q in fake_db.queries)


def test_create_boxer_existing(fake_db) -> None:
    """Test that create_boxer raises a ValueError when the boxer already exists.

    Sets the fake connection to simulate an existing boxer record and expects
    the function to raise an exception.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = (1,)
    with pytest.raises(ValueError, match="already exists"):
        create_boxer("Existing Boxer", 130, 68, 70.0, 25)


def test_create_boxer_invalid_weight() -> None:
    """Test that create_boxer raises a ValueError for an invalid weight input.

    Expects the function to raise a ValueError when the weight is below the minimum threshold.
    """
    with pytest.raises(ValueError, match="Invalid weight"):
        create_boxer("Test Boxer", 120, 68, 70.0, 25)


def test_delete_boxer_success(fake_db) -> None:
    """Test that delete_boxer successfully deletes a boxer record.

    Simulates a database where the boxer exists, then verifies that the DELETE statement
    is executed and commit is called.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = (1,)
    delete_boxer(1)
    assert fake_db.commit_called is True
    assert any("DELETE FROM boxers" in q[0] for q in fake_db.queries)


def test_delete_boxer_not_found(fake_db) -> None:
    """Test that delete_boxer raises a ValueError when the boxer is not found.

    Simulates a database with no matching record and expects a ValueError.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = None
    with pytest.raises(ValueError, match="not found"):
        delete_boxer(2)

def test_get_leaderboard_success(fake_db) -> None:
    """Test that get_leaderboard returns a valid leaderboard list.

    Verifies that the leaderboard is returned as a list with correct boxer details
    when a valid sort parameter is provided.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    leaderboard = get_leaderboard("wins")
    assert isinstance(leaderboard, list)
    assert leaderboard[0]["name"] == "Test Boxer"
    leaderboard_pct = get_leaderboard("win_pct")
    assert leaderboard_pct[0]["win_pct"] == round(0.6 * 100, 1)


def test_get_leaderboard_invalid_sort() -> None:
    """Test that get_leaderboard raises a ValueError for an invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter"):
        get_leaderboard("invalid")


def test_get_boxer_by_id_success(fake_db) -> None:
    """Test that get_boxer_by_id returns a Boxer object for a valid ID.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    boxer = get_boxer_by_id(1)
    assert isinstance(boxer, Boxer)
    assert boxer.name == "Test Boxer"


def test_get_boxer_by_id_not_found(fake_db) -> None:
    """Test that get_boxer_by_id raises a ValueError when no boxer is found for the given ID.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = None
    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_id(2)


def test_get_boxer_by_name_success(fake_db) -> None:
    """Test that get_boxer_by_name returns a Boxer object for a valid name.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = (1, "Test Boxer", 150, 70, 72.0, 25)
    boxer = get_boxer_by_name("Test Boxer")
    assert isinstance(boxer, Boxer)
    assert boxer.id == 1


def test_get_boxer_by_name_not_found(fake_db) -> None:
    """Test that get_boxer_by_name raises a ValueError when the boxer is not found.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = None
    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_name("Unknown Boxer")


def test_get_weight_class_heavy() -> None:
    """Test that get_weight_class returns 'HEAVYWEIGHT' for a weight of 205."""
    assert get_weight_class(205) == "HEAVYWEIGHT"


def test_get_weight_class_middle() -> None:
    """Test that get_weight_class returns 'MIDDLEWEIGHT' for a weight of 170."""
    assert get_weight_class(170) == "MIDDLEWEIGHT"


def test_get_weight_class_light() -> None:
    """Test that get_weight_class returns 'LIGHTWEIGHT' for a weight of 140."""
    assert get_weight_class(140) == "LIGHTWEIGHT"


def test_get_weight_class_feather() -> None:
    """Test that get_weight_class returns 'FEATHERWEIGHT' for a weight of 130."""
    assert get_weight_class(130) == "FEATHERWEIGHT"


def test_get_weight_class_invalid() -> None:
    """Test that get_weight_class raises a ValueError for an invalid weight (below 125)."""
    with pytest.raises(ValueError, match="Invalid weight"):
        get_weight_class(120)

def test_update_boxer_stats_win(fake_db) -> None:
    """Test that update_boxer_stats correctly increments wins and fights for a win.
    
    Args:
        fake_db: Fixture tha provides a fake database connection.
    """
    fake_db.fetchone_value = (1,)
    update_boxer_stats(1, 'win')
    assert any("wins = wins + 1" in q[0] for q in fake_db.queries)

def test_update_boxer_stats_loss(fake_db) -> None:
    """Test that update_boxer_stats correctly increments only fights for a loss.

    Args:
        fake_db: Fixture that provides a fake database connection.
    """
    fake_db.fetchone_value = (1,)
    update_boxer_stats(1, 'loss')
    assert any("fights = fights + 1" in q[0] for q in fake_db.queries)


def test_update_boxer_stats_invalid_result(fake_db) -> None:
    """Test that update_boxer_stats raises a ValueError for an invalid result input."""
    with pytest.raises(ValueError, match="Invalid result"):
        update_boxer_stats(1, 'draw')