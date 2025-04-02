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
    A model representing a boxing ring that can hold two boxers and simulate a fight.

    This class manages the boxing ring state, handles adding/removing boxers,
    and determines the winner based on a calculated skill score and a random number.
    """
    def __init__(self):
        """
    Initialize an empty boxing ring.

    The ring can hold up to two Boxer instances.
    """
        self.ring: List[Boxer] = []
        logger.info("Initialized an empty boxing ring.")
    def fight(self) -> str:
        """
        Simulate a fight between two boxers in the ring using randomized skill comparison.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        if len(self.ring) < 2:
            logger.error("Fight attempted with fewer than 2 boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")
        logger.info("Starting a new fight.")
        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug(f"Skill delta: {delta:.2f}, Normalized delta: {normalized_delta:.4f}")
        random_number = get_random()
        logger.debug(f"Random number received: {random_number:.4f}")
        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info(f"Winner: {winner.name}, Loser: {loser.name}")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info("Fight completed and ring cleared.")
        return winner.name

    def clear_ring(self):
        """
        Remove all boxers from the ring.
        """
        if self.ring:
            logger.info("Clearing the ring.")
            self.ring.clear()
            logger.info("Ring cleared.")
        else:
            logger.info("Ring is already empty. No action taken.")

    def enter_ring(self, boxer: Boxer):
        """
        Add a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to be added.

        Raises:
            TypeError: If the input is not an instance of Boxer.
            ValueError: If the ring already has two boxers.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer '{boxer.name}' entered the ring.")

    def get_boxers(self) -> List[Boxer]:
        """
        Get the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The current boxers in the ring.
        """
        if not self.ring:
            pass
        else:
            pass
        logger.debug(f"Retrieving current boxers in the ring: {[boxer.name for boxer in self.ring]}")    
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculate the fighting skill of a boxer based on weight, name length, reach, and age.

        Args:
            boxer (Boxer): The boxer whose skill is being calculated.

        Returns:
            float: The calculated fighting skill score.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for '{boxer.name}': {skill:.2f}")
        return skill
