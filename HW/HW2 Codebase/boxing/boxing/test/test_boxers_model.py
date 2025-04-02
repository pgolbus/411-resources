import pytest
import sqlite3
from boxing.models.boxers_model import (
    create_boxer, delete_boxer, get_boxer_by_id,
    get_boxer_by_name, update_boxer_stats, get_weight_class, get_leaderboard
)

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda s: mock_conn
    mock_conn.__exit__ = mocker.Mock()
    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=mock_conn)
    return mock_cursor

def test_create_boxer_success(mock_cursor):
    mock_cursor.fetchone.return_value = None  # Simulate no existing boxer
    create_boxer("Ali", 180, 185, 78.5, 28)
    insert_args = ("Ali", 180, 185, 78.5, 28)
    mock_cursor.execute.assert_any_call(
        "INSERT INTO boxers (name, weight, height, reach, age) VALUES (?, ?, ?, ?, ?)",
        insert_args
    )

def test_create_boxer_duplicate(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)  # Simulate duplicate boxer
    with pytest.raises(ValueError, match="Boxer with name 'Ali' already exists"):
        create_boxer("Ali", 180, 185, 78.5, 28)

def test_create_boxer_invalid_input():
    with pytest.raises(ValueError):
        create_boxer("Ali", 100, 185, 78.5, 28)
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 0, 78.5, 28)
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 185, 0, 28)
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 185, 78.5, 10)

def test_delete_boxer_success(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer exists
    delete_boxer(1)
    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))

def test_delete_boxer_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None  # Simulate not found
    with pytest.raises(ValueError, match="Boxer with ID 99 not found."):
        delete_boxer(99)

def test_update_boxer_stats_win(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, 'win')
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))

def test_update_boxer_stats_loss(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, 'loss')
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))

def test_update_boxer_stats_invalid_result():
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, 'draw')

def test_get_boxer_by_id_success(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ali", 180, 185, 78.5, 28)
    boxer = get_boxer_by_id(1)
    assert boxer.name == "Ali"

def test_get_boxer_by_name_success(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ali", 180, 185, 78.5, 28)
    boxer = get_boxer_by_name("Ali")
    assert boxer.id == 1

def test_get_weight_class():
    assert get_weight_class(125) == "FEATHERWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    assert get_weight_class(170) == "MIDDLEWEIGHT"
    assert get_weight_class(210) == "HEAVYWEIGHT"
    with pytest.raises(ValueError):
        get_weight_class(100)
