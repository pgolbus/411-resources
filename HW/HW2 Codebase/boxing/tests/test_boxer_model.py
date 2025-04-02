from dataclasses import asdict

import pytest

from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

@pytest.fixture()
def boxer_model():
    return create_boxer()

def test_addBoxer_with_Invalid_height():
    return true

def test_addBoxer_with_Invalid_weight():
    return true

def test_addBoxer_with_Invalid_reach():
    return true

def test_addBoxer_with_Invalid_age():
    return true

def test_add_duplicate_boxer(boxer_model, sample_boxer1):
    """Test error when adding a duplicate boxer

    """
    playlist_model.add_song_to_playlist(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer with name already exists"):
        playlist_model.add_song_to_playlist(sample_song1)

@pytest.fixture()
def delete_boxer_test():
    return true

@pytest.fixture()
def delete_boxer_DNEinDB_test():
    return true

@pytest.fixture()
def get_leaderboard_test():
    return true

@pytest.fixture()
def get_leaderboard_withInvalidSort_test():
    return true

@pytest.fixture()
def get_boxer_by_id_test():
    return true

@pytest.fixture()
def get_boxer_by_idDNE_test():
    return true

@pytest.fixture()
def get_boxer_by_name_test():
    return true

@pytest.fixture()
def get_boxer_by_nameDNE_test():
    return true

@pytest.fixture()
def get_weight_class():
    return true

@pytest.fixture()
def get_weight_classInvalid():
    return true

@pytest.fixture()
def update_boxer_stats_test():
    return true

@pytest.fixture()
def update_boxer_stats_butINvalidResult():
    return true

@pytest.fixture()
def update_boxer_stats_butBoxerDNE():
    return true
