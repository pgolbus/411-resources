from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from music_collection.utils.logger import configure_logger
from music_collection.utils.random_utils import get_random
from music_collection.utils.sql_utils import get_db_connection


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Song:
    id: int
    artist: str
    title: str
    year: int
    genre: str
    duration: int  # in seconds

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError(f"Duration must be greater than 0, got {self.duration}")
        if self.year <= 1900:
            raise ValueError(f"Year must be greater than 1900, got {self.year}")


def create_song(artist: str, title: str, year: int, genre: str, duration: int) -> None:
    """
    Creates a new song in the songs table.

    Args:
        artist (str): The artist's name.
        title (str): The song title.
        year (int): The year the song was released.
        genre (str): The song genre.
        duration (int): The duration of the song in seconds.

    Raises:
        ValueError: If year or duration are invalid.
        sqlite3.IntegrityError: If a song with the same compound key (artist, title, year) already exists.
        sqlite3.Error: For any other database errors.
    """
    # Validate the required fields
    if not isinstance(year, int) or year < 1900:
        raise ValueError(f"Invalid year provided: {year} (must be an integer greater than or equal to 1900).")
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError(f"Invalid song duration: {duration} (must be a positive integer).")

    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO songs (artist, title, year, genre, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (artist, title, year, genre, duration))
            conn.commit()

            logger.info("Song created successfully: %s - %s (%d)", artist, title, year)

    except sqlite3.IntegrityError as e:
        logger.error("Song with artist '%s', title '%s', and year %d already exists.", artist, title, year)
        raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating song: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")


def delete_song(song_id: int) -> None:
    """
    Soft deletes a song from the catalog by marking it as deleted.

    Args:
        song_id (int): The ID of the song to delete.

    Raises:
        ValueError: If the song with the given ID does not exist or is already marked as deleted.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists and if it's already deleted
            cursor.execute("SELECT deleted FROM songs WHERE id = ?", (song_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Song with ID %s has already been deleted", song_id)
                    raise ValueError(f"Song with ID {song_id} has already been deleted")
            except TypeError:
                logger.info("Song with ID %s not found", song_id)
                raise ValueError(f"Song with ID {song_id} not found")

            # Perform the soft delete by setting 'deleted' to TRUE
            cursor.execute("UPDATE songs SET deleted = TRUE WHERE id = ?", (song_id,))
            conn.commit()

            logger.info("Song with ID %s marked as deleted.", song_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting song: %s", str(e))
        raise e

def get_song_by_id(song_id: int) -> Song:
    """
    Retrieves a song from the catalog by its song ID.

    Args:
        song_id (int): The ID of the song to retrieve.

    Returns:
        Song: The Song object corresponding to the song_id.

    Raises:
        ValueError: If the song is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve song with ID %s", song_id)
            cursor.execute("""
                SELECT id, artist, title, year, genre, duration, deleted
                FROM songs
                WHERE id = ?
            """, (song_id,))
            row = cursor.fetchone()

            if row:
                if row[6]:  # deleted flag
                    logger.info("Song with ID %s has been deleted", song_id)
                    raise ValueError(f"Song with ID {song_id} has been deleted")
                logger.info("Song with ID %s found", song_id)
                return Song(id=row[0], artist=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5])
            else:
                logger.info("Song with ID %s not found", song_id)
                raise ValueError(f"Song with ID {song_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving song by ID %s: %s", song_id, str(e))
        raise e

def get_song_by_compound_key(artist: str, title: str, year: int) -> Song:
    """
    Retrieves a song from the catalog by its compound key (artist, title, year).

    Args:
        artist (str): The artist of the song.
        title (str): The title of the song.
        year (int): The year of the song.

    Returns:
        Song: The Song object corresponding to the compound key.

    Raises:
        ValueError: If the song is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve song with artist '%s', title '%s', and year %d", artist, title, year)
            cursor.execute("""
                SELECT id, artist, title, year, genre, duration, deleted
                FROM songs
                WHERE artist = ? AND title = ? AND year = ?
            """, (artist, title, year))
            row = cursor.fetchone()

            if row:
                if row[6]:  # deleted flag
                    logger.info("Song with artist '%s', title '%s', and year %d has been deleted", artist, title, year)
                    raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} has been deleted")
                logger.info("Song with artist '%s', title '%s', and year %d found", artist, title, year)
                return Song(id=row[0], artist=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5])
            else:
                logger.info("Song with artist '%s', title '%s', and year %d not found", artist, title, year)
                raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving song by compound key (artist '%s', title '%s', year %d): %s", artist, title, year, str(e))
        raise e

def get_all_songs(sort_by_play_count: bool = False) -> list[dict]:
    """
    Retrieves all songs that are not marked as deleted from the catalog.

    Args:
        sort_by_play_count (bool): If True, sort the songs by play count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all non-deleted songs with play_count.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted songs from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, artist, title, year, genre, duration, play_count
                FROM songs
                WHERE deleted = FALSE
            """
            if sort_by_play_count:
                query += " ORDER BY play_count DESC"

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The song catalog is empty.")
                return []

            songs = [
                {
                    "id": row[0],
                    "artist": row[1],
                    "title": row[2],
                    "year": row[3],
                    "genre": row[4],
                    "duration": row[5],
                    "play_count": row[6],
                }
                for row in rows
            ]
            logger.info("Retrieved %d songs from the catalog", len(songs))
            return songs

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all songs: %s", str(e))
        raise e

def get_random_song() -> Song:
    """
    Retrieves a random song from the catalog.

    Returns:
        Song: A randomly selected Song object.

    Raises:
        ValueError: If the catalog is empty.
    """
    try:
        all_songs = get_all_songs()

        if not all_songs:
            logger.info("Cannot retrieve random song because the song catalog is empty.")
            raise ValueError("The song catalog is empty.")

        # Get a random index using the random.org API
        random_index = get_random(len(all_songs))
        logger.info("Random index selected: %d (total songs: %d)", random_index, len(all_songs))

        # Return the song at the random index, adjust for 0-based indexing
        song_data = all_songs[random_index - 1]
        return Song(
            id=song_data["id"],
            artist=song_data["artist"],
            title=song_data["title"],
            year=song_data["year"],
            genre=song_data["genre"],
            duration=song_data["duration"]
        )

    except Exception as e:
        logger.error("Error while retrieving random song: %s", str(e))
        raise e

def update_play_count(song_id: int) -> None:
    """
    Increments the play count of a song by song ID.

    Args:
        song_id (int): The ID of the song whose play count should be incremented.

    Raises:
        ValueError: If the song does not exist or is marked as deleted.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update play count for song with ID %d", song_id)

            # Check if the song exists and if it's deleted
            cursor.execute("SELECT deleted FROM songs WHERE id = ?", (song_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Song with ID %d has been deleted", song_id)
                    raise ValueError(f"Song with ID {song_id} has been deleted")
            except TypeError:
                logger.info("Song with ID %d not found", song_id)
                raise ValueError(f"Song with ID {song_id} not found")

            # Increment the play count
            cursor.execute("UPDATE songs SET play_count = play_count + 1 WHERE id = ?", (song_id,))
            conn.commit()

            logger.info("Play count incremented for song with ID: %d", song_id)

    except sqlite3.Error as e:
        logger.error("Database error while updating play count for song with ID %d: %s", song_id, str(e))
        raise e
