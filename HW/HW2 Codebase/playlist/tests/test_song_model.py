from contextlib import contextmanager
import re
import sqlite3

import pytest

from playlist.models.song_model import (
    Song,
    create_song,
    delete_song,
    get_song_by_id,
    get_song_by_compound_key,
    get_all_songs,
    get_random_song,
    update_play_count
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("playlist.models.song_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_song(mock_cursor):
    """Test creating a new song in the catalog.

    """
    create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=180)

    expected_query = normalize_whitespace("""
        INSERT INTO songs (artist, title, year, genre, duration)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Artist Name", "Song Title", 2022, "Pop", 180)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_song_duplicate(mock_cursor):
    """Test creating a song with a duplicate artist, title, and year (should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: songs.artist, songs.title, songs.year")

    with pytest.raises(ValueError, match="Song with artist 'Artist Name', title 'Song Title', and year 2022 already exists."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=180)


def test_create_song_invalid_duration():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)

    """
    with pytest.raises(ValueError, match=r"Invalid duration: -180 \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=-180)

    with pytest.raises(ValueError, match=r"Invalid duration: invalid \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration="invalid")


def test_create_song_invalid_year():
    """Test error when trying to create a song with an invalid year (e.g., less than 1900 or non-integer).

    """
    with pytest.raises(ValueError, match=r"Invalid year: 1899 \(must be an integer greater than or equal to 1900\)."):
        create_song(artist="Artist Name", title="Song Title", year=1899, genre="Pop", duration=180)

    with pytest.raises(ValueError, match=r"Invalid year: invalid \(must be an integer greater than or equal to 1900\)."):
        create_song(artist="Artist Name", title="Song Title", year="invalid", genre="Pop", duration=180)


def test_delete_song(mock_cursor):
    """Test deleting a song from the catalog by song ID.

    """
    # Simulate the existence of a song w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_song(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM songs WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM songs WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_song_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song.

    """
    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Song with ID 999 not found"):
        delete_song(999)


######################################################
#
#    Get Song
#
######################################################


def test_get_song_by_id(mock_cursor):
    """Test getting a song by id.

    """
    mock_cursor.fetchone.return_value = (1, "Artist Name", "Song Title", 2022, "Pop", 180, False)

    result = get_song_by_id(1)

    expected_result = Song(1, "Artist Name", "Song Title", 2022, "Pop", 180)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration FROM songs WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_song_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent song.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Song with ID 999 not found"):
        get_song_by_id(999)


def test_get_song_by_compound_key(mock_cursor):
    """Test getting a song by compound key.

    """
    mock_cursor.fetchone.return_value = (1, "Artist Name", "Song Title", 2022, "Pop", 180, False)

    result = get_song_by_compound_key("Artist Name", "Song Title", 2022)

    expected_result = Song(1, "Artist Name", "Song Title", 2022, "Pop", 180)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration FROM songs WHERE artist = ? AND title = ? AND year = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Artist Name", "Song Title", 2022)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_song_by_compound_key_bad_id(mock_cursor):
    """Test error when getting a non-existent song.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Song with artist 'Artist Name', title 'Song Title', and year 2022 not found"):
        get_song_by_compound_key("Artist Name", "Song Title", 2022)


def test_get_all_songs(mock_cursor):
    """Test retrieving all songs.

    """
    mock_cursor.fetchall.return_value = [
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10, False),
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20, False),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5, False)
    ]

    songs = get_all_songs()

    expected_result = [
        {"id": 1, "artist": "Artist A", "title": "Song A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 2, "artist": "Artist B", "title": "Song B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 3, "artist": "Artist C", "title": "Song C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert songs == expected_result, f"Expected {expected_result}, but got {songs}"

    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM songs
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_all_songs_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all songs returns an empty list when the catalog is empty and logs a warning.

    """
    mock_cursor.fetchall.return_value = []

    result = get_all_songs()

    assert result == [], f"Expected empty list, but got {result}"

    assert "The song catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."

    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_all_songs_ordered_by_play_count(mock_cursor):
    """Test retrieving all songs ordered by play count.

    """
    mock_cursor.fetchall.return_value = [
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    songs = get_all_songs(sort_by_play_count=True)

    expected_result = [
        {"id": 2, "artist": "Artist B", "title": "Song B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 1, "artist": "Artist A", "title": "Song A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 3, "artist": "Artist C", "title": "Song C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert songs == expected_result, f"Expected {expected_result}, but got {songs}"

    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM songs
        ORDER BY play_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_random_song(mock_cursor, mocker):
    """Test retrieving a random song from the catalog.

    """
    mock_cursor.fetchall.return_value = [
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    # Mock random number generation to return the 2nd song
    mock_random = mocker.patch("playlist.models.song_model.get_random", return_value=2)

    result = get_random_song()

    expected_result = Song(2, "Artist B", "Song B", 2021, "Pop", 180)
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure that the random number was called with the correct number of songs
    mock_random.assert_called_once_with(3)

    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_random_song_empty_catalog(mock_cursor, mocker):
    """Test retrieving a random song when the catalog is empty.

    """
    mock_cursor.fetchall.return_value = []

    mock_random = mocker.patch("playlist.models.song_model.get_random")

    with pytest.raises(ValueError, match="The song catalog is empty"):
        get_random_song()

    # Ensure that the random number was not called since there are no songs
    mock_random.assert_not_called()

    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs ")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


######################################################
#
#    Play count
#
######################################################


def test_update_play_count(mock_cursor):
    """Test updating the play count of a song.

    """
    mock_cursor.fetchone.return_value = True

    song_id = 1
    update_play_count(song_id)

    expected_query = normalize_whitespace("""
        UPDATE songs SET play_count = play_count + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (song_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
