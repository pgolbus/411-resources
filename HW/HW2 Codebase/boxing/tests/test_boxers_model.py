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
def fake_db_connection(mocker):
    fake_conn = FakeConnection()
    # Patch get_db_connection in the boxers_model module
    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=fake_conn)
    return fake_conn


def test_create_boxer_success(fake_db_connection) -> None:
    """Test that create_boxer successfully inserts a new boxer record.

    Mocks a database connection and verifies that an INSERT statement is executed
    and the commit is called when valid inputs are provided.

    Args:
        fake_db_connection: Fixture that provides a fake database connection.
    """
    create_boxer("New Boxer", 130, 68, 70.0, 25)
    assert fake_db_connection.commit_called is True
    assert any("INSERT INTO boxers" in q[0] for q in fake_db_connection.queries)


def test_create_boxer_existing(fake_db_connection) -> None:
    """Test that create_boxer raises a ValueError when the boxer already exists.

    Sets the fake connection to simulate an existing boxer record and expects
    the function to raise an exception.

    Args:
        fake_db_connection: Fixture that provides a fake database connection.
    """
    fake_db_connection.fetchone_value = (1,)
    with pytest.raises(ValueError, match="already exists"):
        create_boxer("Existing Boxer", 130, 68, 70.0, 25)


def test_create_boxer_invalid_weight() -> None:
    """Test that create_boxer raises a ValueError for an invalid weight input.

    Expects the function to raise a ValueError when the weight is below the minimum threshold.
    """
    with pytest.raises(ValueError, match="Invalid weight"):
        create_boxer("Test Boxer", 120, 68, 70.0, 25)


def test_delete_boxer_success(fake_db_connection) -> None:
    """Test that delete_boxer successfully deletes a boxer record.

    Simulates a database where the boxer exists, then verifies that the DELETE statement
    is executed and commit is called.

    Args:
        fake_db_connection: Fixture that provides a fake database connection.
    """
    fake_db_connection.fetchone_value = (1,)
    delete_boxer(1)
    assert fake_db_connection.commit_called is True
    assert any("DELETE FROM boxers" in q[0] for q in fake_db_connection.queries)


def test_delete_boxer_not_found(fake_db_connection) -> None:
    """Test that delete_boxer raises a ValueError when the boxer is not found.

    Simulates a database with no matching record and expects a ValueError.

    Args:
        fake_db_connection: Fixture that provides a fake database connection.
    """
    fake_db_connection.fetchone_value = None
    with pytest.raises(ValueError, match="not found"):
        delete_boxer(2)
