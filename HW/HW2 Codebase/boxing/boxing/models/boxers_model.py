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
    A class to store and access Boxer attributes."

    Attributes:
        id (int): ID number of the boxer
        name (str): name of the boxer
        weight (int): weight of the boxer
        height (int): height of the boxer
        reach (float): reach of the boxer
        age (int): boxer's age
        weight_class (str): boxer's weight class

    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """
        Initializes a boxer with their weight class assigned. 
        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Initializes a new boxer not currently in the SQL database and inserts them in it.

        Args:
            id (int): ID number of the boxer
            name (str): name of the boxer
            weight (int): weight of the boxer
            height (int): height of the boxer
            reach (float): reach of the boxer
            age (int): boxer's age

        Raises:
            ValueError: If an attribute is does not meet the criteria or if the boxer already exists in the db.

        """
    logger.info("Received request to create new boxer")

    if weight < 125:
        logger.warning("Invalid input data types")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.warning("Invalid input data types")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning("Invalid input data types")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.warning("Invalid input data types")
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
            logger.info(f"Adding boxer: {name}, {weight}kg, {height}cm, {reach} inches, {age} years old")
            logger.info(f"Boxer added successfully: {name}")
            conn.commit()

    except sqlite3.IntegrityError:
        logger.error(f"Failed to add boxer:")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Failed to add boxer:")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the database.

        Args:
            id (int): ID number of the boxer.

        Raises:
            ValueError: If the boxer's ID is not in the database.

        """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves the leaderboard of boxers from the SQL database and sorts them by wins.

        Args:
            sort the database by wins.

        Raises:
            ValueError: If a parameter for sort_by is not possible.

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
    """Retrieves a boxer's stats by ID.

        Args:
            id (int): ID number of the boxer.

        Raises:
            ValueError: If the ID is not in the database.

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
    """Retrieves a boxer's stats by name.

        Args:
            name (str): Name of the boxer.

        Raises:
            ValueError: If the name is not in the database.

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
    """Outputs a weightclass based on an input weight

        Args:
            weight (int): Weight of the boxer.

        Raises:
            ValueError: If the weight is not at least 125.

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
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates stats after a match.

        Args:
            id (int): ID number of the boxer.
            result (str): Result of the boxer's match

        Raises:
            ValueError: Invalid result of a match or if a boxer is not in the database.

        """
    if result not in {'win', 'loss'}:
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
