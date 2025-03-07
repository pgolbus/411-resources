from dataclasses import asdict, dataclass
import logging
from typing import Any, List

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from meal_max.clients.redis_client import redis_client
from meal_max.db import db
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meals(db.Model):
    __tablename__ = 'meals'

    id: int = db.Column(db.Integer, primary_key=True)
    meal: str = db.Column(db.String(80), unique=True, nullable=False)
    cuisine: str = db.Column(db.String(50))
    price: float = db.Column(db.Float, nullable=False)
    difficulty: str = db.Column(db.String(10), nullable=False)
    battles: int = db.Column(db.Integer, default=0)
    wins: int = db.Column(db.Integer, default=0)
    deleted: bool = db.Column(db.Boolean, default=False)

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")

    @classmethod
    def create_meal(cls, meal: str, cuisine: str, price: float, difficulty: str, battles: int = 0, wins: int = 0) -> None:
        """
        Create a new meal in the database.

        Args:
            meal (str): The name of the meal.
            cuisine (str): The type of cuisine (e.g., 'Italian', 'Mexican').
            price (float): The price of the meal. Must be a positive number.
            difficulty (str): The difficulty level of preparing the meal ('LOW', 'MED', 'HIGH').
            battles (int, optional): Initial number of battles for the meal. Defaults to 0.
            wins (int, optional): Initial number of wins for the meal. Defaults to 0.

        Raises:
            ValueError: If the price or difficulty level is invalid, or if a meal with the same name exists.
            IntegrityError: If there is a database error.
        """
        # Validate price and difficulty
        if price <= 0:
            raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
        if difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

        # Create and commit the new meal
        new_meal = cls(meal=meal, cuisine=cuisine, price=price, difficulty=difficulty, battles=battles, wins=wins)
        try:
            db.session.add(new_meal)
            db.session.commit()
            logger.info("Meal successfully added to the database: %s", meal)
        except Exception as e:
            db.session.rollback()
            if isinstance(e, IntegrityError):
                logger.error("Duplicate meal name: %s", meal)
                raise ValueError(f"Meal with name '{meal}' already exists")
            else:
                logger.error("Database error: %s", str(e))
                raise

    @classmethod
    def delete_meal(cls, meal_id: int) -> None:
        """
        Soft delete a meal by marking it as deleted.

        Args:
            meal_id (int): The ID of the meal to delete.

        Raises:
            ValueError: If the meal with the given ID does not exist or is already deleted.
        """
        meal = cls.query.filter_by(id=meal_id).first()
        if not meal:
            logger.info("Meal %s not found", meal_id)
            raise ValueError(f"Meal {meal_id} not found")
        if meal.deleted:
            logger.info("Meal with ID %s has already been deleted", meal_id)
            raise ValueError(f"Meal with ID {meal_id} has been deleted")

        meal.deleted = True
        db.session.commit()
        logger.info("Meal with ID %s marked as deleted.", meal_id)

    @classmethod
    def get_leaderboard(cls, sort_by: str = "wins") -> List[dict[str, Any]]:
        """
        Retrieve the leaderboard of meals based on wins or win percentage.

        Args:
            sort_by (str, optional): Specifies the sorting method for the leaderboard.
                                     Options are 'wins' (default) or 'win_pct'.

        Returns:
            List[dict]: A list of meals with stats for leaderboard display.

        Raises:
            ValueError: If an invalid sort_by parameter is provided.
        """
        if sort_by not in ["wins", "win_pct"]:
            logger.error("Invalid sort_by parameter: %s", sort_by)
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")

        query = cls.query.filter_by(deleted=False).filter(cls.battles > 0)
        if sort_by == "win_pct":
            query = query.order_by((cls.wins * 1.0 / cls.battles).desc())
        elif sort_by == "wins":
            query = query.order_by(cls.wins.desc())

        leaderboard = [
            {
                'id': meal.id,
                'meal': meal.meal,
                'cuisine': meal.cuisine,
                'price': meal.price,
                'difficulty': meal.difficulty,
                'battles': meal.battles,
                'wins': meal.wins,
                'win_pct': round((meal.wins / meal.battles) * 100, 1) if meal.battles > 0 else 0
            }
            for meal in query.all()
        ]
        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    @classmethod
    def get_meal_by_id(cls, meal_id: int, meal_name: str = None) -> dict[str, Any]:
        """
        Retrieve a meal by its ID.

        Args:
            meal_id (int): The ID of the meal.
            meal_name (str, optional): The name of the meal, if available.

        Returns:
            dict: The meal data as a dictionary.

        Raises:
            ValueError: If the meal does not exist or is deleted.
        """
        logger.info("Retrieving meal by ID: %s", meal_id)
        cache_key = f"meal_{meal_id}"
        cached_meal = redis_client.hgetall(cache_key)
        if cached_meal:
            logger.info("Meal retrieved from cache: %s", meal_id)
            meal_data = {k.decode(): v.decode() for k, v in cached_meal.items()}
            meal_data["price"] = float(meal_data["price"])
            # meal_data['deleted'] is a string. We need to convert it to a bool
            meal_data['deleted'] = meal_data.get('deleted', 'false').lower() == 'true'
            if meal_data['deleted']:
                logger.info("Meal with %s %s not found", "name" if meal_name else "ID", meal_name or meal_id)
                raise ValueError(f"Meal {meal_name or meal_id} not found")
            return meal_data
        meal = cls.query.filter_by(id=meal_id).first()
        if not meal or meal.deleted:
            logger.info("Meal with %s %s not found", "name" if meal_name else "ID", meal_name or meal_id)
            raise ValueError(f"Meal {meal_name or meal_id} not found")
        # Convert the meal object to a dictionary and cache it
        logger.info("Meal retrieved from database and cached: %s", meal_id)
        meal_dict = asdict(meal)
        redis_client.hset(cache_key, mapping={k: str(v) for k, v in meal_dict.items()})
        return meal_dict

    @classmethod
    def get_meal_by_name(cls, meal_name: str) -> dict[str, Any]:
        """
        Retrieve a meal by its name, using a cached association between name and ID.

        Args:
            meal_name (str): The name of the meal.

        Returns:
            dict: The meal data as a dictionary.

        Raises:
            ValueError: If the meal does not exist or is deleted.
        """
        logger.info("Retrieving meal by name: %s", meal_name)
        cache_key = f"meal_name:{meal_name}"

        # Check if name-to-ID association is cached
        meal_id = redis_client.get(cache_key)
        if meal_id:
            logger.info("Meal ID %s retrieved from cache for name: %s", meal_id.decode(), meal_name)
            # Use get_meal_by_id to retrieve the full meal data from ID
            return cls.get_meal_by_id(int(meal_id.decode()), meal_name)

        # Fallback to database if cache miss
        meal = cls.query.filter_by(meal=meal_name).first()
        if not meal or meal.deleted:
            logger.info("Meal with name %s not found", meal_name)
            raise ValueError(f"Meal {meal_name} not found")

        # Cache the name-to-ID association and retrieve the full meal data
        # TODO: This should happen when a meal is created, not here
        logger.info("Caching meal ID %s for name: %s", meal.id, meal_name)
        redis_client.set(cache_key, str(meal.id))
        return cls.get_meal_by_id(meal.id, meal_name)

    @classmethod
    def update_meal(cls, meal_id: int, **kwargs) -> None:
        """
        Update attributes of a meal.

        Args:
            meal_id (int): The ID of the meal to update.
            kwargs: Key-value pairs of attributes to update (excluding 'meal').

        Raises:
            ValueError: If any attribute is invalid or if the meal is not found.
        """
        meal = cls.query.filter_by(id=meal_id).first()
        if not meal or meal.deleted is True:
            logger.info("Meal with ID %s not found", meal_id)
            raise ValueError(f"Meal {meal_id} not found")

        logger.debug("Updating meal with ID %s: %s", meal_id, kwargs)

        for key, value in kwargs.items():
            if key == "meal":
                logger.info("Cannot update meal name")
                raise ValueError("Cannot update meal name")
            if key == "difficulty" and value not in ['LOW', 'MED', 'HIGH']:
                logger.info("Invalid difficulty level: %s", value)
                raise ValueError(f"Invalid difficulty level: {value}. Must be 'LOW', 'MED', or 'HIGH'.")
            if key == "price" and value <= 0:
                logger.info("Invalid price: %s", value)
                raise ValueError(f"Invalid price: {value}. Price must be a positive number.")
            if hasattr(meal, key):
                setattr(meal, key, value)
            else:
                logger.info("Invalid attribute: %s", key)
                raise ValueError(f"Invalid attribute: {key}")

        db.session.commit()
        logger.info("Meal with ID %s updated successfully", meal_id)

    @classmethod
    def update_meal_stats(cls, meal_id: int, result: str) -> None:
        """
        Update meal stats (battles and wins).

        Args:
            meal_id (int): The ID of the meal.
            result (str): 'win' or 'loss' to update the stats.

        Raises:
            ValueError: If the meal is not found, deleted, or the result is invalid.
        """
        meal = cls.query.filter_by(id=meal_id).first()
        if not meal:
            logger.info("Meal with ID %s not found", meal_id)
            raise ValueError(f"Meal {meal_id} not found")
        if meal.deleted:
            logger.info("Meal with ID %s has been deleted", meal_id)
            raise ValueError(f"Meal {meal_id} has been deleted")

        if result == 'win':
            meal.battles += 1
            meal.wins += 1
        elif result == 'loss':
            meal.battles += 1
        else:
            raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

        db.session.commit()
        logger.info("Meal stats updated for ID %s: %s", meal_id, result)

