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
# Root Route (just to avoid 404 confusion)
#
####################################################

@app.route('/', methods=['GET'])
def index() -> Response:
    """Root route to confirm the app is running."""
    return make_response(jsonify({
        'status': 'success',
        'message': 'Boxing Flask app is running. Use /api/* routes.'
    }), 200)


####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    app.logger.info("Health check endpoint hit")
    return make_response(jsonify({
        'status': 'success',
        'message': 'Service is running'
    }), 200)


@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
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
    try:
        app.logger.info(f"Received request to delete boxer with ID {boxer_id}")
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
        app.logger.error(f"Failed to delete boxer: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An internal error occurred while deleting the boxer",
            "details": str(e)
        }), 500)


@app.route('/api/get-boxer-by-id/<int:boxer_id>', methods=['GET'])
def get_boxer_by_id(boxer_id: int) -> Response:
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


@app.route('/api/fight', methods=['GET'])
def bout() -> Response:
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


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard() -> Response:
    try:
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
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
