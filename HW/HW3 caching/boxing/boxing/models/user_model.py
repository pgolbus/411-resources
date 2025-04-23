import hashlib
import logging
import os

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError

from boxing.db import db
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)  
    password = db.Column(db.String(64), nullable=False)  

    @staticmethod
    def _generate_hashed_password(password: str) -> tuple[str, str]:
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
        logger.info(f"Attempting to create new user: {username}")
        
        salt, hashed_password = cls._generate_hashed_password(password)
        new_user = cls(username=username, salt=salt, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User successfully created: {username}")
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Duplicate username: {username}")
            raise ValueError(f"User with username '{username}' already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error creating user {username}: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Check if a given password matches the stored password for a user.

        Args:
            username (str): The username of the user.
            password (str): The password to check.

        Returns:
            bool: True if the password is correct, False otherwise.

        Raises:
            ValueError: If the user does not exist.
        """
        logger.info(f"Attempting password check for user: {username}")
        
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User not found: {username}")
            raise ValueError(f"User {username} not found")
            
        hashed_password = hashlib.sha256((password + user.salt).encode()).hexdigest()
        is_valid = hashed_password == user.password
        
        if is_valid:
            logger.info(f"Password check successful for user: {username}")
        else:
            logger.warning(f"Invalid password attempt for user: {username}")
            
        return is_valid

    @classmethod
    def delete_user(cls, username: str) -> None:
        """
        Delete a user from the database.

        Args:
            username (str): The username of the user to delete.

        Raises:
            ValueError: If the user does not exist.
        """
        logger.info(f"Attempting to delete user: {username}")
        
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User not found for deletion: {username}")
            raise ValueError(f"User {username} not found")
            
        db.session.delete(user)
        db.session.commit()
        logger.info(f"User deleted successfully: {username}")

    def get_id(self) -> str:
        """
        Get the ID of the user.

        Returns:
            str: The ID of the user.
        """
        return str(self.id)

    @classmethod
    def get_id_by_username(cls, username: str) -> int:
        """
        Retrieve the ID of a user by username.

        Args:
            username (str): The username of the user.

        Returns:
            int: The ID of the user.

        Raises:
            ValueError: If the user does not exist.
        """
        logger.info(f"Looking up ID for username: {username}")
        
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User not found when looking up ID: {username}")
            raise ValueError(f"User {username} not found")
            
        logger.info(f"Found ID {user.id} for username: {username}")
        return user.id

    @classmethod
    def update_password(cls, username: str, new_password: str) -> None:
        """
        Update the password for a user.

        Args:
            username (str): The username of the user.
            new_password (str): The new password to set.

        Raises:
            ValueError: If the user does not exist.
        """
        logger.info(f"Attempting password update for user: {username}")
        
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User not found for password update: {username}")
            raise ValueError(f"User {username} not found")

        salt, hashed_password = cls._generate_hashed_password(new_password)
        user.salt = salt
        user.password = hashed_password
        
        try:
            db.session.commit()
            logger.info(f"Password updated successfully for user: {username}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update password for user {username}: {str(e)}")
            raise ValueError(f"Failed to update password: {str(e)}")