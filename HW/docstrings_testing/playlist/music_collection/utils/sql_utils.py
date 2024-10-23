from contextlib import contextmanager
import logging
import os
import sqlite3

from music_collection.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# load the db path from the environment with a default value
DB_PATH = os.getenv("DB_PATH", "/app/sql/song_catalog.db")


def check_database_connection():
    """Check the database connection

    Raises:
        Exception: If the database connection is not OK
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # This ensures the connection is actually active
        cursor.execute("SELECT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """Check if the table exists by querying it

    Args:
        tablename (str): The name of the table to check

    Raises:
        Exception: If the table does not exist
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM {tablename} LIMIT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Table check error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connection.

    Yields:
        sqlite3.Connection: The SQLite connection object.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.error("Database connection error: %s", str(e))
        raise e
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
