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
        # Automatically determine weight class when a Boxer instance is created
        self.weight_class = get_weight_class(self.weight)

def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Create a new boxer and insert them into the database."""
    logger.info(f"Creating boxer: {name}")

    # Validate input fields
    if weight < 125:
        logger.error("Invalid weight")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error("Invalid height")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error("Invalid reach")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error("Invalid age")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.debug("Checking if boxer already exists")
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            logger.debug("Inserting new boxer into database")
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()
            logger.info(f"Boxer '{name}' created successfully")

    except sqlite3.IntegrityError:
        logger.exception("Integrity error when creating boxer")
        raise ValueError(f"Boxer with name '{name}' already exists")
    except sqlite3.Error as e:
        logger.exception("Database error during boxer creation")
        raise e

def delete_boxer(boxer_id: int) -> None:
    """Delete a boxer by ID."""
    logger.info(f"Deleting boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID {boxer_id} deleted")

    except sqlite3.Error as e:
        logger.exception("Error deleting boxer")
        raise e

def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieve a list of boxers sorted by performance."""
    logger.info(f"Retrieving leaderboard sorted by {sort_by}")

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
        logger.error("Invalid sort_by parameter")
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
                'weight_class': get_weight_class(row[2]),
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)
            }
            leaderboard.append(boxer)

        logger.info("Leaderboard retrieval successful")
        return leaderboard

    except sqlite3.Error as e:
        logger.exception("Error retrieving leaderboard")
        raise e

def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieve a boxer by their ID."""
    logger.info(f"Looking up boxer by ID: {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))
            row = cursor.fetchone()

            if row:
                logger.info(f"Found boxer with ID {boxer_id}")
                return Boxer(*row)
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.exception("Error retrieving boxer by ID")
        raise e

def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieve a boxer by their name."""
    logger.info(f"Looking up boxer by name: {boxer_name}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))
            row = cursor.fetchone()

            if row:
                logger.info(f"Found boxer named {boxer_name}")
                return Boxer(*row)
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.exception("Error retrieving boxer by name")
        raise e

def get_weight_class(weight: int) -> str:
    """Determine the weight class based on the given weight."""
    logger.debug(f"Classifying weight: {weight}")
    if weight >= 203:
        return 'HEAVYWEIGHT'
    elif weight >= 166:
        return 'MIDDLEWEIGHT'
    elif weight >= 133:
        return 'LIGHTWEIGHT'
    elif weight >= 125:
        return 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Update a boxer's stats based on fight result."""
    logger.info(f"Updating stats for boxer {boxer_id} with result: {result}")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result type: {result}")
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
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer {boxer_id} stats updated successfully")

    except sqlite3.Error as e:
        logger.exception("Error updating boxer stats")
        raise e
