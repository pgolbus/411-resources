import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from boxing.db import db
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Boxers(db.Model):
    """Represents a competitive boxer in the system.

    This model maps to the 'boxers' table in the database and stores personal
    and performance-related attributes such as name, weight, height, reach,
    age, and fight statistics. Used in a Flask-SQLAlchemy application to
    manage boxer data, run simulations, and track fight outcomes.

    """

    __tablename__ = 'boxers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    reach = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    fights = db.Column(db.Integer, nullable=False, default=0)
    wins = db.Column(db.Integer, nullable=False, default=0)
    weight_class = db.Column(db.String)

    def __init__(self, name: str, weight: float, height: float, reach: float, age: int):
        """Initialize a new Boxer instance with basic attributes.

        Args:
            name (str): The boxer's name. Must be unique.
            weight (float): The boxer's weight in pounds. Must be at least 125.
            height (float): The boxer's height in inches. Must be greater than 0.
            reach (float): The boxer's reach in inches. Must be greater than 0.
            age (int): The boxer's age. Must be between 18 and 40, inclusive.

        Notes:
            - The boxer's weight class is automatically assigned based on weight.
            - Fight statistics (`fights` and `wins`) are initialized to 0 by default in the database schema.

        """
        if weight < 125:
            raise ValueError("Weight must be at least 125 pounds.")
        if height <= 0:
            raise ValueError("Height must be greater than 0 inches.")
        if reach <= 0:
            raise ValueError("Reach must be greater than 0 inches.")
        if not (18 <= age <= 40):
            raise ValueError("Age must be between 18 and 40, inclusive.")

        self.name = name
        self.weight = weight
        self.height = height
        self.reach = reach
        self.age = age
        self.weight_class = self.get_weight_class(weight)
        self.fights = 0
        self.wins = 0

    @classmethod
    def get_weight_class(cls, weight: float) -> str:
        """Determine the weight class based on weight.

        This method is defined as a class method rather than a static method,
        even though it does not currently require access to the class object.
        Both @staticmethod and @classmethod would be valid choices in this context;
        however, using @classmethod makes it easier to support subclass-specific
        behavior or logic overrides in the future.

        Args:
            weight: The weight of the boxer.

        Returns:
            str: The weight class of the boxer.

        Raises:
            ValueError: If the weight is less than 125.

        """
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

    @classmethod
    def create_boxer(cls, name: str, weight: float, height: float, reach: float, age: int) -> None:
        """Create and persist a new Boxer instance.

        Args:
            name: The name of the boxer.
            weight: The weight of the boxer.
            height: The height of the boxer.
            reach: The reach of the boxer.
            age: The age of the boxer.

        Raises:
            IntegrityError: If a boxer with the same name already exists.
            ValueError: If the weight is less than 125 or if any of the input parameters are invalid.
            SQLAlchemyError: If there is a database error during creation.

        """
        logger.info(f"Creating boxer: {name}, {weight=} {height=} {reach=} {age=}")

        try:
            logger.info(f"Boxer created successfully: {name}")
        except IntegrityError:
            logger.error(f"Boxer with name '{name}' already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during creation: {e}")


        logger.info(f"Creating boxer: {name}, {weight=} {height=} {reach=} {age=}")

        if not all([name, weight >= 125, height > 0, reach > 0, 18 <= age <= 40]):
            raise ValueError("Invalid boxer parameters")

        try:
            boxer = cls(name=name, weight=weight, height=height, reach=reach, age=age)
            db.session.add(boxer)
            db.session.commit()
            logger.info(f"Boxer created successfully: {name}")
            return boxer
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Boxer with name '{name}' already exists.")
            raise ValueError(f"Boxer with name '{name}' already exists")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during creation: {e}")
            raise ValueError(f"Database error: {e}")

    @classmethod
    def get_boxer_by_id(cls, boxer_id: int) -> "Boxers":
        """Retrieve a boxer by ID.

        Args:
            boxer_id: The ID of the boxer.

        Returns:
            Boxer: The boxer instance.

        Raises:
            ValueError: If the boxer with the given ID does not exist.

        """
        logger.info(f"Attempting to retrieve boxer with ID {boxer_id}")
        try:
            boxer = cls.query.get(boxer_id)

            if not boxer:
                logger.info(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found")

            logger.info(f"Successfully retrieved boxer: {boxer.name}")
            return boxer

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving song by ID {boxer_id}: {e}")
            raise
    @classmethod
    def get_boxer_by_name(cls, name: str) -> "Boxers":
        """Retrieve a boxer by name.

        Args:
            name: The name of the boxer.

        Returns:
            Boxer: The boxer instance.

        Raises:
            ValueError: If the boxer with the given name does not exist.

        """
        logger.info(f"Attempting to retrieve boxer with name '{name}'")
    
        try:
            boxer = cls.query.filter_by(name=name).first()

            if not boxer:
                logger.info(f"Boxer with name '{name}' not found")
                raise ValueError(f"Boxer with name '{name}' not found")

            logger.info(f"Successfully retrieved boxer: {boxer.name} (ID: {boxer.id})")
            
            return boxer

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving boxer by name '{name}': {e}")
            db.session.rollback()
            raise
        
    @classmethod
    def delete(cls, boxer_id: int) -> None:
        """Delete a boxer by ID.

        Args:
            boxer_id: The ID of the boxer to delete.

        Raises:
            ValueError: If the boxer with the given ID does not exist.

        """
        boxer = cls.get_boxer_by_id(boxer_id)
        if boxer is None:
            logger.info(f"Boxer with ID {boxer_id} not found.")
            raise ValueError(f"Boxer with ID {boxer_id} not found.")
        db.session.delete(boxer)
        db.session.commit()
        logger.info(f"Boxer with ID {boxer_id} permanently deleted.")

    def update_stats(self, result: str) -> None:
        """Update the boxer's fight and win count based on result.

        Args:
            result: The result of the fight ('win' or 'loss').

        Raises:
            ValueError: If the result is not 'win' or 'loss'.
            ValueError: If the number of wins exceeds the number of fights.

        """
        if result not in {"win", "loss"}:
            raise ValueError("Result must be 'win' or 'loss'.")

        self.fights += 1
        if result == "win":
            self.wins += 1

        if self.wins > self.fights:
            raise ValueError("Wins cannot exceed number of fights.")

        db.session.commit()
        logger.info(f"Updated stats for boxer {self.name}: {self.fights} fights, {self.wins} wins.")

    @staticmethod
    def get_leaderboard(sort_by: str = "wins") -> List[dict]:
        """Retrieve a sorted leaderboard of boxers.

        Args:
            sort_by (str): Either "wins" or "win_pct".

        Returns:
            List[Dict]: List of boxers with stats and win percentage.

        Raises:
            ValueError: If the sort_by parameter is not valid.

        """
        logger.info(f"Retrieving leaderboard. Sort by: {sort_by}")

        if sort_by not in {"wins", "win_pct"}:
            logger.error(f"Invalid sort_by parameter: {sort_by}")
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")

        boxers = Boxers.query.filter(Boxers.fights > 0).all()

        def compute_win_pct(b: Boxers) -> float:
            return round((b.wins / b.fights) * 100, 1) if b.fights > 0 else 0.0

        leaderboard = [{
            "id": b.id,
            "name": b.name,
            "weight": b.weight,
            "height": b.height,
            "reach": b.reach,
            "age": b.age,
            "weight_class": b.weight_class,
            "fights": b.fights,
            "wins": b.wins,
            "win_pct": compute_win_pct(b)
        } for b in boxers]

        leaderboard.sort(key=lambda b: b[sort_by], reverse=True)
        logger.info("Leaderboard retrieved successfully.")
        return leaderboard