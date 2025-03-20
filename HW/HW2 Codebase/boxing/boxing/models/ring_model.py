import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage boxing matches in a ring with boxers.

    Attributes:
        ring (List[Boxer]): A list of Boxers currently in the ring.
    """
    def __init__(self):
        """Initializes the RingModel with an empty ring with no boxers in it.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Organizes a fight between two boxers in the ring and updates their stats based on the result.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are less than two boxers in the ring.
            sqlite3.Error: If any database error occurs during the update.
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
        """ Clears the ring of all boxers
        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring if there is space.

        Args:
            boxer (Boxer): The boxer to be added to the ring.

        Raises:
            TypeError: If the object provided is not an instance of Boxer.
            ValueError: If the ring is already full (has 2 boxers).
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The boxers in the ring.
        """
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on their attributes.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The skill of the boxer.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
