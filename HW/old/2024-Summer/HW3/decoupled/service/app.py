from flask import Flask, jsonify, make_response, request, Response
from flask_cors import CORS

from tictactoe.controller import get_board_state, get_winner, make_move
from tictactoe.view import View

app = Flask(__name__)
CORS(app)  # This will allow the React front-end to communicate with the Flask back-end


VIEW = View()


@app.route("/tictactoe/health", methods=["GET"])
@app.route("/tictactoe/healthcheck", methods=["GET"])
def health_check() -> Response:
    app.logger.info('Health check')
    return make_response(jsonify({"status": "OK"}), 200)

@app.route("/tictactoe/board", methods=["GET"])
def board_state() -> Response:
    app.logger.info('Get board state')
    return get_board_state()

@app.route("/tictactoe/check_winner", methods=["GET"])
def check_winner() -> Response:
    app.logger.info('Checking for a winner')
    return get_winner()

@app.route("/tictactoe/move", methods=["POST"])
def move() -> Response:
    app.logger.info('Moving')
    data = request.get_json()
    app.logger.info(data)
    index = data['index']
    app.logger.info(index)
    try:
        return make_move(index)
    except ValueError as e:
        return VIEW.error(str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
