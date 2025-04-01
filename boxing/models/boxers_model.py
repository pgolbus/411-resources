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
    """
    A class to represent a boxer in the fight.

    Attributes:
        id (int): The unique ID of the boxer.
        name (str): The name of the boxer (must be unique).
        weight (int): The weight of the boxer in pounds (must be >= 125).
        height (int): The height of the boxer in inches (must be > 0).
        reach (float): The reach of the boxer in inches (must be > 0).
        age (int): The age of the boxer (must be between 18 and 40).
        weight_class (str, optional): The automatically assigned weight class based on weight.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Assigns a weight class to the boxer based on their weight."""
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


##################################################
# Boxer Creation / Deletion
##################################################

def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer and adds them to the database.

    Args:
        name (str): The unique name of the boxer.
        weight (int): The weight of the boxer in pounds (must be >= 125).
        height (int): The height of the boxer in inches (must be > 0).
        reach (float): The reach of the boxer in inches (must be > 0).
        age (int): The age of the boxer (must be between 18 and 40).

    Raises:
        ValueError: If any argument is invalid or if a boxer with the same name already exists.
        sqlite3.Error: If a database error occurs.
    """
    
    logger.info(f"Received request to create boxer: {name}")

    if weight < 125:
        logger.error(f"Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid reach: {reach}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age: {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Checking for existing boxer with name '{name}'")

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            logger.info(f"Inserting boxer '{name}' into the database")
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

            logger.info(f"Successfully created boxer: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Integrity error: Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating boxer '{name}': {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database by their unique ID.

    Looks up the boxer in the database using the provided ID. If the boxer exists,
    deletes their record from the 'boxers' table.

    Args:
        boxer_id (int): The ID of the boxer to delete.

    Raises:
        ValueError: If no boxer with the given ID exists.
        sqlite3.Error: If a database error occurs during deletion.
    """

    logger.info(f"Received request to delete boxer with ID {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            logger.info(f"Checking if boxer with ID {boxer_id} exists in the database")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            logger.info(f"Deleting boxer with ID {boxer_id}")
            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Successfully deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer with ID {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves a list of all boxers with at least one fight, sorted by performance.

    Queries the database for boxers who have participated in at least one fight
    and returns a leaderboard sorted by either total wins or win percentage.

    Args:
        sort_by (str, optional): The field to sort by. Must be either 'wins' or 'win_pct'.
        Defaults to 'wins'.

    Returns:
        List[dict[str, Any]]: A list of dictionaries, each representing a boxer and their stats,
        including win percentage and calculated weight class.

    Raises:
        ValueError: If the 'sort_by' parameter is not 'wins' or 'win_pct'.
        sqlite3.Error: If a database error occurs during the query.
    """

    logger.info(f"Generating leaderboard sorted by: {sort_by}")

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
        logger.info(f"Generating leaderboard sorted by: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            logger.info("Executing leaderboard query...")
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        logger.info(f"Retrieved {len(rows)} boxers from the database")

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

        logger.info("Successfully built leaderboard")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the database based on their ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: A `Boxer` object representing the retrieved boxer.

    Raises:
        ValueError: If a boxer with the given ID is not found.
        sqlite3.Error: If there is an error during database operation.
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
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully boxer by id: {boxer.id} - {boxer.name} ({boxer.age} years, {boxer.weight} pounds, {boxer.height} inches, {boxer.reach} inches)")
                return boxer
            else:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while getting boxer by id: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the database based on their name.

    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: A `Boxer` object representing the retrieved boxer.

    Raises:
        ValueError: If a boxer with the given name is not found.
        sqlite3.Error: If there is an error during database operation.
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
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully boxer by name: {boxer.id} - {boxer.name} ({boxer.age} years, {boxer.weight} pounds, {boxer.height} inches, {boxer.reach} inches)")
                return boxer
            else:
                logger.error(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while getting boxer by name: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weight class of a boxer based on their weight.

    Args:
        weight (int): The weight of the boxer in pounds.

    Returns:
        str: The weight class of the boxer (HEAVYWEIGHT, MIDDLEWEIGHT, LIGHTWEIGHT, FEATHERWEIGHT).

    Raises:
        ValueError: If the provided weight is invalid (must be at least 125).
    """
    
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

    logger.info(f"Weight class of {weight} is {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the fight statistics (fights and wins) for a boxer.

    Args:
        boxer_id (int): The ID of the boxer to update.
        result (str): The result of the fight ('win' or 'loss').

    Raises:
        ValueError: If the `result` is invalid or if a boxer with the given ID is not found.
        sqlite3.Error: If there is an error during database operation.
    """
    
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"boxer with {boxer_id}'s status has been updated to {result}")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer status: {e}")
        raise e
