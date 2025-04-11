from dataclasses import dataclass
import logging
import sqlite3

from playlist.utils.logger import configure_logger
from playlist.utils.api_utils import get_random
from playlist.utils.sql_utils import get_db_connection


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
    """Creates a new song in the songs table.

    Args:
        artist (str): The artist's name.
        title (str): The song title.
        year (int): The year the song was released.
        genre (str): The song genre.
        duration (int): The duration of the song in seconds.

    Raises:
        ValueError: If any field is invalid.
        sqlite3.IntegrityError: If a song with the same compound key (artist, title, year) already exists.
        sqlite3.Error: For any other database errors.

    """
    logger.info(f"Received request to create song: {artist} - {title} ({year})")

    if not isinstance(artist, str) or not artist.strip():
        logger.warning("Invalid artist name provided.")
        raise ValueError("Invalid artist name: must be a non-empty string.")

    if not isinstance(title, str) or not title.strip():
        logger.warning("Invalid song title provided.")
        raise ValueError("Invalid song title: must be a non-empty string.")

    if not isinstance(year, int) or year < 1900:
        logger.warning(f"Invalid year provided: {year}")
        raise ValueError(f"Invalid year: {year} (must be an integer greater than or equal to 1900).")

    if not isinstance(genre, str) or not genre.strip():
        logger.warning("Invalid genre provided.")
        raise ValueError("Invalid genre: must be a non-empty string.")

    if not isinstance(duration, int) or duration <= 0:
        logger.warning(f"Invalid song duration provided: {duration}")
        raise ValueError(f"Invalid duration: {duration} (must be a positive integer).")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO songs (artist, title, year, genre, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (artist, title, year, genre, duration))
            conn.commit()

            logger.info(f"Song successfully added: {artist} - {title} ({year})")

    except sqlite3.IntegrityError:
        logger.error(f"Song already exists: {artist} - {title} ({year})")
        raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} already exists.")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating song: {e}")
        raise sqlite3.Error(f"Database error: {e}")

def delete_song(song_id: int) -> None:
    """Permanently deletes a song from the catalog.

    Args:
        song_id (int): The ID of the song to delete.

    Raises:
        ValueError: If the song with the given ID does not exist.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists before attempting deletion
            cursor.execute("SELECT id FROM songs WHERE id = ?", (song_id,))
            song = cursor.fetchone()

            if not song:
                logger.warning(f"Attempted to delete non-existent song with ID {song_id}")
                raise ValueError(f"Song with ID {song_id} not found")

            cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            conn.commit()

            logger.info(f"Successfully deleted song with ID {song_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting song: {e}")
        raise e

def get_song_by_id(song_id: int) -> Song:
    """Retrieves a song from the catalog by its song ID.

    Args:
        song_id (int): The ID of the song to retrieve.

    Returns:
        Song: The Song object corresponding to the song_id.

    Raises:
        ValueError: If the song is not found.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve song with ID {song_id}")
            cursor.execute("""
                SELECT id, artist, title, year, genre, duration
                FROM songs
                WHERE id = ?
            """, (song_id,))
            row = cursor.fetchone()

            if row:
                logger.info(f"Song with ID {song_id} found")
                return Song(id=row[0], artist=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5])
            else:
                logger.info(f"Song with ID {song_id} not found")
                raise ValueError(f"Song with ID {song_id} not found")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving song by ID {song_id}: {e}")
        raise e

def get_song_by_compound_key(artist: str, title: str, year: int) -> Song:
    """Retrieves a song from the catalog by its compound key (artist, title, year).

    Args:
        artist (str): The artist of the song.
        title (str): The title of the song.
        year (int): The year of the song.

    Returns:
        Song: The Song object corresponding to the compound key.

    Raises:
        ValueError: If the song is not found.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve song with artist '{artist}', title '{title}', and year {year}")
            cursor.execute("""
                SELECT id, artist, title, year, genre, duration
                FROM songs
                WHERE artist = ? AND title = ? AND year = ?
            """, (artist, title, year))
            row = cursor.fetchone()

            if row:
                logger.info(f"Song with artist '{artist}', title '{title}', and year {year} found")
                return Song(id=row[0], artist=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5])
            else:
                logger.info(f"Song with artist '{artist}', title '{title}', and year {year} not found")
                raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} not found")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving song by compound key (artist '{artist}', title '{title}', year {year}): {e}")
        raise e

def get_all_songs(sort_by_play_count: bool = False) -> list[dict]:
    """Retrieves all songs from the catalog.

    Args:
        sort_by_play_count (bool): If True, sort the songs by play count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all songs with play_count.

    Raises:
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all songs from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, artist, title, year, genre, duration, play_count
                FROM songs
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
            logger.info(f"Retrieved {len(songs)} songs from the catalog")
            return songs

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving all songs: {e}")
        raise e

def get_random_song() -> Song:
    """Retrieves a random song from the catalog.

    Returns:
        Song: A randomly selected Song object.

    Raises:
        ValueError: If the catalog is empty.
        sqlite3.Error: If any database error occurs.

    """
    try:
        all_songs = get_all_songs()

        if not all_songs:
            logger.info("Cannot retrieve random song because the song catalog is empty.")
            raise ValueError("The song catalog is empty.")

        # Get a random index using the random.org API
        random_index = get_random(len(all_songs))
        logger.info(f"Random index selected: {random_index} (total songs: {len(all_songs)})")

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

    except sqlite3.Error as e:
        logger.error(f"SQLite error while retrieving random song: {e}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error while retrieving random song: {e}")
        raise e

def update_play_count(song_id: int) -> None:
    """Increments the play count of a song by song ID.

    Args:
        song_id (int): The ID of the song whose play count should be incremented.

    Raises:
        ValueError: If the song does not exist.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to update play count for song with ID {song_id}")

            # Ensure the song exists before updating
            cursor.execute("SELECT id FROM songs WHERE id = ?", (song_id,))
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Cannot update play count: Song with ID {song_id} not found.")
                raise ValueError(f"Song with ID {song_id} not found")

            # Increment the play count
            cursor.execute("UPDATE songs SET play_count = play_count + 1 WHERE id = ?", (song_id,))
            conn.commit()

            logger.info(f"Play count incremented for song with ID: {song_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating play count for song with ID {song_id}: {e}")
        raise e
