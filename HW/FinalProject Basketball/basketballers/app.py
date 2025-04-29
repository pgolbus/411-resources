from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

# Import configuration from the config file
from basketballers.config import ProductionConfig, TestConfig  # Correct import for config
from basketballers.db import db  # Correct import for db object
from basketballers.models.user_model import User  # Correct import for User model

# Initialize Flask app
app = Flask(__name__)

# Set up the configuration based on environment variable (default to ProductionConfig)
if os.getenv('FLASK_ENV') == 'development':
    app.config.from_object(TestConfig)  # Use TestConfig for testing
else:
    app.config.from_object(ProductionConfig)  # Use ProductionConfig for production

# Initialize SQLAlchemy and Flask-Login
db.init_app(app)  # Initialize db with Flask app
login_manager = LoginManager(app)

# This function is called when a user needs to be loaded from their session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route to create a new user account (POST request)
@app.route('/create-account', methods=['POST'])
def create_account():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists!"}), 400
        
        # Create new user and store in the database
        new_user = User(username=username)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully!"})

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

# Route for user login (POST request)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login successful!"})
    
    return jsonify({"message": "Invalid credentials!"}), 401

# Route for user logout (POST request)
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

# A protected route that requires the user to be logged in (GET request)
@app.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Hello, {current_user.username}! Welcome to the protected route."})

# Route to test if the app is working (GET request)
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Basketball App!"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
