"""
Module for simulating boxing matches in a ring.

This module defines the RingModel class, which allows for adding boxers to the ring,
conducting a fight between two boxers, and computing the fight outcome based on their
calculated fighting skills. The module leverages logging for tracing execution, uses a
random number generator to simulate fight uncertainty, and updates boxer statistics
accordingly.
"""

import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """Model representing a boxing ring.

    This class manages a ring where boxers can enter, fight, and have their statistics updated.
    It provides methods to simulate a fight between two boxers, clear the ring after a fight,
    and compute a fighter's skill.
    """

    def __init__(self):
        """Initializes a new RingModel with an empty ring.

        Attributes:
            ring (List[Boxer]): A list holding the boxers currently in the ring.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Conducts a fight between two boxers in the ring.

        The method retrieves the two boxers, computes their fighting skills, and determines the winner
        based on a probabilistic model using a normalized logistic function and a random number.
        After the fight, it updates the boxer statistics and clears the ring.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        If the ring is already empty, no action is taken.
        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
