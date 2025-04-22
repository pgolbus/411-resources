import pytest

# from app import create_app
from app import create_app
from config import TestConfig
from boxing.db import db

@pytest.fixture
def app():
    """Create a test Flask application with a clean database.
    
    This fixture ensures proper cleanup of database connections.
    Note: Added db.engine.dispose() to properly close all database connections.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        try:
            yield app
        finally:
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def session(app):
    """Provide a database session for tests.
    
    This fixture ensures proper cleanup of database connections.
    Note: Added try/finally block to ensure connections are properly closed.
    """
    with app.app_context():
        try:
            yield db.session
        finally:
            db.session.close()
            db.engine.dispose()