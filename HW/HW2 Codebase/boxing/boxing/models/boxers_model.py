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
    """Creates a new boxer in the database with the given information.
    
    Args:
        name (str): The name of the boxer. Must have a unique name.
        weight (int): The weight of the boxer. Must be greater than 125 pounds.
        height (int): The height of the boxer in inches. Must be greater than 0 inches.
        reach (float): The reach of the boxer in inches. Must be greater than 0 inches.
        age (int): The age of the boxer. Must be between 18 years old and 40 years old inclusive.
        
    Raises:
        ValueError: The weight is not at least 125 pounds.
        ValueError: The height is not greater than 0 inches.
        ValueError: The reach is not greather than 0 inches.
        ValueError: The age is not in between 18 years old and 40 years old inclusive.
        ValueError: There is a boxer already with the same name and it already exists.
        IntegrityError: Multiple of the same named boxers are inserted.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    logger.info(f"Received request to create a Boxer")
    
    logger.info(f"Comparing args to requirements")
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
        logger.info(f"attempting to connect to database")
        with get_db_connection() as conn:
            cursor = conn.cursor()

            logger.info(f"Connected to database.")
            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            logger.info(f"Creating boxer in the database.")
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Boxer '{name}' created.")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database based on the given boxer ID.
    
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        
    Raises:
        ValueError: Boxer ID was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    logger.info(f"Request to delete Boxer: {boxer_id}")
    try:
        logger.info(f"Attemping to connect to database.")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Connected to database.")

            logger.info(f"Searching for Boxer with ID: {boxer_id}")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            logger.info(f"attempting to delete boxer from database")
            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Deleted boxer: {boxer_id} from database")

    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retreieves a list of boxers from the data base sorted by win percentage or wins if the boxer has at least one match.
    
    Args:
        sort_by (str): Default set to "wins", selects whether the leaderboard is sorted by wins or win percentage based on if equal to "wins" or "win_pct".
        
    Raises:
        ValueError: If sort_by is not set to either "win_pct" or "wins".
        Error: If any connection failure to database occurs.
        
    Returns: 
        leaderboard (list): A list of dictionaries of boxers sorted by win percentage or total wins.
          
    """
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """
    logger.info(f"Request to create leaderboard received sorted by {sort_by}")

    
    if sort_by == "win_pct":
        logger.info(f"Valid sort_by parameter. Sorted by {sort_by}")
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        logger.info(f"Valid sort_by parameter. Sorted by {sort_by}")
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        logger.info(f"Attempting to connect to database")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            logger.info(f"Successfully connected to database and retrieved rows from database")

        logger.info(f"Creating leaderboard list")
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
            logger.info(f"Sucesfully added {boxer['name']} to leaderboard}")
        
        logger.info(f"Sucesfully created leaderboard list")
        
        return leaderboard
        logger.info(f"leaderboard successfully returned")
        
    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Searches the database for a boxers information given Boxers ID and returns a Boxer object.
    
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        
    Raises:
        ValueError: boxer ID was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Boxer (object): A Boxer object with the given boxer_id.
        
    """
    logger.info(f"Received request to search database for boxer {boxer_id}")
    
    try:
        logger.info(f"Attempting to connect to database")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()
            logger.info(f"Successfully connected to database and retreived boxer information based on {boxer_id}")

            logger.info(f"Attemping to access information")
            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully accessed boxer id, name, weight, height, reach, and age and assigned it to boxer")
                return boxer
                logger.info(f"Successfully returned boxer {boxer_id}")
                
            else:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Searches the database for a str that matches boxer_name and returns a Boxer object.
        
    Args:
        boxer_name (str): The unique name of a boxer.
        
    Raises:
        ValueError: Boxer name was not found in the fetch.
        Error: If any connection failure to database occurs.
        
    Returns:
        Boxer (object): A Boxer object with the given boxer_name.
        
    """
    logger.info(f"Received request to search database for boxer {boxer_name}")
    try:
        logger.info(f"Attempting to connect to database")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()
            logger.info(f"Successfully connected to database and retreived boxer information based on {boxer_name}")

            logger.info(f"Attemping to access information")
            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully accessed boxer id, name, weight, height, reach, and age and assigned it to boxer")
                return boxer
                logger.info(f"Successfully returned boxer {boxer_name}")
                
            else:
                logger.error(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weightclass of given integer.

    Args:
        weight (int): The int the function is comparing. Must be greater than 125 pounds. Represents weigth of boxer.
        
    Raises:
        ValueError: weight was not at least 125.
        
    Returns:
        weight_class (str): returns 'HEAVYWEIGHT','MIDDLEWEIGHT','LIGHTWEIGHT','FEATHERWEIGHT' based on the range varible weight is in.
        
    """
    logger.info(f"Received request to get weight class of given integer {weight}")
    
    logger.info(f"Assigning weightclass based on {weight}")
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
        logger.info(f"Successfully assigned weightclass {weight_class} based on {weight}")
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
        logger.info(f"Successfully assigned weightclass {weight_class} based on {weight}")
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
        logger.info(f"Successfully assigned weightclass {weight_class} based on {weight}")
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
        logger.info(f"Successfully assigned weightclass {weight_class} based on {weight}")
    else:
        logger.error(f"Invalid weight: {weight}. Weight must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
        
    return weight_class
    logger.info(f"Successfully returned weight_class {weight_class}")


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the number of fights a boxer with the given boxer_id has completed and updates the number of wins based on result in the database.
        
    Args:
        boxer_id (int): A ID associated with a boxer's information in the database.
        result (str): The result of a boxers match. Must be 'win' or 'loss.
        
    Raises:
        ValueError: result(str) is not equal to 'win' or 'loss'.
        ValueError: Boxer with the given ID was not found.
        Error: If any connection failure to database occurs.
        
    Returns:
        Nothing.
        
    """
    logger.info(f"Successfully received request to update boxer stats in database")

    logger.info(f"Checking is {result} is valid argument")
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    logger.info(f"Attempting to connect to database")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Successfully connected to database")

            logger.info(f"Searching database for boxer {boxer_id}")
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")
            logger.info(f"Boxer {boxer_id} found")

            logger.info(f"Updating boxer {fights} and {wins} based on {result}")
            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Boxer won, Successfully updated boxer fights to {fights} and wins to {wins}")
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Boxer lost, Successfully updated boxer fights to {fights}")

            conn.commit()
            logger.info(f"Successfully uploaded to database")

    except sqlite3.Error as e:
        logger.error(f"Faulty database connection: {str(e)}")
        raise e
