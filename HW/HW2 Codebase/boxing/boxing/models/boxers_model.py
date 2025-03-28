from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


# Set up module-level logger
logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Boxer:
    """
    Represents a boxer with attributes relevant to boxing statistics.

    Attributes:
        id (int): Unique identifier for the boxer.
        name (str): Name of the boxer.
        weight (int): Weight of the boxer in pounds.
        height (int): Height in inches.
        reach (float): Reach in inches.
        age (int): Age in years.
        weight_class (str): Automatically assigned based on weight.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Automatically assign weight class after initialization."""
        self.weight_class = get_weight_class(self.weight)
        logger.debug(f"Initialized Boxer: {self.name} | Weight class: {self.weight_class}")


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """
    Create a new boxer and insert into the database

    Args:
        name (str): Boxer's name (must be unique).
        weight (int): Weight in pounds (must be greater than or equal to 125)
        height (int): Height in inches (must be greater than 0)
        reach (float): Reach in inches (must be greater than 0)
        age (int): Age (must be between 18 and 40)

    Raises:
        ValueError: If any validation fails or boxer already exists
        sqlite3.Error: For unexpected database errors
    """
    logger.info(f"Creating boxer: {name}")
    if weight < 125:
        logger.error(f"Invalid weight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height: {height}")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid reach: {reach}")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age: {age}")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Attempted to create duplicate boxer: {name}")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()
            logger.info(f"Boxer '{name}' successfully added to the database.")
    except sqlite3.IntegrityError:
        logger.error(f"IntegrityError while adding boxer '{name}' (duplicate likely).")
        raise ValueError(f"Boxer with name '{name}' already exists")
    except sqlite3.Error as e:
        logger.exception(f"Database error while adding boxer '{name}': {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """
    Deletes a boxer from the database using the id

    Args:
        boxer_id (int): The id of the boxer to delete

    Raises:
        ValueError: If the boxer doesn't exist
        sqlite3.Error: If the database operation fails
    """
    logger.info(f"Attempting to delete boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID {boxer_id} deleted.")
    except sqlite3.Error as e:
        logger.exception(f"Error while deleting boxer {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Retrieves a leaderboard of boxers with fights and wins

    Args:
        sort_by (str): Either "wins" or "win_pct" to sort by total wins or win percentage.

    Returns:
        List[dict[str, Any]]: List of boxer stats dictionaries sorted

    Raises:
        ValueError: If an invalid sort_by value is passed through
        sqlite3.Error: On database error.
    """
    logger.info(f"Generating leaderboard sorted by '{sort_by}'")
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """
    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort parameter: {sort_by}")
        raise ValueError(f"Invalid sort parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)
            }
            leaderboard.append(boxer)
        logger.info(f"Leaderboard generated with {len(leaderboard)} boxers.")
        return leaderboard

    except sqlite3.Error as e:
        logger.exception(f"Database error retrieving leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Fetch a boxer from the database by id

    Args:
        boxer_id (int): The ID of the boxer

    Returns:
        Boxer: A Boxer object with the data retrieved.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: On database error.
    """
    logger.info(f"Fetching boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))
            row = cursor.fetchone()

            if row:
                logger.info(f"Found boxer with id {boxer_id}")
                return Boxer(*row)
            else:
                logger.warning(f"No boxer found with id {boxer_id}")
                raise ValueError(f"Boxer with id {boxer_id} not found.")
    except sqlite3.Error as e:
        logger.exception(f"Database error fetching boxer id {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Fetch a boxer from the database by name

    Args:
        boxer_name (str): The name of the boxer.

    Returns:
        Boxer: A Boxer object.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: On database error.
    """
    logger.info(f"Fetching boxer with name '{boxer_name}'")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))
            row = cursor.fetchone()

            if row:
                logger.info(f"Found boxer '{boxer_name}'")
                return Boxer(*row)
            else:
                logger.warning(f"No boxer found with name '{boxer_name}'")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.exception(f"Database error fetching boxer '{boxer_name}': {e}")
        raise e

def get_weight_class(weight: int) -> str:
    """
    Determine a boxer's weight class based on weight.

    Args:
        weight (int): The weight of the boxer in pounds.

    Returns:
        str: Weight class.

    Raises:
        ValueError: If weight is below the valid minimum.
    """
    if weight >= 203:
        return 'HEAVYWEIGHT'
    elif weight >= 166:
        return 'MIDDLEWEIGHT'
    elif weight >= 133:
        return 'LIGHTWEIGHT'
    elif weight >= 125:
        return 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Update a boxer's stats with a new fight result.

    Args:
        boxer_id (int): ID of the boxer.
        result (str): Either "win" or "loss".

    Raises:
        ValueError: If boxer does not exist or result is invalid.
        sqlite3.Error: On database error.
    """
    logger.info(f"Updating stats for boxer {boxer_id} with result '{result}'")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found for update.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer {boxer_id} stats updated with result '{result}'.")

    except sqlite3.Error as e:
        logger.exception(f"Error updating boxer {boxer_id} stats: {e}")
        raise e