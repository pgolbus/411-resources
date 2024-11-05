from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    """
    A class with a list of meals tracking their id, name. cuisine, price. and difficulty

    Attributes:         
        id (int): id number of Meal
        meal (str): string name of Meal
        cuisine (str): string cuisine
        price (float): a decimal representation of price
        difficulty(str): can either be one of "LOW", "MED", "HIGH" 

    """
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        """
        Returns:
            If price(float) is less than 0, it returns an error that the price is negative
            If difficulty(str) is not one of "LOW", "MED", or "HIGH", return error
        """
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")


def create_meal(meal: str, cuisine: str, price: float, difficulty: str) -> None:
    """
    Creates a meal with all of the given parameters given no errors

    Args:
        meal: a string that resembles what meal name
        cuisine: a string representing cuisine of meal
        price: a float representing decimal price of meal 
        difficulty: a string representing "LOW", "MED", "HIGH" 

    Returns: 
        If no errors from price <= 0, difficulty not correctly listed, 
        no duplicates, and no DB connection errors
        
        If nothing is raised, successfully created meal and added to DB

        sqlite3.Error: If any database error occurs.

    """
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
    if difficulty not in ['LOW', 'MED', 'HIGH']:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """, (meal, cuisine, price, difficulty))
            conn.commit()

            logger.info("Meal successfully added to the database: %s", meal)

    except sqlite3.IntegrityError:
        logger.error("Duplicate meal name: %s", meal)
        raise ValueError(f"Meal with name '{meal}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def clear_meals() -> None:
    """
    Recreates the meals table, effectively deleting all meals.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_meal_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Meals cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing meals: %s", str(e))
        raise e

def delete_meal(meal_id: int) -> None:
    """
    Deletes a meal from the DB and denotes which meal ID was deleted 

    Args:
        meal_id(int): the meal id that each meal is uniquely assigned
    
    Returns: 
        Looks through a DB parsing through table meals such that id = meal_id
            - If it finds the matching id attributes, it will delete otherwise it will say that it has been deleted 
                or that it has already been deleted 
            - If successfully deleted, it will UPDATE the table where it was deleted where id attributes match and commit

        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    """
    Creates a leaderboard by parsing SQL tables and utilizing a win percentage of wins/battles
    then sorts all the wins & pct by descending order then creating a leaderboard with all information with wins

    Args: 
        sort_by: Looks for sort_by as our method of ORDER BY used in our SQL query
        str = "wins" what we would be looking for as our method of comparison between all tuples

    Returns: 
        Returns a leaderboard with strings of Any type
        Looks through all SQL query result tuples where wins are sorted in descending order
            - If there is an error, the parameters will return an error
        Successfully creates a leaderboard and is returned 

        sqlite3.Error: If any database error occurs. 
    """

    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    """
    Parses through the SQL database where we are matching to see if the id in the attributes matches our parameter meal_id

    Args:
        meal_id(int): the meal id that we are looking for within the SQL DB

    Returns: 
        Looks through the DB to find the information based on the parameter meal_id and returns the information of Meal if it is true

        If found, it returns the meal and all its information but if row[5] (whether or not it is deleted) is true, it wil raise an error that it has been deleted from the DB
        Otherwise, it will raise an error that it has not been found throughout the DB
        
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    """
    Looks through DB to search for meal information based on the name of the meal_name(str)

    Args:
        meal_name(str): parameter we use to look for name of meal in DB
        
    Returns: 
        Returns the Meal information given that we can find the name of the meal within the DB

        If found, it returns the meal and all its information but if row[5] (whether or not it is deleted) is true, it wil raise an error that it has been deleted from the DB
        Otherwise, it will raise an error that it has not been found throughout the DB
        
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    """
    Looks to update any Meals given the meal_id and the result of the match we are going to update in the DB attribute column

    Args:
        meal_id(str): The id of the meal that we are looking to make edits or changes to  
        result(str): The string of the result that represents whether or not the result of the watch was a win or loss 
    
    Returns: 
        Makes changes to DB list based off win/loss:
        Raises errors if the meal in the DB is deleted or has not been found
        Executes changes to the wins(int) and battle(int) by adding 1 based off wins or loss
            - Raises error if result(str) is invalid (not 'win' or 'loss')
        
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
