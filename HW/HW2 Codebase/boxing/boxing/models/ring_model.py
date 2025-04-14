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
    A class to manage boxing matches between two boxers in the ring.

    Attributes:
        ring (List[Boxer]): The list of boxers currently in the ring.
    """
    def __init__(self):
        """Initializes the RingModel with an empty ring."""
        logger.info("Initializing an empty ring")
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a boxing match between two boxers currently in the ring.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.

        """
        if len(self.ring) < 2:
            logger.warning("Attempted to start a fight with fewer than two boxers")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Match setup: {boxer_1.name} vs {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"Calculated skills of opposing boxers - {boxer_1.name}: {skill_1}, {boxer_2.name}: {skill_2}")
        
        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug(f"Skill delta: {delta}, normalized skill delta: {normalized_delta}")

        random_number = get_random()
        logger.debug(f"Random number generated: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner: {winner.name}, Loser: {loser.name}")
        
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        logger.info(f"Updated stats: win added for {winner.name}, loss added for {loser.name}")
        
        self.clear_ring()
        logger.debug("Ring cleared after the match")
        
        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        If the ring is already empty, does nothing.
        """
        if not self.ring:
            logger.info("The ring is already empty! We don't need to clear")
            return

        logger.info("Clearing all boxers from the ring")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to enter the ring.

        Raises:
            TypeError: If the provided object is not a Boxer instance.
            ValueError: If the ring already has two boxers.

        """

        logger.info(f"Attempting to add to ring boxer: {getattr(boxer, 'name', 'Unknown')}")
        
        if not isinstance(boxer, Boxer):
            logger.warning(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Cannot add a third boxer to the ring")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} added to the ring")

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers currently in the ring.

        Returns:
            List[Boxer]: A list of Boxer instances currently in the ring.

        """
        logger.info(f"Getting list of boxers in the ring: {[boxer.name for boxer in self.ring]}")
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer.

        The skill is based on the boxer's weight, name length, reach, and an age-based modifier.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill of the boxer.

        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        logger.debug(f"Skill for {boxer.name} → weight: {boxer.weight}, reach: {boxer.reach}, age: {boxer.age}, modifier: {age_modifier}, final skill: {skill}")
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
