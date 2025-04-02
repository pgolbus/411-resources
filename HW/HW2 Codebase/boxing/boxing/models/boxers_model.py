"""Boxer management module for handling boxer creation, deletion, retrieval, and updates."""

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
    """Represents a boxer with physical attributes and a weight class."""

    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Automatically assigns a weight class based on weight."""
        self.weight_class = get_weight_class(self.weight)


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates and inserts a new boxer into the database after validation.

    Args:
        name (str): Name of the boxer.
        weight (int): Weight of the boxer in pounds.
        height (int): Height of the boxer in inches.
        reach (float): Reach of the boxer in inches.
        age (int): Age of the boxer.

    Raises:
        ValueError: If input values are invalid or the boxer already exists.
        sqlite3.Error: If a database error occurs.
    """
    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

    except sqlite3.IntegrityError:
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database by ID.

    Args:
        boxer_id (int): Unique ID of the boxer to delete.

    Raises:
        ValueError: If the boxer does not exist.
        sqlite3.Error: If a database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves a sorted leaderboard of boxers with recorded fights.

    Args:
        sort_by (str): Sorting criterion, either 'wins' or 'win_pct'. Defaults to 'wins'.

    Returns:
        List[dict[str, Any]]: List of boxer stats dictionaries sorted by the given criterion.

    Raises:
        ValueError: If an invalid sort_by parameter is provided.
        sqlite3.Error: If a database error occurs.
    """
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

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the database using their ID.

    Args:
        boxer_id (int): Unique ID of the boxer.

    Returns:
        Boxer: The Boxer object with the specified ID.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If a database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                return Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the database using their name.

    Args:
        boxer_name (str): Name of the boxer.

    Returns:
        Boxer: The Boxer object with the specified name.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If a database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                return Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weight class of a boxer based on their weight.

    Args:
        weight (int): Weight of the boxer in pounds.

    Returns:
        str: The corresponding weight class.

    Raises:
        ValueError: If the weight is below the minimum threshold.
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
    """Updates the stats of a boxer after a match result.

    Args:
        boxer_id (int): Unique ID of the boxer.
        result (str): Result of the fight, either 'win' or 'loss'.

    Raises:
        ValueError: If the result is invalid or the boxer does not exist.
        sqlite3.Error: If a database error occurs.
    """
    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
