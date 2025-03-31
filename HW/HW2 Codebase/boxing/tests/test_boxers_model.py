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

