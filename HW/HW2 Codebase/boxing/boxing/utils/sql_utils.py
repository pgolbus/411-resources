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
    """ Checks the database connection.

    Raises: 
        Exception: If there is an error in connecting to the database or executing a query.
        
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute a simple query to verify the connection is active
        cursor.execute("SELECT 1;")
        conn.close()

    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """Checks if the specified table exists in the SQLite database.

    Args:
        tablename (str): The name of the table to check.

    Raises:
        Exception: If the table does not exist or if there's an error during the database query.
    """
    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
        result = cursor.fetchone()

        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            raise Exception(error_message)

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """Provides a context-managed connection to an SQLite database.

    Yields:
        sqlite3.Connection: Connection object to the SQLite database specified by DB_PATH.

    Raises:
        sqlite3.Error: If there is an issue connecting to the database.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        raise e
    finally:
        if conn:
            conn.close()
