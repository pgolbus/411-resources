from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

# Import configuration from the config file
from basketballers.config import ProductionConfig, TestConfig  # Correct import for config
from basketballers.db import db  # Correct import for db object
from basketballers.models.user_model import User  # Correct import for User model
from basketballers.models.basketball_player_model import BasketballPlayer
from basketballers.models.basketball_general_model import GameModel

import logging
logger = logging.getLogger(__name__)

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
@app.route('/api/create-account', methods=['POST'])
def create_account():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists!"}), 400
        
        # Create new user and store in the database
        User.create_user(username, password)

        return jsonify({"message": "User created successfully!"})

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

# Route for user login (POST request)
@app.route('/api/login', methods=['POST'])
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
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

# A protected route that requires the user to be logged in (GET request)
@app.route('/api/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Hello, {current_user.username}! Welcome to the protected route."})

# Route to test if the app is working (GET request)
@app.route('/api', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Basketball App!"})

#Healthcheck

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
     Health check route to verify the service is running.

     Returns:
        JSON response indicating the health status of the service.

    """
    logger.info("Health check endpoint hit")
    return make_response(jsonify({
        'status': 'success',
            'message': 'Service is running'
    }), 200)
 
@app.route("/api/delete-users", methods=["DELETE"])
def delete_users():
    try:
            logger.info("Received request to recreate Users table")
            with app.app_context():
                User.__table__.drop(db.engine)
                User.__table__.create(db.engine)
            logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

    except Exception as e:
            logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            User.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)
        
@app.route("/api/delete-players", methods=["DELETE"])
def delete_players():
    """Recreate the players table to delete players users.

      Returns:
          JSON response indicating the success of recreating the BasketballPlayer table.

      Raises:
          500 error if there is an issue recreating the BasketballPlayer table.
      """
    try:
          logger.info("Received request to recreate BasketballPlayer table")
          with app.app_context():
              BasketballPlayer.__table__.drop(db.engine)
              BasketballPlayer.__table__.create(db.engine)
          logger.info("BasketballPlayer table recreated successfully")
          return make_response(jsonify({
              "status": "success",
              "message": f"BasketballPlayer table recreated successfully"
          }), 200)

    except Exception as e:
          logger.error(f"BasketballPlayer table recreation failed: {e}")
          return make_response(jsonify({
              "status": "error",
              "message": "An internal error occurred while deleting users",
              "details": str(e)
          }), 500)
      
      
@app.route('/api/add-player', methods=['POST'])
@login_required
def add_player() -> Response:
    """
    Route to add a new basketball player to the database.

    Expected JSON Input:
        - full_name (str): The player's full name.
        - position (str): The player's position.
        - team (str): The team name.
        - height_feet (int): Height in feet.
        - height_inches (int): Additional inches.
        - weight_pounds (int): Player weight in pounds.

    Returns:
        JSON response indicating the success of the player addition.

    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the player to the database.
    """
    logger.info("Received request to add a new player")

    try:
        data = request.get_json()
        required_fields = ["full_name", "position", "team", "height_feet", "height_inches", "weight_pounds"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return make_response(jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400)

        full_name = data["full_name"]
        position = data["position"]
        team = data["team"]
        height_feet = data["height_feet"]
        height_inches = data["height_inches"]
        weight_pounds = data["weight_pounds"]

        if (
            not isinstance(full_name, str)
            or not isinstance(position, str)
            or not isinstance(team, str)
            or not isinstance(height_feet, int)
            or not isinstance(height_inches, int)
            or not isinstance(weight_pounds, int)
        ):
            logger.warning("Invalid input data types")
            return make_response(jsonify({
                "status": "error",
                "message": "Invalid input types"
            }), 400)

        logger.info(f"Adding player: {full_name} - {team}, {position}, {height_feet}'{height_inches}, {weight_pounds}lbs")
        BasketballPlayer.create_player(full_name, position, team, height_feet, height_inches, weight_pounds)

        return make_response(jsonify({
            "status": "success",
            "message": f"Player '{full_name}' added successfully"
        }), 201)

    except Exception as e:
        logger.error(f"Failed to add player: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while adding the player",
            "details": str(e)
        }), 500)

@app.route('/api/get-player-by-name/<string:player_name>', methods=['GET'])
@login_required
def get_player_by_name(player_name: str) -> Response:
    """
    Route to get a basketball player by full name.

    Path Parameter:
        - player_name (str): The full name of the player.

    Returns:
        JSON response containing the player details if found.

    Raises:
        400 error if the player is not found.
        500 error if there is an issue retrieving the player from the database.
    """
    try:
        logger.info(f"Received request to retrieve player with name '{player_name}'")

        player = BasketballPlayer.get_player_by_name(player_name)

        if not player:
            logger.warning(f"Player '{player_name}' not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Player '{player_name}' not found"
            }), 400)

        logger.info(f"Successfully retrieved player: {player.full_name}")
        return make_response(jsonify({
            "status": "success",
            "player": {
                "id": player.id,
                "full_name": player.full_name,
                "position": player.position,
                "team": player.team,
                "height_feet": player.height_feet,
                "height_inches": player.height_inches,
                "weight_pounds": player.weight_pounds
            }
        }), 200)

    except Exception as e:
        logger.error(f"Error retrieving player '{player_name}': {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while retrieving the player",
            "details": str(e)
        }), 500)


@app.route('/api/delete-player/<int:player_id>', methods=['DELETE'])
@login_required
def delete_player(player_id: int) -> Response:
    """
    Route to delete a basketball player by ID.

    Path Parameter:
        - player_id (int): The ID of the player to delete.

    Returns:
        JSON response indicating success of the operation.

    Raises:
        400 error if the player does not exist.
        500 error if there is an issue deleting the player from the database.
    """
    try:
        logger.info(f"Received request to delete player with ID {player_id}")

        player = BasketballPlayer.get_player_by_id(player_id)
        if not player:
            logger.warning(f"Player with ID {player_id} not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Player with ID {player_id} not found"
            }), 400)

        BasketballPlayer.delete_player(player_id)
        logger.info(f"Successfully deleted player with ID {player_id}")

        return make_response(jsonify({
            "status": "success",
            "message": f"Player with ID {player_id} deleted successfully"
        }), 200)

    except Exception as e:
        logger.error(f"Failed to delete player: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while deleting the player",
            "details": str(e)
        }), 500)

        
@app.route('/api/get-player-by-id/<int:player_id>', methods=['GET'])
@login_required
def get_player_by_id(player_id: int) -> Response:
    """
    Route to get a basketball player by their ID.

    Path Parameter:
        - player_id (int): The ID of the player.

    Returns:
        JSON response containing the player details if found.

    Raises:
        400 error if the player is not found.
        500 error if there is an issue retrieving the player from the database.
    """
    try:
        logger.info(f"Received request to retrieve player with ID {player_id}")

        player = BasketballPlayer.get_player_by_id(player_id)

        if not player:
            logger.warning(f"Player with ID {player_id} not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Player with ID {player_id} not found"
            }), 400)

        logger.info(f"Successfully retrieved player: {player.full_name}")
        return make_response(jsonify({
            "status": "success",
            "player": {
                "id": player.id,
                "full_name": player.full_name,
                "position": player.position,
                "team": player.team,
                "height_feet": player.height_feet,
                "height_inches": player.height_inches,
                "weight_pounds": player.weight_pounds
            }
        }), 200)

    except Exception as e:
        logger.error(f"Error retrieving player with ID {player_id}: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while retrieving the player",
            "details": str(e)
        }), 500)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
