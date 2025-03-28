import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random

# Set up module-level logger
logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A model to simulate boxing matches between two boxers.

    Attributes:
        ring (List[Boxer]): A list holding up to two boxers for a fight
    """

    def __init__(self):
        """
        Initialize the RingModel to be empty
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between the two boxers in the ring

        Uses a logistic function to determine the outcome based on the the 
        fighting skills and updates their win/loss stats accordingly.

        Returns:
            str: The name of the winner

        Raises:
            ValueError: If there are less than two boxers in the ring.
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
        Clears the ring
        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add.

        Raises:
            TypeError: If the input is not a Boxer instance.
            ValueError: If the ring already has two boxers.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Retrieves the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The list of boxers (max of 2).
        """
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a fighting skill score based on the boxer's attributes.

        The score is based on weight, name length, reach, and age modifiers

        Args:
            boxer (Boxer): The boxer to evaluate the attributes of

        Returns:
            float: The skill score.
        """
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
