import pytest
from unittest.mock import patch, MagicMock
from boxing.models import boxers_model


def test_get_weight_class_valid():
    assert boxers_model.get_weight_class(210) == 'HEAVYWEIGHT'
    assert boxers_model.get_weight_class(180) == 'MIDDLEWEIGHT'
    assert boxers_model.get_weight_class(140) == 'LIGHTWEIGHT'
    assert boxers_model.get_weight_class(130) == 'FEATHERWEIGHT'

def test_get_weight_class_invalid():
    with pytest.raises(ValueError):
        boxers_model.get_weight_class(100)


@patch("boxing.models.boxers_model.get_db_connection")
def test_create_boxer_valid(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    boxers_model.create_boxer("Rocky", 160, 70, 70.0, 25)

    mock_cursor.execute.assert_any_call("SELECT 1 FROM boxers WHERE name = ?", ("Rocky",))


@patch("boxing.models.boxers_model.get_db_connection")
def test_create_boxer_duplicate_name(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = True

    with pytest.raises(ValueError, match="already exists"):
        boxers_model.create_boxer("Rocky", 160, 70, 70.0, 25)


@patch("boxing.models.boxers_model.get_db_connection")
def test_get_boxer_by_id_found(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "Ali", 160, 70, 70.0, 28)

    boxer = boxers_model.get_boxer_by_id(1)
    assert boxer.name == "Ali"
    assert boxer.weight_class == "LIGHTWEIGHT"

@patch("boxing.models.boxers_model.get_db_connection")
def test_get_boxer_by_id_not_found(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        boxers_model.get_boxer_by_id(42)
