from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from boxing.models import boxers_model
from boxing.models.ring_model import RingModel
from boxing.utils.logger import configure_logger
from boxing.utils.sql_utils import check_database_connection, check_table_exists


load_dotenv()


app = Flask(__name__)
# If you get errors that use words like cross origin or flight, uncomment this.
# It will bypass standard security stuff we'll talk about later
# CORS(app)


ring_model = RingModel()
configure_logger(app.logger)


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
    app.logger.info("Health check endpoint hit")
    return make_response(jsonify({
        'status': 'success',
        'message': 'Service is running'
    }), 200)


@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """Route to check if the database connection and boxers table are functional.

    Returns:
        JSON response indicating the database health status.

    Raises:
        404 error if the boxers table is not found.
        500 error if there is an issue with the database connection.

    """
    try:
        check_database_connection()
        app.logger.info("Database connection is OK.")
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return make_response(jsonify({
            'status': 'error',
            'message': 'Database connection failed',
            'details': str(e)
        }), 500)

    try:
        check_table_exists("boxers")
        app.logger.info("Boxer table exists.")
    except Exception as e:
        app.logger.error(f"Failed to find boxers table: {e}")
        return make_response(jsonify({
            'status': 'error',
            'message': 'Boxers table not found',
            'details': str(e)
        }), 404)

    return make_response(jsonify({
        'status': 'success',
        'message': 'Database and boxers table are healthy'
    }), 200)


##########################################################
#
# Boxers
#
##########################################################


@app.route('/api/add-boxer', methods=['POST'])
def add_boxer() -> Response:
    """Route to add a new boxer to the gym.

    Expected JSON Input:
        - name (str): The boxer's name.
        - weight (int): The boxer's weight.
        - height (int): The boxer's height.
        - reach (float): The boxer's reach in inches.
        - age (int): The boxer's age.

    Returns:
        JSON response indicating the success of the boxer addition.

    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the boxer to the database.

    """
    app.logger.info("Received request to create new boxer")

    try:
        data = request.get_json()

        required_fields = ["name", "weight", "height", "reach", "age"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            app.logger.warning(f"Missing required fields: {missing_fields}")
            return make_response(jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400)

        name = data["name"]
        weight = data["weight"]
        height = data["height"]
        reach = data["reach"]
        age = data["age"]

        if (
            not isinstance(name, str)
            or not isinstance(weight, (int, float))
            or not isinstance(height, (int, float))
            or not isinstance(reach, (int, float))
            or not isinstance(age, int)
        ):
            app.logger.warning("Invalid input data types")
            return make_response(jsonify({
                "status": "error",
                "message": "Invalid input types: name should be a string, weight/height/reach should be numbers, age should be an integer"
            }), 400)

        app.logger.info(f"Adding boxer: {name}, {weight}kg, {height}cm, {reach} inches, {age} years old")
        boxers_model.create_boxer(name, weight, height, reach, age)

        app.logger.info(f"Boxer added successfully: {name}")
        return make_response(jsonify({
            "status": "success",
            "message": f"Boxer '{name}' added successfully"
        }), 201)

    except Exception as e:
        app.logger.error(f"Failed to add boxer: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while adding the boxer",
            "details": str(e)
        }), 500)


@app.route('/api/delete-boxer/<int:boxer_id>', methods=['DELETE'])
def delete_boxer(boxer_id: int) -> Response:
    """Route to delete a boxer by ID.

    Path Parameter:
        - boxer_id (int): The ID of the boxer to delete.

    Returns:
        JSON response indicating success of the operation.

    Raises:
        400 error if the boxer does not exist.
        500 error if there is an issue removing the boxer from the database.

    """
    try:
        app.logger.info(f"Received request to delete boxer with ID {boxer_id}")

        # Check if the boxer exists before attempting to delete
        boxer = boxers_model.get_boxer_by_id(boxer_id)
        if not boxer:
            app.logger.warning(f"Boxer with ID {boxer_id} not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Boxer with ID {boxer_id} not found"
            }), 400)

        boxers_model.delete_boxer(boxer_id)
        app.logger.info(f"Successfully deleted boxer with ID {boxer_id}")

        return make_response(jsonify({
            "status": "success",
            "message": f"Boxer with ID {boxer_id} deleted successfully"
        }), 200)

    except Exception as e:
        app.logger.error(f"Failed to add boxer: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while deleting the boxer",
            "details": str(e)
        }), 500)


