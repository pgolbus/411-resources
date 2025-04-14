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
    Checks that the database connection is working

    Attempts to open a connection and execute (`SELECT 1`)
    to check that the database is reachable.

    Raises:
        Exception: If the database connection or query fails.
    """
    logger.info("Checking database connection")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute a simple query to verify the connection is active
        cursor.execute("SELECT 1;")
        conn.close()
        logger.info("Database connection is healthy")
    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """
    Checks whether a specific table exists in the database by name

    Args:
        tablename (str): The name of the table that it's checking

    Raises:
        Exception: If the table doesn't exist or if a database error occurs.
    """
    logger.info(f"Checking if table '{tablename}' exists")
    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
        result = cursor.fetchone()

        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            logger.warning(error_message)
            raise Exception(error_message)
    
        logger.info(f"Table '{tablename}' exists.")

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        logger.exception(error_message)
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """
    Context manager that opens a database connection and closes it after

    Yields:
        sqlite3.Connection: An active SQLite database connection

    Raises:
        sqlite3.Error: If a database connection error occurs
    """
    conn = None
    try:
        logger.debug("Opening new database connection")
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.exception("Database connection failed")
        raise e
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")
