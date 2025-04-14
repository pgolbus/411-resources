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
    """Creates and initializes characteristics for a new boxer.

    Args:
        id (int): The boxer's id.
        name (str): The boxer's name.
        weight (int): The boxer's weight.
        height (int): The boxer's height.
        reach (float): The boxer's reach.
        age (int): The boxer's age.
        weight_class (str): The boxer's weight class.

    Returns:
        None, this is a constructor, so it does not return anything.
    """
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

    """Creates a new boxer in the database after validating the input.

    Args:
        name (str): The boxer's name.
        weight (int): The boxer's weight.
        height (int): The boxer's height.
        reach (float): The boxer's reach.
        age (int): The boxer's age.

    Returns:
        None, this function does not return anything but modifies the database.
    
    Raises:
        ValueError: If the input values are invalid.
        sqlite3.IntegrityError: If a boxer with the same name already exists.
        sqlite3.Error: If there is an error with the database.
    """
    logger.info(f"Attempting to create a boxer:{name}")
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

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Succesfully created boxer: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Integrity error while creating boxer: {name}")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating boxer: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database by their ID.

    Args:
        boxer_id (int): The ID of the boxer to be deleted.

    Returns:
        None, this function does not return anything but modifies the database.

    Raises:
        ValueError: If the boxer with the given ID does not exist.
        sqlite3.Error: If there is an error with the database.
    """
    logger.info(f"Attempting to delete boxer with ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Succesfully deleted boxer with ID: {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Fetches the leaderboard of boxers.

    Args:
        sort_by (str): The sorting of the leaderboard by wins.

    Returns:
        List[dict[str, Any]]: The leaderboard of boxers.

    Raises:
        ValueError: If the sort_by parameter is invalid.
        sqlite3.Error: If there is an error with the database.
    """
    logger.info(f"Fetching leaderboard sorted by: {sort_by}")

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
        logger.info(f"Leaderboard succesfully retrieved")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Fetches a boxer's details from the database by their ID.

    Args:
        boxer_id (int): The boxer's id to retrive.

    Returns:
        Boxer: The boxer.

    Raises:
        ValueError: If no boxer with the given ID is found.
        sqlite3.Error: If there is an error with the database.
    """
    logger.info(f"Fetching boxer with ID: {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Found boxer with ID: {boxer_id}")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching boxer by ID: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Fetches a boxer's details from the database by their name.

    Args:
        boxer_name (str): The boxer's name.

    Returns:
        Boxer: The boxer's name

    Raises:
        ValueError: If no boxer with the given name is found.
        sqlite3.Error: If there is an error with the database.
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
                logger.info(f"Found boxer with name '{boxer_name}'")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching boxer by name: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weight class of a boxer based on their weight.

    Args:
        weight (int): The boxer's weight.

    Returns:
        str: The boxer's weight.

    Raises:
        ValueError: If the weight is less than 125, no valid weight class exists.
    """
    logger.debug(f"Determining weight class for weight: {weight}")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weiight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the statistics for a boxer based on the result of their fight.

    Args:
        boxer_id (int): The boxer's ID.
        result (str): The result of the fight (win/loss).

    Returns:
        None, this function does not return anything but modifies the database.

    Raises:
        ValueError: If the result is not "win" or "loss".
        ValueError: If no boxer with the given ID is found.
        sqlite3.Error: If there is an error with the database.
    """
    logger.info(f"Updating stats for boxer ID {boxer_id} with result '{result}'")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Succesfully updated stats for boxer ID: {boxer_id}")
    except sqlite3.Error as e:
        logger.error(f"Database error while updating stats: {e}")
        raise e
