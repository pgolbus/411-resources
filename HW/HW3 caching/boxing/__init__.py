from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ✅ This is what the smoketest is checking
    @app.route("/api/health")
    def health():
        return jsonify({"status": "success"}), 200

    return app
