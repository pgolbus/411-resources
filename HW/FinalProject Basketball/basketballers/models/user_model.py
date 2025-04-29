import hashlib
import logging
import os
from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from basketballers.db import db  # Ensure db import is correct
from basketballers.utils.logger import configure_logger  # Ensure logger is correct

# Set up logger
logger = logging.getLogger(__name__)
configure_logger(logger)

class User(db.Model, UserMixin):
    """Represents a user in the system."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    
    @staticmethod
    def _generate_hashed_password(password: str) -> tuple:
        """
        Generates a salted, hashed password.

        Args:
            password (str): The password to hash.

        Returns:
            tuple: A tuple containing the salt and hashed password.
        """
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return salt, hashed_password

    @classmethod
    def create_user(cls, username: str, password: str) -> None:
        """
        Create a new user with a salted, hashed password.

        Args:
            username (str): The username of the user.
            password (str): The password to hash and store.

        Raises:
            ValueError: If a user with the username already exists.
        """
        salt, hashed_password = cls._generate_hashed_password(password)
        new_user = cls(username=username, salt=salt, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User {username} created successfully.")
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Duplicate username: {username}")
            raise ValueError(f"User with username '{username}' already exists.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Check if the password matches the stored password for a user.

        Args:
            username (str): The username of the user.
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        hashed_password = hashlib.sha256((password + user.salt).encode()).hexdigest()
        return hashed_password == user.password

    @classmethod
    def delete_user(cls, username: str) -> None:
        """
        Delete a user from the database.

        Args:
            username (str): The username of the user to delete.

        Raises:
            ValueError: If the user does not exist.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info(f"User {username} not found")
            raise ValueError(f"User {username} not found")
        db.session.delete(user)
        db.session.commit()
        logger.info(f"User {username} deleted successfully.")

    def get_id(self) -> str:
        """Returns the user's id (username)."""
        return self.username

    @classmethod
    def get_id_by_username(cls, username: str) -> int:
        """
        Retrieve the ID of a user by username.

        Args:
            username (str): The username of the user.

        Returns:
            int: The ID of the user.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        return user.id

    @classmethod
    def update_password(cls, username: str, new_password: str) -> None:
        """
        Update the password for a user.

        Args:
            username (str): The username of the user.
            new_password (str): The new password to set.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info(f"User {username} not found")
            raise ValueError(f"User {username} not found")
        salt, hashed_password = cls._generate_hashed_password(new_password)
        user.salt = salt
        user.password = hashed_password
        db.session.commit()
        logger.info(f"Password updated for user: {username}")
