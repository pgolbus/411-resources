import pytest

from tictactoe import Board, SQUARE_OCCUPIED_ERROR_MSG
from tictactoe.model import Model


@pytest.fixture
def model():
    return Model()

def test_init_board(model):
    # Test that the board is initialized correctly
    assert isinstance(model.board, Board)

    # assert that there are 9 elts, all the empty string
    assert len(model.board.squares) == 9
    for square in model.board.squares:
        assert square == ""

def test_move(model):
    model.player = "X"
    model.move(0)
    assert model.board.squares[0] == "X"
    assert model.player == "O"
    assert model.winner is None
    model.move(1)
    assert model.board.squares[1] == "O"
    assert model.player == "X"
    assert model.winner is None
    model.board.squares = ["X", "O", "X", "O", "X", "O", "", "", ""]
    model.move(8)
    assert model.winner == "X"

def test_set_winner(model):
    model.board.squares = ["X", "X", "X", "", "", "", "", "", ""]
    model.set_winner()
    assert model.winner == "X"
    model = Model()
    model.board.squares = ["O", "", "", "O", "", "", "O", "", ""]
    model.set_winner()
    assert model.winner == "O"

    # reset winner to None
    model.winner = None
    model.board.squares = ["X", "O", "X", "O", "X", "O", "", "", ""]
    model.set_winner()
    assert model.winner is None

def test_get_current_player(model):
    assert model.get_current_player() == "X"
    model.player = "O"
    assert model.get_current_player() == "O"

def test_change_player(model):
    model.change_player()
    assert model.player == "O"
    model.change_player()
    assert model.player == "X"

def test_get_board_state(model):
    model.board.squares = ["X", "O", "X", "O", "X", "O", "", "", ""]
    assert model.get_board_state() == Board(["X", "O", "X", "O", "X", "O", "", "", ""])

def test_move_occupied(model):
    model.board.squares = ["X", "O", "X", "O", "X", "O", "", "", ""]
    with pytest.raises(ValueError,
                       match=SQUARE_OCCUPIED_ERROR_MSG):
        model.move(0)