def update_cache_for_meal(mapper, connection, target):
    """
    Update the Redis cache for a meal entry after an update or delete operation.

    This function is intended to be used as an SQLAlchemy event listener for the
    `after_update` and `after_delete` events on the Meals model. When a meal is
    updated or deleted, this function will either update the corresponding Redis
    cache entry with the new meal details or remove the entry if the meal has
    been marked as deleted.

    Args:
        mapper (Mapper): The SQLAlchemy Mapper object, which provides information
                         about the model being updated (automatically passed by SQLAlchemy).
        connection (Connection): The SQLAlchemy Connection object used for the
                                 database operation (automatically passed by SQLAlchemy).
        target (Meals): The instance of the Meals model that was updated or deleted.
                        The `target` object contains the updated meal data.

    Side-effects:
        - If the meal is marked as deleted (`target.deleted` is True), the function
          removes the corresponding cache entry from Redis.
        - If the meal is not marked as deleted, the function updates the Redis cache
          entry with the latest meal data using the `hset` command.
    """
    cache_key = f"meal:{target.id}"
    if target.deleted:
        redis_client.delete(cache_key)
    else:
        redis_client.hset(
            cache_key,
            mapping={k.encode(): str(v).encode() for k, v in asdict(target).items()}
        )

# Register the listener for update and delete events
event.listen(Meals, 'after_update', update_cache_for_meal)
event.listen(Meals, 'after_delete', update_cache_for_meal)