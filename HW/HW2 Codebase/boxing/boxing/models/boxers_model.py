"""
Module for managing boxer records.

This module defines the Boxer dataclass and provides functions to create, delete, retrieve,
and update boxer records in a SQLite database. All operations are performed with input validation,
appropriate error handling, and detailed logging.
"""

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
    """Data class representing a boxer.

    Attributes:
        id (int): Unique identifier for the boxer.
        name (str): The name of the boxer.
        weight (int): The weight of the boxer.
        height (int): The height of the boxer.
        reach (float): The reach of the boxer.
        age (int): The age of the boxer.
        weight_class (str, optional): The weight class determined from the boxer's weight.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Automatically assign the appropriate weight class based on the boxer's weight."""
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer record in the database.

    Validates the input parameters and inserts a new boxer into the database.
    The name must be unique and all parameters must meet specific criteria:
      - weight must be at least 125,
      - height must be greater than 0,
      - reach must be greater than 0,
      - age must be between 18 and 40.

    Args:
        name (str): The unique name of the boxer.
        weight (int): The weight of the boxer.
        height (int): The height of the boxer.
        reach (float): The reach of the boxer.
        age (int): The age of the boxer.

    Raises:
        ValueError: If any parameter fails validation or if a boxer with the given name already exists.
        sqlite3.Error: If a database error occurs during insertion.
    """
    logger.info(f"Initiating creation of boxer '{name}' with weight={weight}, height={height}, reach={reach}, age={age}")

    if weight < 125:
        logger.error(f"Creation failed: Invalid weight {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Creation failed: Invalid height {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Creation failed: Invalid reach {reach}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Creation failed: Invalid age {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug(f"Checking for existing boxer with name '{name}'.")

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Creation failed: Boxer with name '{name}' already exists.")
                raise ValueError(f"Boxer with name '{name}' already exists")

            logger.debug("Inserting new boxer record into the database.")
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()
            logger.info(f"Boxer '{name}' created successfully.")

    except sqlite3.IntegrityError as ie:
        logger.error(f"Database integrity error during creation of boxer '{name}': {ie}")
        raise ValueError(f"Boxer with name '{name}' already exists") from ie

    except sqlite3.Error as e:
        logger.error(f"Database error during creation of boxer '{name}': {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer record from the database based on the provided ID.

    Args:
        boxer_id (int): The unique identifier of the boxer to be deleted.

    Raises:
        ValueError: If no boxer is found with the provided ID.
        sqlite3.Error: If a database error occurs during deletion.
    """
    logger.info(f"Initiating deletion of boxer with ID {boxer_id}.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug(f"Verifying existence of boxer with ID {boxer_id}.")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Deletion failed: Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            logger.debug(f"Deleting boxer with ID {boxer_id}.")
            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID {boxer_id} deleted successfully.")

    except sqlite3.Error as e:
        logger.error(f"Database error during deletion of boxer with ID {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves a leaderboard of boxers sorted by wins or win percentage.

    Only boxers with at least one fight are included. The win percentage is calculated
    as (wins / fights) and converted to a percentage value.

    Args:
        sort_by (str, optional): The sorting criterion for the leaderboard.
            Accepted values are "wins" (default) or "win_pct". 

    Returns:
        List[dict[str, Any]]: A list of dictionaries, each representing a boxer with details
            including id, name, weight, height, reach, age, weight_class, fights, wins, and win_pct.

    Raises:
        ValueError: If an invalid sort_by parameter is provided.
        sqlite3.Error: If a database error occurs during retrieval.
    """
    logger.info(f"Retrieving leaderboard sorted by '{sort_by}'.")
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
        logger.error(f"Invalid leaderboard sort parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug("Executing leaderboard query.")
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
        logger.info(f"Leaderboard retrieval successful. {len(leaderboard)} boxers found.")

        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error during leaderboard retrieval: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer record by its unique ID.

    Args:
        boxer_id (int): The unique identifier of the boxer.

    Returns:
        Boxer: An instance of the Boxer dataclass with the boxer's details.

    Raises:
        ValueError: If no boxer is found with the provided ID.
        sqlite3.Error: If a database error occurs during retrieval.
    """
    logger.info(f"Retrieving boxer with ID {boxer_id}.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug(f"Executing query to get boxer with ID {boxer_id}.")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.debug(f"Boxer with ID {boxer_id} found.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error during retrieval of boxer with ID {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer record by their unique name.

    Args:
        boxer_name (str): The name of the boxer.

    Returns:
        Boxer: An instance of the Boxer dataclass with the boxer's input.

    Raises:
        ValueError: If no boxer is found with the provided name.
        sqlite3.Error: If a database error occurs during retrieval.
    """
    logger.info(f"Retrieving boxer with name '{boxer_name}'.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug(f"Executing query to get boxer with name '{boxer_name}'.")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.debug(f"Boxer '{boxer_name}' found.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.error(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error during retrieval of boxer '{boxer_name}': {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weight class for a given boxers weight.

    Args:
        weight (int): The weight of the boxer.

    Returns:
        str: The corresponding weight class.

    Raises:
        ValueError: If the weight is below the minimum valid value of 125.
    """
    logger.debug(f"Determining weight class for weight {weight}.")
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

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates a boxer's fight stats based on the match results.

    Args:
        boxer_id (int): The unique identifier of the boxer.
        result (str): The result of the fight, either 'win' or 'loss'.

    Raises:
        ValueError: If an invalid result is provided or if no boxer is found.
        sqlite3.Error: If a database error occurs.
    """
    logger.info(f"Updating stats for boxer with ID {boxer_id}, result: {result}.")
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid fight result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            logger.debug(f"Verifying existence of boxer with ID {boxer_id}.")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                logger.debug("Incrementing fights and wins count.")
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                logger.debug("Incrementing fights count.")
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Stats updated successfully for boxer with ID {boxer_id}.")

    except sqlite3.Error as e:
        logger.error(f"Database error during stats update for boxer with ID {boxer_id}: {e}")
        raise e

