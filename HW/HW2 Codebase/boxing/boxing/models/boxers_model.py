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
    """ Creates new boxer in boxer table

    Args: 
        - name (str): The boxer's name.
        - weight (int): The boxer's weight.
        - height (int): The boxer's height. 
        - reach (float): The boxer's reach in inches.
        - age (int): The boxer's age.

    Raises:
        ValueError: If any field is invalid or the boxer already exists.
        sqlite3.IntegrityError: If a boxer with the same name already exists.
        sqlite3.Error: For any other database errors.
    """
    loger.info("Received request to add new boxer")
    
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

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")
        
            logger.info("Adding boxer...")
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info("Successfully added boxer to the table")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """ Permanently deletes a boxer from the boxers table. 

    Args:
        boxer_id (int): The id of the boxer to be deleted

    Raises:
        ValueError: If the boxer with the given ID does not exist.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            logger.info("Deleting boxer...")
            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info("Successfully deleted boxer from the table")

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves a leaderboard of boxers from the database, sorted by wins or win percentage.

    Args:
        sort_by (str): Determines the sorting criterion of the leaderboard, either 'wins' or 'win_pct'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a boxer with their stats and calculated win percentage.

    Raises:
        ValueError: If the 'sort_by' parameter is neither 'wins' nor 'win_pct'.
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
    """ Retrieves a boxer from the table by its associated ID. 

    Args:
        boxer_id (int) : The id of the boxer to be retrieved

    Returns:
        Boxer: The boxer object associated with the inputted id. 

    Raises:
        ValueError: If the song is not found.
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
                return boxer
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the table by its associated name. 

    Args:
        boxer_name (str) : The name of the boxer to be retrieved 

    Returns:
        Boxer: The boxer object associated with the inputted name. 

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
                return boxer
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Returns the weight class associated with a weight

    Args:
        weight (int): a weight value

    Returns:
        str: The weight class the inputted weight falls into 

    Raises:
        ValueError: If the weight inputted is less than 125

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

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the statistics of a boxer based on the fight's result by boxer ID.

    Args:
        boxer_id (int): The ID of the boxer whose stats are to be updated.
        result (str): The fight result, which should be either 'win' or 'loss'.

    Raises:
        ValueError: If the result is neither 'win' nor 'loss', or if no boxer with the specified ID exists.
        sqlite3.Error: If any database error occurs during the update.

    """

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
