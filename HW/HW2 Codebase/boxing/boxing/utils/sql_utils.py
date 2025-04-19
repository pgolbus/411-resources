from contextlib import contextmanager
import logging
import os
import sqlite3

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# load the db path from the environment with a default value
DB_PATH = os.getenv("DB_PATH", "/app/sql/boxing.db")


def check_database_connection():
    """
    Check connection to the database

    Raises:
        Exception: If the database connection is not OK.

    """
    try:
        logger.info("Checking the connection to the database...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute a simple query to verify the connection is active
        cursor.execute("SELECT 1;")
        conn.close("Successful database connection.")


    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error("Error connecting to the database.")
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """
    Queries the SQLite master table to check if the table, tablename, exists.

    Args:
        tablename (str): The name of the table being checked.

    Raises:
        Exception: If the table does not exist.

    """
    try:
        logger.info("Checking if the table exists...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
        result = cursor.fetchone()

        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            logger.error("The table does not exist.")
            raise Exception(error_message)

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        logger.error("Database error [table].")
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connection.

    Yields:
        sqlite3.Connection: The connection object.

    Raises:
        sqlite3.Error: If there is an issue connecting to the database.

    """
    conn = None
    try:
        logger.info("Getting the database connection...")
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.error("Database error [fetching db connection].")
        raise e
    finally:
        if conn:
            conn.close()
            logger.info("The database connection has been closed.")
