# boxing/__init__.py
from flask import Flask
from boxing.models import db

def create_app(config_class):
    """Application factory with configurable environment support."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app