@app.route('/api/get-boxer-by-id/<int:boxer_id>', methods=['GET'])
def get_boxer_by_id(boxer_id: int) -> Response:
    """Route to get a boxer by its ID.

    Path Parameter:
        - boxer_id (int): The ID of the boxer.

    Returns:
        JSON response containing the boxer details if found.

    Raises:
        400 error if the boxer is not found.
        500 error if there is an issue retrieving the boxer from the database.

    """
    try:
        app.logger.info(f"Received request to retrieve boxer with ID {boxer_id}")

        boxer = boxers_model.get_boxer_by_id(boxer_id)

        if not boxer:
            app.logger.warning(f"Boxer with ID {boxer_id} not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Boxer with ID {boxer_id} not found"
            }), 400)

        app.logger.info(f"Successfully retrieved boxer: {boxer}")
        return make_response(jsonify({
            "status": "success",
            "boxer": boxer
        }), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving boxer with ID {boxer_id}: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while retrieving the boxer",
            "details": str(e)
        }), 500)


@app.route('/api/get-boxer-by-name/<string:boxer_name>', methods=['GET'])
def get_boxer_by_name(boxer_name: str) -> Response:
    """Route to get a boxer by its name.

    Path Parameter:
        - boxer_name (str): The name of the boxer.

    Returns:
        JSON response containing the boxer details if found.

    Raises:
        400 error if the boxer name is missing or not found.
        500 error if there is an issue retrieving the boxer from the database.

    """
    try:
        app.logger.info(f"Received request to retrieve boxer with name '{boxer_name}'")

        boxer = boxers_model.get_boxer_by_name(boxer_name)

        if not boxer:
            app.logger.warning(f"Boxer '{boxer_name}' not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Boxer '{boxer_name}' not found"
            }), 400)

        app.logger.info(f"Successfully retrieved boxer: {boxer}")
        return make_response(jsonify({
            "status": "success",
            "boxer": boxer
        }), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving boxer with name '{boxer_name}': {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while retrieving the boxer",
            "details": str(e)
        }), 500)


############################################################
#
# Ring
#
############################################################


@app.route('/api/fight', methods=['GET'])
def bout() -> Response:
    """Route that triggers the fight between the two current boxers.

    Returns:
        JSON response indicating the winner of the fight.

    Raises:
        400 error if the fight cannot be triggered due to insufficient combatants.
        500 error if there is an issue during the fight.

    """
    try:
        app.logger.info("Initiating fight...")

        winner = ring_model.fight()

        app.logger.info(f"Fight complete. Winner: {winner}")
        return make_response(jsonify({
            "status": "success",
            "message": "Fight complete",
            "winner": winner
        }), 200)

    except ValueError as e:
        app.logger.warning(f"Fight cannot be triggered: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": str(e)
        }), 400)

    except Exception as e:
        app.logger.error(f"Error while triggering fight: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while triggering the fight",
            "details": str(e)
        }), 500)


@app.route('/api/clear-boxers', methods=['POST'])
def clear_boxers() -> Response:
    """Route to clear the list of boxers from the ring.

    Returns:
        JSON response indicating success of the operation.

    Raises:
        500 error if there is an issue clearing boxers.

    """
    try:
        app.logger.info("Clearing all boxers...")

        ring_model.clear_ring()

        app.logger.info("Boxers cleared from ring successfully.")
        return make_response(jsonify({
            "status": "success",
            "message": "Boxers have been cleared from ring."
        }), 200)

    except Exception as e:
        app.logger.error(f"Failed to clear boxers: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while clearing boxers",
            "details": str(e)
        }), 500)


