import logging

from flask import jsonify, make_response, Response
from tictactoe import Board

logger = logging.getLogger(__name__)

class View:
    """
    A class to represent the view for the Tic Tac Toe game.

    Methods
    -------
    board_state(board: Board) -> Response:
        Returns the current state of the board as a JSON response.

    get_winner(winner: str = None) -> Response:
        Returns the winner of the game as a JSON response.

    error(error: str) -> Response:
        Returns an error message as a JSON response.
    """

    def board_state(self, board: Board) -> Response:
        """
        Returns the current state of the board as a JSON response.

        Parameters
        ----------
        board : Board
            The current state of the Tic Tac Toe board.

        Returns
        -------
        Response
            A Flask response object containing the board state.
        """
        pass

    def get_winner(self, winner: str = None) -> Response:
        """
        Returns the winner of the game as a JSON response.

        Parameters
        ----------
        winner : str, optional
            The winner of the game (default is None).

        Returns
        -------
        Response
            A Flask response object containing the winner.
        """
        pass

    def error(self, error: str) -> Response:
        """
        Returns an error message as a JSON response.

        Parameters
        ----------
        error : str
            The error message to return.

        Returns
        -------
        Response
            A Flask response object containing the error message.
        """
        pass
