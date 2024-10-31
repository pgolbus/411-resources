from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from meal_max.models import kitchen_model
from meal_max.models.battle_model import BattleModel
from meal_max.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)

# Initialize the BattleModel
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

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and meals table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if meals table exists...")
        check_table_exists("meals")
        app.logger.info("meals table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


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
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Check that price is a float and has at most two decimal places
        try:
            price = float(price)
            if round(price, 2) != price:
                raise ValueError("Price has more than two decimal places")
        except ValueError as e:
            return make_response(jsonify({'error': 'Price must be a valid float with at most two decimal places'}), 400)

        # Call the kitchen_model function to add the combatant to the database
        app.logger.info('Adding meal: %s, %s, %.2f, %s', meal, cuisine, price, difficulty)
        kitchen_model.create_meal(meal, cuisine, price, difficulty)

        app.logger.info("Combatant added: %s", meal)
        return make_response(jsonify({'status': 'success', 'combatant': meal}), 201)
    except Exception as e:
        app.logger.error("Failed to add combatant: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-meals', methods=['DELETE'])
def clear_catalog() -> Response:
    """
    Route to clear all meals (recreates the table).

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info("Clearing the meals")
        kitchen_model.clear_meals()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error clearing catalog: {e}")
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

        kitchen_model.delete_meal(meal_id)
        return make_response(jsonify({'status': 'success'}), 200)
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

        meal = kitchen_model.get_meal_by_id(meal_id)
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

        meal = kitchen_model.get_meal_by_name(meal_name)
        return make_response(jsonify({'status': 'success', 'meal': meal}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving meal by name: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


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

        return make_response(jsonify({'status': 'success', 'winner': winner}), 200)
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
        return make_response(jsonify({'status': 'success'}), 200)
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
        meal = data.get('meal')
        app.logger.info("Preparing combatant: %s", meal)

        if not meal:
            return make_response(jsonify({'error': 'You must name a combatant'}), 400)

        try:
            meal = kitchen_model.get_meal_by_name(meal)
            battle_model.prep_combatant(meal)
            combatants = battle_model.get_combatants()
        except Exception as e:
            app.logger.error("Failed to prepare combatant: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
        return make_response(jsonify({'status': 'success', 'combatants': combatants}), 200)

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

        leaderboard_data = kitchen_model.get_leaderboard(sort_by)

        return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
    except Exception as e:
        app.logger.error(f"Error generating leaderboard: {e}")
        return make_response(jsonify({'error': str(e)}), 500)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)