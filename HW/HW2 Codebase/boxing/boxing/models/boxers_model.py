"""Boxer management module for handling boxer creation, deletion, retrieval, and updates."""

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
    """Represents a boxer with physical attributes and a weight class."""

    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Automatically assigns a weight class based on weight."""
        self.weight_class = get_weight_class(self.weight)
        logger.debug(f"Assigned weight class '{self.weight_class}' to boxer '{self.name}'")


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    logger.info(f"Attempting to create boxer: {name}")

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

            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Successfully created boxer '{name}'")

    except sqlite3.IntegrityError:
        logger.exception(f"IntegrityError: Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.exception("Database error occurred while creating boxer")
        raise e


def delete_boxer(boxer_id: int) -> None:
    logger.info(f"Attempting to delete boxer with ID {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.exception("Database error occurred while deleting boxer")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
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
                'weight_class': get_weight_class(row[2]),
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)
            }
            leaderboard.append(boxer)

        logger.info("Leaderboard fetched successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.exception("Database error occurred while fetching leaderboard")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    logger.info(f"Fetching boxer with ID {boxer_id}")
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
                return Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.exception("Database error occurred while fetching boxer by ID")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
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
                logger.info(f"Found boxer '{boxer_name}'")
                return Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.exception("Database error occurred while fetching boxer by name")
        raise e


def get_weight_class(weight: int) -> str:
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
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Successfully updated stats for boxer ID {boxer_id}")

    except sqlite3.Error as e:
        logger.exception("Database error occurred while updating boxer stats")
        raise e
