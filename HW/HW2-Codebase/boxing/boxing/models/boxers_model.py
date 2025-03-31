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
    """
    Creates a new boxer to add to the boxer table.
    Args:
    name(str): The boxer's name.
    weight(str): The boxer's weight.
    height (int): The boxer's height.
    reach float: The boxer's reach
    age (int): boxer's age

    Raises:
    Value error: If any field is invalid.
    sqlite3.IntegrityError: If a boxer with the same name already exists. 
    sqlite3.Error: For any other database errors.

        
    """
    logger.info(f"Recived request to create a boxer: {name}")

    if weight < 125:
        logger.warning("Invalid weight provided.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")

    if height <= 0:
        logger.warning("Invalid height provided.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning("Invalid reach provided.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")

    if not (18 <= age <= 40):
        logger.warning("Invalid age provided.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
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
    """ Permanently deletes a boxer from the table.
    Args:
        boxer_id (int): The ID of the boxer to delete.

        Raises:
        ValueError: If the song with the given ID does not exist.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Attempted to delete non-existent boxer with ID {boxer_id}")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Successfully deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """ Gets a list of the current leaderboard. 
        
    Args:
        sort_by (str): If caller does not provide a value wins will be provided.

    Returns:
        List: A dictionary listing the winners.

    Raises:
        ValueError: If there is a invalid sort_by parameter.
        sqlite3.Error: If any database error occurs.
            
    """
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
        logger.info(f"Leaderboard gets sorted by win_pct")
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
        logger.info(f"Leaderboard gets sorted by wins")

    else:
        logger.info(f"Invalid parameter")
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

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the table by their table.

        Args:
            boxer_id (int): The ID of the boxer to retrieve.

        Returns:
            Boxer: The Boxer object corresponding to the boxer_id.

        Raises:
            ValueError: If the boxer is not found.
            sqlite3.Error: If any database error occurs.

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
                logger.info(f"Boxer with ID {boxer_id} found")
                return boxer
            else:
                logger.info(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer by ID {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrives a boxer from the table by its name.
    Args:
        boxer_name (str): The boxers name.

    Returns: 
        Boxer: The boxer object corresponding to the name.
    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If any database error occurs.
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
                logger.info(f"Boxer with name '{boxer_name}' found")
                return boxer
            else:
                logger.info(f"Boxer with name '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Retrives the weight class of a boxer by its weight

    Args: weight(int): The boxer's weight
    Returns: The weightclass corresponding to the weight
    Raise:
        ValueError: If weight is less than 125
    """
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
        logger.info(f"Weight class is HEAVYWEIGHT")
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
        logger.info(f"Weight class is MIDDLEWEIGHT")
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
        logger.info(f"Weight class is LIGHTWEIGHT")
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
        logger.info(f"Weight class is FEATHERWEIGHT")
    else:
        logger.info(f"Boxer with weight '{weight}' could not be classified.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
"""update the boxer's stats
    Args: boxer_id (int), results(str)
    
    Returns: Does not return a value

    Raise:
        ValueError: If boxer's id cannot be found and if the result is not win or lose
        sqlite3.Error: If any database error occurs.
    """
    if result not in {'win', 'loss'}:
        logger.info(f"Invalid Result")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.info(f"Invalid Boxer ID")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
