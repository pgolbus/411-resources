from dataclasses import asdict
from contextlib import contextmanager
import sqlite3
import re

import pytest
from pytest_mock import MockerFixture

from boxing.models.boxers_model import (Boxer, create_boxer)
from boxing.models.ring_model import RingModel


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor 

def test_create_boxer(mock_cursor):

    create_boxer(name="Mo",weight=130,height=50,reach=6,age=30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Mo", 130, 50, 6, 30)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_addBoxer_with_Invalid_height():
    assert True

def test_addBoxer_with_Invalid_weight():
    assert True

def test_addBoxer_with_Invalid_reach():
    assert True

def test_addBoxer_with_Invalid_age():
    assert True

def test_add_duplicate_boxer(mock_cursor):
    """Test error when adding a duplicate boxer

    """
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: songs.artist, songs.title, songs.year")
    with pytest.raises(ValueError, match=f"Boxer with name 'So' already exists"):
        create_boxer(name="So",weight=130,height=50,reach=6,age=30)

@pytest.fixture()
def test_delete_boxer():
    assert True

@pytest.fixture()
def test_delete_boxer_DNEinDB():
    assert True

@pytest.fixture()
def test_get_leaderboard():
    assert True

@pytest.fixture()
def test_get_leaderboard_withInvalidSort():
    assert True

@pytest.fixture()
def test_get_boxer_by_id():
    assert True

@pytest.fixture()
def test_get_boxer_by_idDNE():
    assert True

@pytest.fixture()
def test_get_boxer_by_name():
    assert True

@pytest.fixture()
def test_get_boxer_by_nameDNE():
    assert True

@pytest.fixture()
def test_get_weight_class():
    assert True

@pytest.fixture()
def test_get_weight_classInvalid():
    assert True

@pytest.fixture()
def test_update_boxer_stats_test():
    assert True

@pytest.fixture()
def test_update_boxer_stats_butINvalidResult():
    assert True

@pytest.fixture()
def test_update_boxer_stats_butBoxerDNE():
    assert True
