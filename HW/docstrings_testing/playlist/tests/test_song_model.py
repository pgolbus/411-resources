from contextlib import contextmanager
import re
import sqlite3

import pytest

from music_collection.models.song_model import (
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

    mocker.patch("music_collection.models.song_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_song(mock_cursor):
    """Test creating a new song in the catalog."""

    # Call the function to create a new song
    create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=180)

    expected_query = normalize_whitespace("""
        INSERT INTO songs (artist, title, year, genre, duration)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Artist Name", "Song Title", 2022, "Pop", 180)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_song_duplicate(mock_cursor):
    """Test creating a song with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: songs.artist, songs.title, songs.year")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Song with artist 'Artist Name', title 'Song Title', and year 2022 already exists."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=180)

def test_create_song_invalid_duration():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid song duration: -180 \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=-180)

    # Attempt to create a song with a non-integer duration
    with pytest.raises(ValueError, match="Invalid song duration: invalid \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration="invalid")

def test_create_song_invalid_year():
    """Test error when trying to create a song with an invalid year (e.g., less than 1900 or non-integer)."""

    # Attempt to create a song with a year less than 1900
    with pytest.raises(ValueError, match="Invalid year provided: 1899 \(must be an integer greater than or equal to 1900\)."):
        create_song(artist="Artist Name", title="Song Title", year=1899, genre="Pop", duration=180)

    # Attempt to create a song with a non-integer year
    with pytest.raises(ValueError, match="Invalid year provided: invalid \(must be an integer greater than or equal to 1900\)."):
        create_song(artist="Artist Name", title="Song Title", year="invalid", genre="Pop", duration=180)

def test_delete_song(mock_cursor):
    """Test soft deleting a song from the catalog by song ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_song(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM songs WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE songs SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_song_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Song with ID 999 not found"):
        delete_song(999)

def test_delete_song_already_deleted(mock_cursor):
    """Test error when trying to delete a song that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match="Song with ID 999 has already been deleted"):
        delete_song(999)

######################################################
#
#    Get Song
#
######################################################

def test_get_song_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Artist Name", "Song Title", 2022, "Pop", 180, False)

    # Call the function and check the result
    result = get_song_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Song(1, "Artist Name", "Song Title", 2022, "Pop", 180)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, deleted FROM songs WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_song_by_id_bad_id(mock_cursor):
    # Simulate that no song exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Song with ID 999 not found"):
        get_song_by_id(999)

def test_get_song_by_compound_key(mock_cursor):
    # Simulate that the song exists (artist = "Artist Name", title = "Song Title", year = 2022)
    mock_cursor.fetchone.return_value = (1, "Artist Name", "Song Title", 2022, "Pop", 180, False)

    # Call the function and check the result
    result = get_song_by_compound_key("Artist Name", "Song Title", 2022)

    # Expected result based on the simulated fetchone return value
    expected_result = Song(1, "Artist Name", "Song Title", 2022, "Pop", 180)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, deleted FROM songs WHERE artist = ? AND title = ? AND year = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Artist Name", "Song Title", 2022)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_all_songs(mock_cursor):
    """Test retrieving all songs that are not marked as deleted."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10, False),
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20, False),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5, False)
    ]

    # Call the get_all_songs function
    songs = get_all_songs()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "artist": "Artist A", "title": "Song A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 2, "artist": "Artist B", "title": "Song B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 3, "artist": "Artist C", "title": "Song C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert songs == expected_result, f"Expected {expected_result}, but got {songs}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM songs
        WHERE deleted = FALSE
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_songs_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all songs returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no songs)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_songs function
    result = get_all_songs()

    # Ensure the result is an empty list
    assert result == [], f"Expected empty list, but got {result}"

    # Ensure that a warning was logged
    assert "The song catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_songs_ordered_by_play_count(mock_cursor):
    """Test retrieving all songs ordered by play count."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    # Call the get_all_songs function with sort_by_play_count = True
    songs = get_all_songs(sort_by_play_count=True)

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "artist": "Artist B", "title": "Song B", "year": 2021, "genre": "Pop", "duration": 180, "play_count": 20},
        {"id": 1, "artist": "Artist A", "title": "Song A", "year": 2020, "genre": "Rock", "duration": 210, "play_count": 10},
        {"id": 3, "artist": "Artist C", "title": "Song C", "year": 2022, "genre": "Jazz", "duration": 200, "play_count": 5}
    ]

    assert songs == expected_result, f"Expected {expected_result}, but got {songs}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, artist, title, year, genre, duration, play_count
        FROM songs
        WHERE deleted = FALSE
        ORDER BY play_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_song(mock_cursor, mocker):
    """Test retrieving a random song from the catalog."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (1, "Artist A", "Song A", 2020, "Rock", 210, 10),
        (2, "Artist B", "Song B", 2021, "Pop", 180, 20),
        (3, "Artist C", "Song C", 2022, "Jazz", 200, 5)
    ]

    # Mock random number generation to return the 2nd song
    mock_random = mocker.patch("music_collection.models.song_model.get_random", return_value=2)

    # Call the get_random_song method
    result = get_random_song()

    # Expected result based on the mock random number and fetchall return value
    expected_result = Song(2, "Artist B", "Song B", 2021, "Pop", 180)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure that the random number was called with the correct number of songs
    mock_random.assert_called_once_with(3)

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_song_empty_catalog(mock_cursor, mocker):
    """Test retrieving a random song when the catalog is empty."""

    # Simulate that the catalog is empty
    mock_cursor.fetchall.return_value = []

    # Expect a ValueError to be raised when calling get_random_song with an empty catalog
    with pytest.raises(ValueError, match="The song catalog is empty"):
        get_random_song()

    # Ensure that the random number was not called since there are no songs
    mocker.patch("music_collection.models.song_model.get_random").assert_not_called()

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, artist, title, year, genre, duration, play_count FROM songs WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_update_play_count(mock_cursor):
    """Test updating the play count of a song."""

    # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_play_count function with a sample song ID
    song_id = 1
    update_play_count(song_id)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE songs SET play_count = play_count + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (song_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Song:
def test_update_play_count_deleted_song(mock_cursor):
    """Test error when trying to update play count for a deleted song."""

    # Simulate that the song exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Song with ID 1 has been deleted"):
        update_play_count(1)

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM songs WHERE id = ?", (1,))
