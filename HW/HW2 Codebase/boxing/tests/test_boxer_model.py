from dataclasses import asdict

import pytest

from playlist.models.playlist_model import PlaylistModel
from playlist.models.song_model import Song

@pytest.fixture()
def boxer_model():
    return create_boxer()

@pytest.fixture()
def delete_boxer_test():
    return true

@pytest.fixture()
def get_leaderboard_test():
    return true

@pytest.fixture()
def boxer_model():
    return create_boxer();

@pytest.fixture()
def get_boxer_by_id_test():
    return true

@pytest.fixture()
def get_boxer_by_name():
    return true

@pytest.fixture()
def get_weight_class():
    return true

@pytest.fixture()
def update_boxer_stats():
    return true


