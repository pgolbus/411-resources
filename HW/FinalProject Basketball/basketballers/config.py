import os

class ProductionConfig:
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = False  # Don't use in production yet
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_DOMAIN = None
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")  # Default secret key for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///basketballers.db")  # Update to basketballers.db

class TestConfig:
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
