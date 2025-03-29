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
    checks if a connection to the database can be succesfully established. 

    Executes a select statement to confirm that the database is accessible.

    Raises:
        Exception: If a aconnection error or SQL error occurs. 
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
    """
    Checks whether a specific table exists in the database.

    Args:
        tablename (str): The name of the table to check.

    Raises: 
        Exception: If the table does not exist or a database error occurs.
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
    """
    Context manager for safely opening and closing a database connection

    Yields: 
        sqlite3.Connection: An active SQLite3 database connection

    Raises:
        sqlite3.Error: If a connection to the database cannot be established.
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
