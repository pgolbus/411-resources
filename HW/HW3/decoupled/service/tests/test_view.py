from dataclasses import asdict

import pytest
from flask import Flask

from tictactoe import Board
from tictactoe.view import View

# Set up Flask app for testing
app = Flask(__name__)

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def view():
    return View()


def test_board_state(view, app_context):
    board = Board
    board.squares = [""] * 9

    with app.test_request_context():
        response = view.board_state(board)
        assert response.status_code == 200
        assert response.get_json() == {
            "board": ["", "", "", "", "", "", "", "", ""]
        }

def test_winner(view, app_context):
    with app.test_request_context():
        response = view.get_winner()
        assert response.status_code == 200
        assert response.get_json() == {
            "winner": None
        }
        response = view.get_winner("X")
        assert response.status_code == 200
        assert response.get_json() == {
            "winner": "X"
        }

def test_error(view, app_context):
    error_msg = "doesn't really matter..."

    with app.test_request_context():
        response = view.error(error_msg)
        assert response.status_code == 400
        assert response.get_json() == {
            "error": error_msg
        }
