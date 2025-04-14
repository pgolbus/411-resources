from flask import Flask, request, jsonify, make_response
import random
import logging

app = Flask(__name__)

boxers = []

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello():
    """
    Root endpoint that returns Hello, World!
    """
    return make_response({
        'response': 'Hello, World!',
        'status': 200
    })

@app.route('/boxer', methods=['POST'])
def create_boxer():
    """
    Create a new boxer.

    JSON input:
        {
            "name": "BoxerName"
        }

    Returns:
        JSON response with current list of boxers or error.
    """
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if name in boxers:
        return jsonify({"error": "Boxer already exists"}), 400

    if len(boxers) >= 2:
        return jsonify({"error": "Cannot add more than 2 boxers"}), 400

    boxers.append(name)
    logging.info(f"Boxer created: {name}")
    return jsonify({"message": f"Boxer {name} created", "boxers": boxers}), 201

@app.route('/boxer', methods=['DELETE'])
def delete_boxer():
    """
    Delete a boxer by name.

    JSON input:
        {
            "name": "BoxerName"
        }

    Returns:
        JSON message if boxer was deleted or an error.
    """
    data = request.get_json()
    name = data.get("name")

    if name not in boxers:
        logging.warning(f"Tried to delete non-existent boxer: {name}")
        return jsonify({"error": "Boxer not found"}), 404

    boxers.remove(name)
    logging.info(f"Deleted boxer: {name}")
    return jsonify({"message": f"{name} deleted", "boxers": boxers})

@app.route('/boxers', methods=['GET'])
def list_boxers():
    """
    List all current boxers.

    Returns:
        JSON array of boxer names.
    """
    return jsonify({"boxers": boxers})

@app.route('/fight', methods=['POST'])
def fight():
    """
    Simulate a fight between the two boxers.

    Returns:
        JSON response with winner and loser.
    """
    if len(boxers) < 2:
        logging.warning("Fight requested with fewer than 2 boxers.")
        return jsonify({"error": "Need two boxers to fight"}), 400

    boxer1, boxer2 = boxers[0], boxers[1]
    winner = random.choice([boxer1, boxer2])
    loser = boxer2 if winner == boxer1 else boxer1

    logging.info(f"Fight: {boxer1} vs {boxer2}. Winner: {winner}")
    return jsonify({
        "result": f"{winner} wins against {loser}!",
        "winner": winner,
        "loser": loser
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

