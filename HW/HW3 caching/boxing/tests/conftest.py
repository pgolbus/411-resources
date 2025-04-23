import pytest

from boxing import create_app
from boxing.config import TestConfig
from boxing.models import db

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app  # this gives the app to the test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session
