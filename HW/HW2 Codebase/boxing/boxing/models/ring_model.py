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
    A class to manage a ring with boxers.

    Attributes:
        ring (List[Boxer]): The list of boxers in the ring.

    """
    def __init__(self):
    """initialize to an empti ring
    """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
            """determine a fight outcome.

        Args:
            self (Boxer): The boxer fighting.

        Returns: 
            name of the winner (str)

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
        """Clears boxers from ring. Logs a warning if the ring is already empty.

        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer enterering the ring.

        Raises:
            TypeError: If the boxer is not a valid instance.
            ValueError: If the ring is full.

        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of boxers in the ring.

        Returns:
            List[Boxer]: A list of all boxers currently in the ring.

        Raises:
            ValueError: If the ring is empty.

        """
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Returns the boxers skill rating.

        Returns:
            float: The the quantifled skill value of boxer.

        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
