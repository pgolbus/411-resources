from dataclasses import asdict

from unittest import mock

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import (
    create_boxer, 
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
	update_boxer_stats
)

mock_rows = [
    (1, "Boxer1", 160, 70, 72, 30, 20, 15, 0.75), 
    (2, "Boxer2", 150, 68, 70, 25, 10, 5, 0.5),    
    (3, "Boxer3", 140, 66, 69, 28, 30, 18, 0.6),   
]

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = mock_rows
    mock_cursor.fetchone.return_value = (1, "dup", 160, 70, 72, 30)
    yield mock_conn, mock_cursor

##################################################
# Create Boxer Test Cases
##################################################

def test_invalid_weight():
    """Test error when the boxer is under 125 pounds
	
 	"""
    with pytest.raises(ValueError, match="Invalid weight: 100. Must be at least 125."):
        create_boxer(name="overweight boxer", weight=100, height=70, reach=70, age=25)

def test_invalid_height():
    """Test error when the boxer is under 0 inches
	
 	"""
    with pytest.raises(ValueError, match="Invalid height: -1. Must be greater than 0."):
        create_boxer(name="short boxer", weight=100, height=-1, reach=70, age=25)

def test_invalid_reach():
    """test error when the boxer's reach is under 0 inches.
	
 	"""
    with pytest.raises(ValueError, match="Invalid reach: -1. Must be greater than 0."):
        create_boxer(name="reach boxer", weight=100, height=70, reach=-1, age=25)

def test_invalid_age_younger():
    """Test error when the boxer age is under 18
	
 	"""
    with pytest.raises(ValueError, match="Invalid age: 2. Must be between 18 and 40."):
        create_boxer(name="younger boxer", weight=100, height=70, reach=70, age=2)

def test_invalid_age_older():
    """Test error when the boxer age is over 40
	
 	"""
    with pytest.raises(ValueError, match="Invalid age: 50. Must be between 18 and 40."):
        create_boxer(name="older boxer", weight=100, height=70, reach=70, age=50)

def test_duplicate_name(mock_db_connection):
    """ Test error when the boxer doesn't have a unique name
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with name dup already exists"):
            create_boxer(name="dup", age=20, weight=150, reach=75, height=71)

##################################################
# Boxer Deletion Test Cases
##################################################
def test_delete_boxer(mock_db_connection):
    """test delete boxers for a boxer that exists
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (1, "Boxer1", 160, 70, 72, 30, 20, 15, 0.75)

	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        delete_boxer(1)

def test_delete_boxer_not_exist(mock_db_connection):
    """test delete boxers for a boxer that does not exist
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    mock_cursor.fetchone.return_value = None
	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with ID 100000 not found."):
            delete_boxer(100000)

##################################################
# Get leaderboard Test Cases
##################################################
def test_leaderboards_by_wins(mock_db_connection):
    """tests leaderboards sorted by wins
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        leaderboard = get_leaderboard(sort_by="wins")
    
    assert leaderboard[0]['name'] == "Boxer1"  
    assert leaderboard[1]['name'] == "Boxer3"
    assert leaderboard[2]['name'] == "Boxer2"

def test_leaderboards_by_win_pct(mock_db_connection):
    """tests leaderboards sorted by wins pct
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        leaderboard = get_leaderboard(sort_by="win_pct")
    
    assert leaderboard[0]['name'] == "Boxer1"  
    assert leaderboard[1]['name'] == "Boxer3"
    assert leaderboard[2]['name'] == "Boxer2"

def test_get_leaderboard_invalid_sort_by(mock_db_connection):
    """Test error when the sort_by parameter is invalid.
	
 	"""

	
    mock_conn, mock_cursor = mock_db_connection
	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
            get_leaderboard(sort_by="invalid")

##################################################
# Get Boxer by ID Test Cases
##################################################
def test_get_boxers_by_ID(mock_db_connection):
	
    mock_conn, mock_cursor = mock_db_connection

	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        boxer = get_boxer_by_id(1)

    assert boxer.id == 1
    assert boxer.name == "dup"
    assert boxer.weight == 160
    assert boxer.height == 70
    assert boxer.reach == 72
    assert boxer.age == 30

def test_get_boxer_by_id_not_found(mock_db_connection):
    """Test when the boxer is not found in the database
	
 	"""

	
    mock_conn, mock_cursor = mock_db_connection

	
    mock_cursor.fetchone.return_value = None
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with ID 10000 not found."):
            get_boxer_by_id(10000)

##################################################
# Get Boxer by Name Test Cases
##################################################


def test_get_boxers_by_name(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        boxer = get_boxer_by_name('dup')

    assert boxer.id == 1
    assert boxer.name == "dup"
    assert boxer.weight == 160
    assert boxer.height == 70
    assert boxer.reach == 72
    assert boxer.age == 30

def test_get_boxer_by_name_not_found(mock_db_connection):
    """Test when the boxer is not found in the database
	
 	"""
	
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None

	
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        with pytest.raises(ValueError, match="Boxer with name 'invalid' not found."):
            get_boxer_by_name('invalid')

##################################################
# Get Boxer by Weight Class Test Cases
##################################################
def test_invalid_weight():
    with pytest.raises(ValueError, match="Invalid weight: -1. Weight must be at least 125."):
        get_weight_class(-1)

def test_get_Heavyweight():
    weight = get_weight_class(300)
    assert weight == "HEAVYWEIGHT"

def test_get_middleweight():
    weight = get_weight_class(166)
    assert weight == "MIDDLEWEIGHT"

def test_get_lightweight():
    weight = get_weight_class(133)
    assert weight == "LIGHTWEIGHT"

def test_get_featherweight():
    weight = get_weight_class(125)
    assert weight == "FEATHERWEIGHT"

##################################################
# Update Boxers Stats
##################################################

def test_update_boxer_stats_win(mock_db_connection):
    """Test updating stats for a win
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    mock_cursor.fetchone.return_value = (1,)
    
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
        update_boxer_stats(boxer_id=1, result='win')

def test_update_boxer_stats_loss(mock_db_connection):
    """Test updating stats for a win
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    mock_cursor.fetchone.return_value = (1,)
    
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
		update_boxer_stats(boxer_id=1, result='loss')
		
def test_update_boxer_invalid_win_loss(mock_db_connection):
    """Test updating stats for invalid input
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    mock_cursor.fetchone.return_value = (1,)
	with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
		with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'.")
    			update_boxer_stats(boxer_id=1, result='invalid')

def test_update_boxer_invalid_ID(mock_db_connection):
    """Test updating stats for invalid input 
	
 	"""
    mock_conn, mock_cursor = mock_db_connection
	
    mock_cursor.fetchone.return_value = None 
    
    with mock.patch('boxing.models.boxers_model.get_db_connection', return_value=mock_conn):
		with pytest.raises(ValueError, match="Boxer with ID 102 not found.")
    			update_boxer_stats(boxer_id=102, result='win')
    
	
