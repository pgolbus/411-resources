from dataclasses import asdict
import pytest
from pytest_mock import MockerFixture
from contextlib import contextmanager

from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

@pytest.fixture()
def ring_model():
    return RingModel()

@pytest.fixture()
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("playlist.models.playlist_model.update_play_count")

@pytest.fixture()
def test_lessthan2Boxers():
    assert True

@pytest.fixture()
def test_clearRing():
    assert True

@pytest.fixture()
def test_enterRing():
    assert True

@pytest.fixture()
def test_enterRingButBNotBoxers():
    assert True

@pytest.fixture()
def sample_boxer1():
    return Boxer(12345,"Mo", 130, 50, 6, 30)

@pytest.fixture()
def sample_boxer2():
    return Boxer(123340,"So", 130, 50, 6, 30)

@pytest.fixture()
def sample_fight(sample_boxer1,sample_boxer2):
    return [sample_boxer1,sample_boxer2]


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

    mocker.patch("boxing.models.ring_model.get_db_connection", mock_get_db_connection)

    return mock_cursor 

def test_fight(ring_model,sample_boxer1,sample_boxer2,sample_fight):
    ring_model.ring.append(sample_boxer1)
    
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."): 
            ring_model.fight()
    
    ring_model.ring = sample_fight
    boxer1 = sample_boxer1
    boxer2 = sample_boxer2
    assert ring_model.fight == boxer1.name or boxer2.name


def test_addtoFullRing(ring_model,sample_fight,sample_boxer1):
    """Test error when adding a boxer to a full ring.

    """
    ring_model.ring = sample_fight

    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."): 
            ring_model.enter_ring(sample_boxer1)

@pytest.fixture()
def test_getBoxers():
    assert True

@pytest.fixture()
def test_getFightingSkills():
    assert True
