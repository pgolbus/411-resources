import math
import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

# Test that a fight cannot be initiated with fewer than two boxers.
def test_fight_insufficient_boxers():
    ring = RingModel()
    # Add only one boxer
    boxer = Boxer(1, "Boxer A", 160, 66, 24, 21)
    ring.enter_ring(boxer)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring.fight()

# Test that only Boxer instances can enter the ring.
def test_enter_ring_invalid_boxer():
    ring = RingModel()
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer'"):
        ring.enter_ring("Not a Boxer")

# Test that the ring refuses more than two boxers.
def test_enter_ring_when_full():
    ring = RingModel()
    boxer1 = Boxer(1, "Boxer A", 160, 66, 24, 21)
    boxer2 = Boxer(2, "Boxer B", 150, 65, 22, 25)
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring.enter_ring(Boxer(3, "Boxer C", 155, 67, 23, 23))

# Test that clear_ring properly clears the ring.
def test_clear_ring():
    ring = RingModel()
    boxer = Boxer(1, "Boxer A", 160, 66, 24, 21)
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1
    ring.clear_ring()
    assert len(ring.ring) == 0

# Test that get_boxers returns the current ring list.
def test_get_boxers():
    ring = RingModel()
    # Initially the ring is empty.
    assert ring.get_boxers() == []
    # Add a boxer and test that get_boxers returns it.
    boxer = Boxer(1, "Boxer A", 160, 66, 24, 21)
    ring.enter_ring(boxer)
    assert ring.get_boxers() == [boxer]

# Test a successful fight.
def test_fight_success(monkeypatch):
    # Prepare a ring with two boxers.
    ring = RingModel()
    boxer1 = Boxer(1, "Boxer A", 160, 66, 24, 21)
    boxer2 = Boxer(2, "Boxer B", 150, 65, 22, 25)
    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    # Patch get_random to always return 0.0.
    def fake_get_random():
        return 0.0

    # Patch update_boxer_stats so we don't perform any external operations.
    def fake_update_boxer_stats(boxer_id, result):
        return None

    monkeypatch.setattr("boxing.models.ring_model.get_random", fake_get_random)
    monkeypatch.setattr("boxing.models.ring_model.update_boxer_stats", fake_update_boxer_stats)

    # With the current skills, the fight should pick boxer1 as the winner.
    # Calculate normalized_delta:
    # For Boxer A: skill = (160 * len("Boxer A")) + (24/10) + (-1) = 160*7 + 2.4 - 1 ≈ 1121.4
    # For Boxer B: skill = (150 * len("Boxer B")) + (22/10) + 0 = 150*7 + 2.2 ≈ 1052.2
    # Since delta is large, normalized_delta ~ 1, so with 0.0 < 1, boxer1 wins.
    winner_name = ring.fight()
    assert winner_name == "Boxer A"
    # After the fight, the ring should be cleared.
    assert len(ring.ring) == 0