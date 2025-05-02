import logging
from typing import List
from sqlalchemy.exc import IntegrityError

from basketballers.db import db
from basketballers.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class BasketballPlayer(db.Model):
    """Represents an NBA player in the system (stored in DB after being fetched from external API).
    
    This model maps to the 'players' table in the database and stores personal
    and performance-related attributes retrieved from the BallDontLie API.
    """

    __tablename__ = "players"
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    team = db.Column(db.String(50), nullable=False)
    height_feet = db.Column(db.Integer, nullable=False)
    height_inches = db.Column(db.Integer, nullable=False)
    weight_pounds = db.Column(db.Integer, nullable=False)

    def __init__(self, full_name: str, position: str, team: str,
                 height_feet: int, height_inches: int, weight_pounds: int):
        """
        Initialize a new Player instance with basic attributes.

        Args:
            full_name (str): Full name of the player.
            position (str): Playing position.
            team (str): Team name or abbreviation.
            height_feet (int): Player height in feet.
            height_inches (int): Additional height in inches.
            weight_pounds (int): Player's weight in pounds.
        Raises:
            ValueError: If any provided attributes are invalid.
        """
        if weight_pounds < 150:
            raise ValueError(f"Invalid weight: {weight_pounds}. Must be at least 150.")
        if height_feet < 4:
            raise ValueError(f"Invalid height (feet): {height_feet}. Must be at least 4 feet.")
        if height_inches < 0 or height_inches > 11:
            raise ValueError(f"Invalid height (inches): {height_inches}. Must be between 0 and 11.")

        self.full_name = full_name
        self.position = position
        self.team = team
        self.height_feet = height_feet
        self.height_inches = height_inches
        self.weight_pounds = weight_pounds
        
    @classmethod
    def create_player(cls, full_name: str, position: str, team: str,
                      height_feet: int, height_inches: int, weight_pounds: int) -> None:
        """
        Creates and stores a new player.

        Args:
            full_name (str): Player's name.
            position (str): Playing position.
            team (str): Team name or code.
            height_feet (int): Height in feet.
            height_inches (int): Additional inches.
            weight_pounds (int): Weight in pounds.

        Raises:
            ValueError: If a player with the same name already exists or validation fails.
            Exception: For any other database error.
        """
        logger.info(f"Creating player: {full_name}, {position}, {team}")
        try:
            if cls.query.filter_by(full_name=full_name).first():
                raise ValueError(f"Player with name '{full_name}' already exists.")

            new_player = cls(full_name=full_name, position=position, team=team,
                             height_feet=height_feet, height_inches=height_inches, weight_pounds=weight_pounds)
            db.session.add(new_player)
            db.session.commit()
            logger.info(f"Player created successfully: {full_name}")
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Integrity error when creating player '{full_name}'")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during player creation: {e}")
            raise
            
    @classmethod
    def get_player_by_id(cls, player_id: int) -> "BasketballPlayer":
        """
        Retrieve a player by internal database ID.

        Args:
            player_id (int): Primary key of the player.

        Returns:
            BasketballPlayer: Player instance.

        Raises:
            ValueError: If player is not found.
        """
        player = cls.query.get(player_id)
        if player is None:
            logger.info(f"Player with ID {player_id} not found.")
            raise ValueError(f"Player with ID {player_id} not found.")
        return player

    @classmethod
    def get_player_by_name(cls, name: str) -> "BasketballPlayer":
        """
        Retrieve a player using their full name.

        Args:
            name (str): Full name of the player.

        Returns:
            BasketballPlayer: Player instance.

        Raises:
            ValueError: If player is not found.
        """
        player = cls.query.filter_by(full_name=name).first()
        if player is None:
            logger.info(f"Player with name '{name}' not found.")
            raise ValueError(f"Player with name '{name}' not found.")
        return player

    @classmethod
    def delete_player(cls, player_id: int) -> None:
        """
        Delete a player from the database by internal ID.

        Args:
            player_id (int): ID of the player to delete.

        Raises:
            ValueError: If player is not found.
        """
        player = cls.get_player_by_id(player_id)
        db.session.delete(player)
        db.session.commit()
        logger.info(f"Player with ID {player_id} deleted.")

    @staticmethod
    def get_all_players() -> List[dict]:
        """
        Retrieve all players currently stored in the database.

        Returns:
            List[dict]: A list of dictionaries with player attributes.
        """
        players = BasketballPlayer.query.all()
        return [
            {
                "id": p.id,
                "full_name": p.full_name,
                "position": p.position,
                "team": p.team,
                "height_feet": p.height_feet,
                "height_inches": p.height_inches,
                "weight_pounds": p.weight_pounds
            } for p in players
        ]