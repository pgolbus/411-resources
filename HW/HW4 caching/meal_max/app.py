from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from meal_max.db import db
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meals
from meal_max.models.mongo_session_model import login_user, logout_user
from meal_max.models.user_model import Users

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    battle_model = BattleModel()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, battle_model)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, battle_model)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    ##########################################################
    #
    # Meals
    #
    ##########################################################


    @app.route('/api/create-meal', methods=['POST'])
    def add_meal() -> Response:
        """
        Route to add a new meal to the database.

        Expected JSON Input:
            - meal (str): The name of the combatant (meal).
            - cuisine (str): The cuisine type of the combatant (e.g., Italian, Chinese).
            - price (float): The price of the combatant.
            - difficulty (str): The preparation difficulty (HIGH, MED, LOW).

        Returns:
            JSON response indicating the success of the combatant addition.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the combatant to the database.
        """
        app.logger.info('Creating new meal')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            meal = data.get('meal')
            cuisine = data.get('cuisine')
            price = data.get('price')
            difficulty = data.get('difficulty')

            if not meal or not cuisine or price is None or difficulty not in ['HIGH', 'MED', 'LOW']:
                raise BadRequest("Invalid input. All fields are required with valid values.")

            # Check that price is a float and has at most two decimal places
            try:
                price = float(price)
                if round(price, 2) != price:
                    raise ValueError("Price has more than two decimal places")
            except ValueError as e:
                return make_response(jsonify({'error': 'Price must be a valid float with at most two decimal places'}), 400)

            # Call the Meals function to add the combatant to the database
            app.logger.info('Adding meal: %s, %s, %.2f, %s', meal, cuisine, price, difficulty)
            Meals.create_meal(meal, cuisine, price, difficulty)

            app.logger.info("Combatant added: %s", meal)
            return make_response(jsonify({'status': 'combatant added', 'combatant': meal}), 201)
        except Exception as e:
            app.logger.error("Failed to add combatant: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/delete-meal/<int:meal_id>', methods=['DELETE'])
    def delete_meal(meal_id: int) -> Response:
        """
        Route to delete a meal by its ID. This performs a soft delete by marking it as deleted.

        Path Parameter:
            - meal_id (int): The ID of the meal to delete.

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info(f"Deleting meal by ID: {meal_id}")

            Meals.delete_meal(meal_id)
            return make_response(jsonify({'status': 'meal deleted'}), 200)
        except Exception as e:
            app.logger.error(f"Error deleting meal: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-meal-by-id/<int:meal_id>', methods=['GET'])
    def get_meal_by_id(meal_id: int) -> Response:
        """
        Route to get a meal by its ID.

        Path Parameter:
            - meal_id (int): The ID of the meal.

        Returns:
            JSON response with the meal details or error message.
        """
        try:
            app.logger.info(f"Retrieving meal by ID: {meal_id}")

            meal = Meals.get_meal_by_id(meal_id)
            return make_response(jsonify({'status': 'success', 'meal': meal}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving meal by ID: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-meal-by-name/<string:meal_name>', methods=['GET'])
    def get_meal_by_name(meal_name: str) -> Response:
        """
        Route to get a meal by its name.

        Path Parameter:
            - meal_name (str): The name of the meal.

        Returns:
            JSON response with the meal details or error message.
        """
        try:
            app.logger.info(f"Retrieving meal by name: {meal_name}")

            if not meal_name:
                return make_response(jsonify({'error': 'Meal name is required'}), 400)

            meal = Meals.get_meal_by_name(meal_name)
            return make_response(jsonify({'status': 'success', 'meal': meal}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving meal by name: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500

    ############################################################
    #
    # Battle
    #
    ############################################################


    @app.route('/api/battle', methods=['GET'])
    def battle() -> Response:
        """
        Route to initiate a battle between the two currently prepared meals.

        Returns:
            JSON response indicating the result of the battle and the winner.
        Raises:
            500 error if there is an issue during the battle.
        """
        try:
            app.logger.info('Two meals enter, one meal leaves!')

            winner = battle_model.battle()

            return make_response(jsonify({'status': 'battle complete', 'winner': winner}), 200)
        except Exception as e:
            app.logger.error(f"Battle error: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/clear-combatants', methods=['POST'])
    def clear_combatants() -> Response:
        """
        Route to clear the list of combatants for the battle.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue clearing combatants.
        """
        try:
            app.logger.info('Clearing all combatants...')
            battle_model.clear_combatants()
            app.logger.info('Combatants cleared.')
            return make_response(jsonify({'status': 'combatants cleared'}), 200)
        except Exception as e:
            app.logger.error("Failed to clear combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-combatants', methods=['GET'])
    def get_combatants() -> Response:
        """
        Route to get the list of combatants for the battle.

        Returns:
            JSON response with the list of combatants.
        """
        try:
            app.logger.info('Getting combatants...')
            combatants = battle_model.get_combatants()
            return make_response(jsonify({'status': 'success', 'combatants': combatants}), 200)
        except Exception as e:
            app.logger.error("Failed to get combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/prep-combatant', methods=['POST'])
    def prep_combatant() -> Response:
        """
        Route to prepare a prep a meal making it a combatant for a battle.

        Parameters:
            - meal (str): The name of the meal

        Returns:
            JSON response indicating the success of combatant preparation.
        Raises:
            500 error if there is an issue preparing combatants.
        """
        try:
            data = request.json
            if not data or 'meal' not in data:
                return make_response(jsonify({'error': 'Meal name is required'}), 400)
            meal = data.get('meal')
            app.logger.info("Preparing combatant: %s", meal)

            if not meal:
                raise BadRequest('You must name a combatant')

            try:
                meal = Meals.get_meal_by_name(meal)
                battle_model.prep_combatant(meal)
                combatants = battle_model.get_combatants()
            except Exception as e:
                app.logger.error("Failed to prepare combatant: %s", str(e))
                return make_response(jsonify({'error': str(e)}), 500)
            return make_response(jsonify({'status': 'combatant prepared', 'combatants': combatants}), 200)

        except Exception as e:
            app.logger.error("Failed to prepare combatants: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    ############################################################
    #
    # Leaderboard
    #
    ############################################################


    @app.route('/api/leaderboard', methods=['GET'])
    def get_leaderboard() -> Response:
        """
        Route to get the leaderboard of meals sorted by wins, battles, or win percentage.

        Query Parameters:
            - sort (str): The field to sort by ('wins', 'battles', or 'win_pct'). Default is 'wins'.

        Returns:
            JSON response with a sorted leaderboard of meals.
        Raises:
            500 error if there is an issue generating the leaderboard.
        """
        try:
            sort_by = request.args.get('sort', 'wins')  # Default sort by wins
            app.logger.info("Generating leaderboard sorted by %s", sort_by)

            leaderboard_data = Meals.get_leaderboard(sort_by)

            return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
        except Exception as e:
            app.logger.error(f"Error generating leaderboard: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)