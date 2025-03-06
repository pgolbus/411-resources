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
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Create a new Boxer and add it to the boxers table.

    Args:
        name (str): The boxer's name.
        weight (int): The boxer's weight (must be > 0).
        height (int): The boxer's height (must be > 0).
        reach (float): The boxer's reach (must be > 0).
        age (int): The boxer's age (must be between 18 and 40, inclusive).

    Raises:
        ValueError: If any of the properties are invalid.
        ValueError: If a boxer with the same name already exists.
        sqlite3.Error: If any other database error occurs.

    """
    logger.info(f"Initiating boxer creation: name={name}, weight={weight}, height={height}, reach={reach}, age={age}")

    if weight < 125:
        logger.error(f"Validation failed: Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Validation failed: Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Validation failed: Invalid reach: {reach}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Validation failed: Invalid age: {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Duplicate boxer name: {name}")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Boxer successfully added to the database: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Duplicate boxer name: {name}")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e

def delete_boxer(boxer_id: int) -> None:
    """Permanently deletes a boxer from the boxers table.

    Args:
        boxer_id (int): The ID of the boxer to delete.

    Raises:
        ValueError: If the boxer with the given ID does not exist.
        sqlite3.Error: If there's a database error.

    """
    logger.info(f"Initiating permanent deletion of boxer with ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Boxer with ID {boxer_id} permanently deleted.")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer {boxer_id}: {e}")
        raise e

def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieve the leaderboard of boxers.

    Retrieves the leaderboard of boxers, sorted either by the number of wins
    (default) or by win percentage (wins / fights). Returns a list of boxers
    with relevant statistics such as fights, wins, and win percentage.

    Args:
        sort_by (str): Specifies how to sort the leaderboard.
                       - "wins": Sort by the number of wins (default).
                       - "win_pct": Sort by win percentage (wins / fights).

    Returns:
        List[dict]: A list of dictionaries where each dictionary represents a boxer.
                    The boxer data includes:
                    - id (int): The boxer's unique ID.
                    - name (str): The name of the boxer.
                    - weight (int): The weight of the boxer.
                    - height (int): The height of the boxer.
                    - reach (float): The reach of the boxer.
                    - age (int): The age of the boxer.
                    - weight_class (str): The calculated weight class.
                    - fights (int): The number of fights the boxer has participated in.
                    - wins (int): The number of fights the boxer has won.
                    - win_pct (float): The win percentage.

    Raises:
        ValueError: If the sort_by parameter is invalid.
        sqlite3.Error: If there is a database error during query execution.

    """
    logger.info(f"Retrieving leaderboard. Sort by: {sort_by}")

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
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info("Leaderboard retrieved successfully.")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e

def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: A Boxer dataclass containing the boxer data.

    Raises:
        sqlite3.Error: If there's a database error.
        ValueError: If the boxer with the given ID is not found.

    """
    logger.info(f"Retrieving boxer by ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrieved boxer: {boxer.name} (ID: {boxer.id})")
                return boxer
            else:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer {boxer_id}: {e}")
        raise e

def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the database by their name.

    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: A Boxer dataclass containing the boxer data.

    Raises:
        sqlite3.Error: If there's a database error.
        ValueError: If the boxer with the given name is not found.

    """
    logger.info(f"Retrieving boxer by name: {boxer_name}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrly retrieved boxer: {boxer.name} (ID: {boxer.id})")
                return boxer
            else:
                logger.info(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer '{boxer_name}': {e}")
        raise e

def get_weight_class(weight: int) -> str:
    """Determine the weight class based on the given weight.

    Args:
        weight (int): The weight of the boxer.

    Returns:
        str: The weight class of the boxer.

    Raises:
        ValueError: If the weight is less than 125.

    """
    logger.info(f"Determining weight class for weight: {weight}")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Weight must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info(f"Assigned weight class: {weight_class} for weight: {weight}")
    return weight_class

def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates a boxer's stats by incrementing the number of fights

    Updates a boxer's stats by incrementing the number of fights,
    and optionally incrementing the number of wins if the result is 'win'.

    Args:
        boxer_id (int): The ID of the boxer to update.
        result (str): Either 'win' or 'loss' to update the stats.

    Raises:
        ValueError: If the boxer with the given ID does not exist.
        ValueError: If result is not 'win' or 'loss'.
        sqlite3.Error: If there's a database error.

    """
    logger.info(f"Updating boxer stats: boxer_id={boxer_id}, result={result}")

    if result not in {'win', 'loss'}:
        logger.error(f"Validation failed: Invalid result '{result}'. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer stats updated: boxer_id={boxer_id}, result={result}")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer {boxer_id}: {e}")
        raise e
