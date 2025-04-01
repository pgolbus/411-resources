import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A model representing a boxing ring where two boxers can fight.

    Attributes:
        ring (List[Boxer]): A list of boxers currently in the ring.
    """

    def __init__(self):
        """Initializes an empty ring."""
        self.ring: List[Boxer] = []
        logger.info("RingModel initialized with an empty ring.")

    def fight(self) -> str:
        """Simulates a fight between two boxers in the ring.

        The winner is determined by comparing their fighting skills, which are calculated
        based on their attributes. A random number is used to introduce variability in the outcome.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        if len(self.ring) < 2:
            logger.error("Attempted to start a fight with fewer than two boxers.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Starting fight between {boxer_1.name} and {boxer_2.name}.")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"Fighting skills calculated: {boxer_1.name} ({skill_1}), {boxer_2.name} ({skill_2}).")

        # Compute the absolute skill difference and normalize it
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug(f"Normalized skill difference: {normalized_delta}.")

        random_number = get_random()
        logger.debug(f"Random number generated: {random_number}.")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner: {winner.name}.")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info(f"Updated stats for {winner.name} (win) and {loser.name} (loss).")

        self.clear_ring()
        logger.info("Ring cleared after the fight.")

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        If the ring is already empty, no action is taken.
        """
        if not self.ring:
            logger.debug("Ring is already empty.")
            return

        self.ring.clear()
        logger.info("Ring cleared.")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the provided object is not an instance of `Boxer`.
            ValueError: If the ring is already full (contains two boxers).
        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type provided: Expected 'Boxer', got '{type(boxer).__name__}'.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Attempted to add a boxer to a full ring.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} entered the ring.")

    def get_boxers(self) -> List[Boxer]:
        """Retrieves the boxers currently in the ring.

        Returns:
            List[Boxer]: A list of boxers in the ring.
        """
        if not self.ring:
            logger.debug("No boxers in the ring.")
            pass
        else:
            logger.debug(f"Retrieved {len(self.ring)} boxers from the ring.")
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on their attributes.

        The skill is calculated using the boxer's weight, name length, reach, and age.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill.
        """
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated fighting skill for {boxer.name}: {skill}.")
        return skill