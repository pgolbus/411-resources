import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    def __init__(self):
        self.ring: List[Boxer] = []

    def fight(self) -> str:
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
        """Removes all boxers from the ring."""
        
        if not self.ring:
            return
        logger.info("ring is cleared now.")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the provided argument is not a Boxer instance.
            ValueError: If the ring is already full (contains two boxers).
        """
        
        logger.info("Received request to add a boxer to the ring")
        
        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: Boxer is not a valid Boxer instance")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error(f"Ring is full, cannot add more boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Successfully added boxer to ring: {boxer.id} - {boxer.name} ({boxer.age} years, {boxer.weight} pounds, {boxer.height} inches, {boxer.reach} inches)")

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers currently in the ring."""
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates a fighting skill score for a given boxer.

        The skill is calculated based on the boxer's weight, the length of their name,
        their reach, and their age.

        Args:
            boxer (Boxer): The Boxer instance for whom to calculate the skill.

        Returns:
            float: The calculated fighting skill score.
        """
        
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