@app.route('/api/enter-ring', methods=['POST'])
def enter_ring() -> Response:
    """Route to have a boxer enter the ring for the next fight.

    Expected JSON Input:
        - name (str): The boxer's name.

    Returns:
        JSON response indicating the success of the boxer entering the ring.

    Raises:
        400 error if the request is invalid (e.g., boxer name missing or too many boxers in the ring).
        500 error if there is an issue with the boxer entering the ring.

    """
    try:
        data = request.get_json()
        boxer_name = data.get("name")

        if not boxer_name:
            app.logger.warning("Attempted to enter ring without specifying a boxer.")
            return make_response(jsonify({
                "status": "error",
                "message": "You must name a boxer"
            }), 400)

        app.logger.info(f"Attempting to enter {boxer_name} into the ring.")

        boxer = boxers_model.get_boxer_by_name(boxer_name)

        if not boxer:
            app.logger.warning(f"Boxer '{boxer_name}' not found.")
            return make_response(jsonify({
                "status": "error",
                "message": f"Boxer '{boxer_name}' not found"
            }), 400)

        try:
            ring_model.enter_ring(boxer)
        except ValueError as e:
            app.logger.warning(f"Cannot enter {boxer_name}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)

        boxers = ring_model.get_boxers()

        app.logger.info(f"Boxer '{boxer_name}' entered the ring. Current boxers: {boxers}")

        return make_response(jsonify({
            "status": "success",
            "message": f"Boxer '{boxer_name}' is now in the ring.",
            "boxers": boxers
        }), 200)

    except Exception as e:
        app.logger.error(f"Failed to enter boxer into the ring: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while entering the boxer into the ring",
            "details": str(e)
        }), 500)


@app.route('/api/get-boxers', methods=['GET'])
def get_boxers() -> Response:
    """Route to get the list of boxers in the ring.

    Returns:
        JSON response with the list of boxers.

    Raises:
        500 error if there is an issue getting the boxers.

    """
    try:
        app.logger.info("Retrieving list of boxers...")

        boxers = ring_model.get_boxers()

        app.logger.info(f"Retrieved {len(boxers)} boxer(s).")
        return make_response(jsonify({
            "status": "success",
            "boxers": boxers
        }), 200)

    except Exception as e:
        app.logger.error(f"Failed to retrieve boxers: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while retrieving boxers",
            "details": str(e)
        }), 500)


############################################################
#
# Leaderboard
#
############################################################


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard() -> Response:
    """Route to get the leaderboard of boxers sorted by wins or win percentage.

    Query Parameters:
        - sort (str): The field to sort by ('wins', or 'win_pct'). Default is 'wins'.

    Returns:
        JSON response with a sorted leaderboard of boxers.

    Raises:
        400 error if an invalid sort parameter is provided.
        500 error if there is an issue generating the leaderboard.

    """
    try:
        # Get the sort parameter from the query string, default to 'wins'
        sort_by = request.args.get('sort', 'wins').lower()

        valid_sort_fields = {'wins', 'win_pct'}

        if sort_by not in valid_sort_fields:
            app.logger.warning(f"Invalid sort parameter: '{sort_by}'")
            return make_response(jsonify({
                "status": "error",
                "message": f"Invalid sort parameter '{sort_by}'. Must be one of: {', '.join(valid_sort_fields)}"
            }), 400)

        app.logger.info(f"Generating leaderboard sorted by '{sort_by}'")

        leaderboard_data = boxers_model.get_leaderboard(sort_by)

        app.logger.info(f"Leaderboard generated successfully. {len(leaderboard_data)} boxers ranked.")

        return make_response(jsonify({
            "status": "success",
            "leaderboard": leaderboard_data
        }), 200)

    except Exception as e:
        app.logger.error(f"Error generating leaderboard: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while generating the leaderboard",
            "details": str(e)
        }), 500)


if __name__ == '__main__':
    app.logger.info("Starting Flask app...")

    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")