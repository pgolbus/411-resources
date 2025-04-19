from contextlib import contextmanager
import re
import sqlite3

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

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

def test_create_boxer_success(mock_cursor):
    create_boxer("Ali", 150, 70, 75.5, 30)

    expected_insert = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_insert = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_insert == expected_insert
    assert mock_cursor.execute.call_args_list[1][0][1] == ("Ali", 150, 70, 75.5, 30)

def test_create_boxer_duplicate(mock_cursor):
    mock_cursor.fetchone.return_value = True

    with pytest.raises(ValueError, match="already exists"):
        create_boxer("Ali", 150, 70, 75.5, 30)

def test_create_boxer_invalid_weight():
    with pytest.raises(ValueError, match="Invalid weight: 100"):
        create_boxer("Ali", 100, 70, 75.5, 30)
        

def test_delete_boxer_success(mock_cursor):
    mock_cursor.fetchone.return_value = True
    delete_boxer(1)

    expected_select = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    actual_select = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select == expected_select
    assert actual_delete == expected_delete

def test_delete_boxer_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        delete_boxer(999)
        
        
def test_get_boxer_by_id_success(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ali", 150, 70, 75.5, 30)

    boxer = get_boxer_by_id(1)

    assert boxer.name == "Ali"
    assert boxer.id == 1
    assert isinstance(boxer, Boxer)

def test_get_boxer_by_id_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_id(42)

def test_get_boxer_by_name_success(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ali", 150, 70, 75.5, 30)

    boxer = get_boxer_by_name("Ali")
    assert boxer.name == "Ali"

def test_get_boxer_by_name_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_name("Ghost")
        
        
def test_get_weight_class_valid():
    assert get_weight_class(210) == "HEAVYWEIGHT"
    assert get_weight_class(170) == "MIDDLEWEIGHT"
    assert get_weight_class(140) == "LIGHTWEIGHT"
    assert get_weight_class(125) == "FEATHERWEIGHT"

def test_get_weight_class_invalid():
    with pytest.raises(ValueError, match="Invalid weight"):
        get_weight_class(100)
        

def test_update_boxer_stats_win(mock_cursor):
    mock_cursor.fetchone.return_value = True

    update_boxer_stats(1, "win")

    update_query = normalize_whitespace(
        "UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?"
    )
    actual = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual == update_query
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_update_boxer_stats_loss(mock_cursor):
    mock_cursor.fetchone.return_value = True

    update_boxer_stats(1, "loss")

    update_query = normalize_whitespace(
        "UPDATE boxers SET fights = fights + 1 WHERE id = ?"
    )
    actual = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual == update_query
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_update_boxer_stats_invalid_result():
    with pytest.raises(ValueError, match="Invalid result"):
        update_boxer_stats(1, "draw")

def test_update_boxer_stats_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        update_boxer_stats(99, "win")
        
        
def test_get_leaderboard_sort_by_win_pct(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Ali", 150, 70, 75.5, 30, 10, 9, 0.9)
    ]
    leaderboard = get_leaderboard("win_pct")

    assert leaderboard[0]["name"] == "Ali"
    assert leaderboard[0]["win_pct"] == 90.0

def test_get_leaderboard_invalid_sort():
    with pytest.raises(ValueError, match="Invalid sort_by"):
        get_leaderboard("invalid")
