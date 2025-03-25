import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)

# using Google style Docstrings for ring_model
class RingModel:
    def __init__(self):
        """
        Initialize a new RingModel with an empty list of boxers in the ring.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        simulates a fight between the two boxers that is currently in the ring.

        The winner is chosen based on a simple skill formula and 
        a random chance component. After the fight, the winner and
        lose boxer’s stats are updated, and the ring is cleared.

        Returns:
            str:The name of the boxer who won the fight.

        Raises:
            ValueError: If fewer than two boxers are in the ring.
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
        """
        Removes all the boxers from the ring.
        Resets the ring so a new match can be set up.
        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring for a future fight.

        Args:
            boxer (Boxer): The boxer who is entering the ring.

        Raises:
            TypeError: If the argument is not a Boxer.
            ValueError: If the ring is full (already has two boxers).
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Returns the current list of boxers in the ring.

        If the ring is empty, returns an empty list.

        Returns:
            List[Boxer]: One or two boxers currently in the ring.
        """
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a boxer’s fighting skill based on weight, reach, name length, and age.

        This is an arbitrary formula used to give each boxer a numeric skill value
        for comparison during fights.

        Args:
            boxer (Boxer): The boxer whose skill is being measured.

        Returns:
            float: The calculated fighting skill value.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
