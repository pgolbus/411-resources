import pytest

from tictactoe import INVALID_MOVE_ERROR_MSG
from tictactoe.controller import validate_index


def test_validate_index():
    with pytest.raises(ValueError, match=INVALID_MOVE_ERROR_MSG):
        validate_index(-1)
    with pytest.raises(ValueError, match=INVALID_MOVE_ERROR_MSG):
        validate_index(9)
    with pytest.raises(ValueError, match=INVALID_MOVE_ERROR_MSG):
        validate_index("zero")
    validate_index(0)
    validate_index(8)