# tests/test_ring_model.py

import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture
def boxer_1():
    return Boxer(id=1, name="Ali", weight=150, height=180, reach=75.0, age=30)


@pytest.fixture
def boxer_2():
    return Boxer(id=2, name="Tyson", weight=160, height=175, reach=72.0, age=28)


@pytest.fixture
def ring():
    return RingModel()


def test_enter_ring_success(ring, boxer_1, boxer_2):
    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)
    assert len(ring.get_boxers()) == 2


def test_enter_ring_too_many_boxers(ring, boxer_1, boxer_2):
    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)
    with pytest.raises(ValueError, match="Ring is full"):
        ring.enter_ring(boxer_1)


def test_enter_ring_invalid_type(ring):
    with pytest.raises(TypeError):
        ring.enter_ring("not_a_boxer")


def test_clear_ring(ring, boxer_1):
    ring.enter_ring(boxer_1)
    ring.clear_ring()
    assert len(ring.get_boxers()) == 0


def test_fight_less_than_two_boxers(ring, boxer_1):
    ring.enter_ring(boxer_1)
    with pytest.raises(ValueError, match="There must be two boxers"):
        ring.fight()


def test_fight_success(mocker, ring, boxer_1, boxer_2):
    mocker.patch("boxing.models.ring_model.get_random", return_value=0.2)
    mock_update = mocker.patch("boxing.models.ring_model.update_boxer_stats")

    ring.enter_ring(boxer_1)
    ring.enter_ring(boxer_2)

    winner = ring.fight()
    assert winner == boxer_1.name  # based on how skill comparison works
    assert mock_update.call_count == 2
    mock_update.assert_any_call(boxer_1.id, 'win')
    mock_update.assert_any_call(boxer_2.id, 'loss')




def test_get_fighting_skill(ring, boxer_1):
    skill = ring.get_fighting_skill(boxer_1)
    assert isinstance(skill, float)
