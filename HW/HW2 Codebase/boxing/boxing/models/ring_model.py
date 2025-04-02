import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A model representing a boxing ring that manages fights between two boxers"""

    def __init__(self):
        """Initializes an empty ring"""
        self.ring: List[Boxer] = []
        logger.info("Initialized an empty ring")

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in the ring.

        Uses logistic function to normalize skill differences. Then it compares to determine who wins.

        Returns:
            str: The name of the winner

        Raises:
            ValueError: If fewer then two boxers are in the ring.
        """
        logger.info("Starting a fight between two boxers")

        if len(self.ring) < 2:
            logger.error("Attempted to start a fight with fewer than two boxers")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.debug(f"Boxers in ring: {boxer_1.name} vs {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"{boxer_1.name}'s skill: {skill_1}, {boxer_2.name}'s skill: {skill_2}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
        logger.debug(f"Delta: {delta}, Normalized delta: {normalized_delta}, Random number: {random_number}")


        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"{winner.name} wins the fight against {loser.name}")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info("Ring cleared after fight")

        return winner.name

    def clear_ring(self):
        """
        Clears all boxers from the ring

        If it is already empty it won't do anything
        """
        logger.info("Attempting to clear a ring")
        if not self.ring:
            logger.warning("Attempted to clear an already empty ring")
            return
        self.ring.clear()
        logger.info("Ring cleared")

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring if space is available.

        Args:
            boxer (Boxer): The boxer to enter the ring.

        Raises:
            TypeError: If the input is not a Boxer instance.
            ValueError: If the ring already has two boxers.
        """
        logger.info(f"Attempting to enter boxer {boxer.name} into the ring")
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Rign is full, cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} has entered the ring")

    def get_boxers(self) -> List[Boxer]:
        """
        Returns the current boxers in the ring.

        Returns:
            List[Boxer]: A list of boxers currently in the ring.
        """
        logger.info("Retrieving current boxers in the ring")

        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a boxer's fighting skill based on its attributes.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill score.
        """

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for {boxer.name}: {skill}")

        return skill
