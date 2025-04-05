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
    """A class to store a boxer's stats.

    Attributes: 
        id (int): Unique numerical ID associated with boxer.
        name (str): The boxer's name.
        weight (int): The weight of the boxer.
        height (int): The height of boxer.
        reach (float): The boxer's reach.
        age (int): The boxer's age.
        weight_class (str): The weight class the boxer falls under.
        
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """ Determines a boxer's weight class.
        
        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer stat for the ring.

    Args:
        name (str): The boxer's name.
        weight (int): The weight of the boxer.
        height (int): The height of boxer.
        reach (float): The boxer's reach.
        age (int): The boxer's age.

    Raises: 
        ValueError: If any field is empty/invalid.
        sqlite3.IntegrityError: If a boxer with the same 'name' already exists.
        sqlite3.Error: For any other database errors.

    """

    logger.info(f"Request received to create boxer {name}.")

    if weight < 125:
        logger.warning("Invalid weight provided.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.warning("Invalid height provided.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning("Invalid reach provided,")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.warning("Invalid age provided.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempt to create boxer {name}.")
            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning("Invalid name: boxer already exists.")
                raise ValueError(f"Boxer with name '{name}' already exists.")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

            logger.info(f"Successfully created boxer {name}.")

    except sqlite3.IntegrityError:
        logger.error("Boxer already exists.")
        raise ValueError(f"Boxer with name '{name}' already exists.")

    except sqlite3.Error as e:
        logger.error(f"Database error when creating boxer: {e}")
        raise sqlite3.Error(f"Database error: {e}")


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the ring using boxer_id.

    Args: 
        boxer_id (int): The numerical ID of the boxer to retrieve. 

    Raises: 
        ValueError: If boxer with boxer_id does not exist.
        sqlite3.Error: Any other database error.

    """
    logger.info("Request received to delete boxer.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempt to delete boxer.")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))

            if cursor.fetchone() is None:
                logger.warning(f"Attempted to delete non-existent boxer with with ID {boxer_id}.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Successfully deleted boxer with ID {boxer_id}")
            
    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer with ID {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Returns the boxer leaderboard by wins.

    Args:
        sort_by (str): Key to sort the boxers by.

    Returns:
        List[dict[str, Any]]: A list of dictionaries, with each dictionary containing a boxer's stats.

    Raises:
        ValueError: If sorting key is not 'wins' or 'win_pct'.
        sqlite3.Error: If any other database error occurs.

    """
    logger.info(f"Request received to return leaderboard sorted by {sort_by}.")

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
        logger.warning("Sort_by parameter is invalid.")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to create leaderboard of boxers sorted by {sort_by}.")
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
        logger.info(f"Successfully created boxer leaderboard sorted by {sort_by}.")

        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error when creating leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Returns boxer and their stats by boxer_id.

    Args:
        boxer_id (int): The numerical ID of the boxer to retrieve. 

    Returns: 
        Boxer: The Boxer object associated with boxer_id, which contains their stats.

    Raises: 
        ValueError: If the boxer is not found.
        sqlite3.Error: If any other database error occurs.

    """
    logger.info(f"Request received to retrieve boxer with ID {boxer_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer by ID {boxer_id}.")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with ID {boxer_id} is found.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully found boxer using ID {boxer_id}.")
                return boxer
            else:
                logger.warning(f"Boxer is not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer by ID {boxer_id}: {e}.")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer's stats by their name.

    Args:
        boxer_name (str): The name of boxer.

    Returns:
        Boxer: The Boxer object associated with the boxer, which contains their stats.

    Raises:
        ValueError: If a boxer is not found.
        sqlite3.Error: If any other database error occurs.
    
    """
    logger.info(f"Request received to retrive boxer with name {boxer_name}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer with name {boxer_name}.")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Successfully found boxer {boxer_name}.")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.warning(f"Boxer with name {boxer_name} is not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer by ID {boxer_name}: {e}.")
        raise e


def get_weight_class(weight: int) -> str:
    """Identifies the weight class the given weight falls under.

    Args:
        weight (int): The weight of boxer.

    Returns: 
        str: The weight class.

    Raises:
        ValueError: If input weight is invalid.

    """
    logger.info("Attempt to classify weight class")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.warning("Input weight is invalid.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info("Successfully classified weight class")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Identfies a boxer using their boxer_id and updates their stats based on new results.

    Args:
        boxer_id (int): The numerical ID of the boxer to retrieve. 
        result (str): The result of a boxer's fight ('win', 'loss')

    Raises:
        ValueError: If the result is invalid.
         ValueError: If the boxer is not found.
        sqlite3.Error: If any other database error occurs.

    """
    if result not in {'win', 'loss'}:
        logger.warning("Result is invalid")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")
    
    logger.info("Request received to update a boxer's stats.")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer by ID {boxer_id}.")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer is not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                logger.info("Attempt to update boxer stats.")
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                logger.info("Attempt to update boxer stats.")
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info("Successfully updated boxer stats.")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer stats: {e}.")
        raise e
