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
    This class represents a boxer  with a unique string id, name, weight, height, reach, age and weight class
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """automatically assigns a weight class depending on the weight"""
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class
        logger.info(f"boxer created with: {self.name}, Weight: {self.weight}, Class: {self.weight_class}")


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:

    """
    this creates a new boxer in the database.

    Parameters: 
        name(str): the name of the boxer
        weight(int): the weight of  the boxer in lbs
        height(int): height of the boxer in inches
        reach(float): reach of the boxer in inches
        age(int): age of the boxer in years

    Raises:
        ValueError if weight<125, height<=0, reach<=0, age<18 or age>40
    """

    if weight < 125:
        logger.error("Invalid boxer attributes")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error("Invalid boxer attributes")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error("Invalid boxer attributes")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error("Invalid boxer attributes")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists.")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Boxer '{name}' successfully added to the database.")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"error while creating boxer: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """
    deletes a boxer from the database through  their boxer id
    Parameters:
            boxer_id(int): the ID of the boxer
            
    Raises: 
            ValueError if the boxer wwith given  id is not found
    """
    logger.info(f"Deleting boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer ID {boxer_id} deleted.")

    except sqlite3.Error as e:
        logger.error(f"Error deleting boxer ID {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    retrieves the leaderboard depending on the sorting condition given
    
    Parameters:
        sort_by(str): must be either "win_pct" or "wins" but the default is "wins"
        
    Returns:
        List[dict[str, Any]]: A list of dictionaries which shows the leaderboard
        
    Raises: 
        ValueError if the sort_by parameter is not "wins" or "wins_pct"
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
        
        logger.info("Leaderboard fetched successfully.")

        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    retrieves a boxer based  on the id given

    Parameters:
        boxer_id(int): the id of the boxer
    Returns: 
        the boxer object with the given id and all other attributes

    Raises: 
        ValueError if the boxer with the given id is not found
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
    """
    retrieves the boxer based on the name given

    Parameters:
        boxer_name(str): the name of the boxer
    
    Returns: 
        the boxer object with the given name and all other attributes

    Raises:
        ValueError if the boxer with the given name is not found


    """
    logger.info(f"Fetching boxer with name: {boxer_name}")
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
                logger.info(f"Boxer found: {boxer.name}")
                return boxer
            else:
                logger.warning(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching boxer '{boxer_name}': {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    retrieves the weight class based on  the given weight
    
    Parameters:
        weight(int): the  weight of the boxer
    Returns:
        str: the weight class of the boxer
    Raises:
        ValueError if the weight is less than 125"""
    
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

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    updates the stats(if they win or lose) depending on the given id
    
    Parameters:
        boxer_id(int): the id of the boxer
        result(str): the result  which can either be "win" or "loss"
        
    Raises:
        ValueError if result is not "win" or "loss" or if the boxer with the given id is not found
    
    """
    if result not in {'win', 'loss'}:
        logger.error("Invalid result type")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer ID {boxer_id} stats updated.")

    except sqlite3.Error as e:
        logger.error(f"there was an error updating boxer ID {boxer_id}: {e}")
        raise e
