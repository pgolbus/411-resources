from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Boxer:
    """Data class representing a boxer."""
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Automatically assign the weight class based on the boxer's weight."""
        self.weight_class = get_weight_class(self.weight)


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """
    Create a new boxer in the database.

    Args:
        name (str): Name of the boxer.
        weight (int): Weight of the boxer in lbs.
        height (int): Height of the boxer.
        reach (float): Reach of the boxer.
        age (int): Age of the boxer.

    Raises:
        ValueError: If inputs are invalid or boxer already exists.
        sqlite3.Error: If database operation fails.
    """
    logger.info(f"Creating boxer: {name}, {weight}lbs, {height}in, reach {reach}, age {age}")
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
                logger.error(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()
            logger.info(f"Boxer '{name}' created successfully")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists (IntegrityError)")
        raise ValueError(f"Boxer with name '{name}' already exists")
    except sqlite3.Error as e:
        logger.error(f"Database error when creating boxer: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """
    Delete a boxer from the database.

    Args:
        boxer_id (int): ID of the boxer to delete.

    Raises:
        ValueError: If boxer not found.
        sqlite3.Error: If database operation fails.
    """
    logger.info(f"Deleting boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")
            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID {boxer_id} deleted successfully")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Get leaderboard of boxers, sorted by win percentage or total wins.

    Args:
        sort_by (str): Sorting method: "wins" or "win_pct".

    Returns:
        List[dict[str, Any]]: List of boxer stats.

    Raises:
        ValueError: If sort_by is invalid.
        sqlite3.Error: If database operation fails.
    """
    logger.info(f"Fetching leaderboard sorted by {sort_by}")
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
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

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

        logger.info(f"Leaderboard fetched: {len(leaderboard)} entries")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error when fetching leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Fetch a boxer by their ID.

    Args:
        boxer_id (int): ID of the boxer.

    Returns:
        Boxer: Boxer object.

    Raises:
        ValueError: If boxer not found.
        sqlite3.Error: If database operation fails.
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
                return Boxer(*row)
            else:
                logger.error(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error when fetching boxer by ID: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Fetch a boxer by their name.

    Args:
        boxer_name (str): Name of the boxer.

    Returns:
        Boxer: Boxer object.

    Raises:
        ValueError: If boxer not found.
        sqlite3.Error: If database operation fails.
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
                return Boxer(*row)
            else:
                logger.error(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error when fetching boxer by name: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    Determine weight class based on weight.

    Args:
        weight (int): Weight of the boxer.

    Returns:
        str: Weight class.

    Raises:
        ValueError: If weight is invalid.
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
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Update the boxer's fight and win stats.

    Args:
        boxer_id (int): ID of the boxer.
        result (str): Result of the match: 'win' or 'loss'.

    Raises:
        ValueError: If result is invalid or boxer not found.
        sqlite3.Error: If database operation fails.
    """
    logger.info(f"Updating boxer ID {boxer_id} with result: {result}")
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer ID {boxer_id} stats updated successfully")

    except sqlite3.Error as e:
        logger.error(f"Database error when updating boxer stats: {e}")
        raise e
