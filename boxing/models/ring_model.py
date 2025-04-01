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
    A class to manage the boxing ring and simulate fights between boxers.

    The ring can hold up to two boxers at a time. Once two boxers are present,
    the `fight()` method can be used to simulate a match and determine a winner.

    Attributes:
        ring (List[Boxer]): The list of boxers currently in the ring (max 2).
    """
    def __init__(self):
        """
        Initializes the RingModel with an empty ring.

        The ring is represented as a list of Boxer objects.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in the ring and returns the winner's name.

        The outcome is probabilistic and depends on each boxer's computed skill score.
        The winner's and loser's stats are updated in the database accordingly.

        Returns:
            str: The name of the winning boxer.

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
        Clears the ring of all boxers.

        Does nothing if the ring is already empty.
        """
        if not self.ring:
            logger.info("Ring is already empty. Nothing to clear.")
            return
        
        logger.info("Clearing the ring of all boxers.")
        self.ring.clear()
        logger.info("Ring has been cleared.")

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the input is not a Boxer instance.
            ValueError: If the ring already contains two boxers.
        """

        logger.info(f"Attempting to add boxer to ring: {boxer}")

        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Ring is full, cannot add more boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} successfully entered the ring.")

    def get_boxers(self) -> List[Boxer]:
        """
        Retrieves the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The list of boxers in the ring.
        """
        if not self.ring:
            logger.info("No boxers currently in the ring.")
        else:
            logger.info(f"{len(self.ring)} boxer(s) currently in the ring: {[boxer.name for boxer in self.ring]}")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a boxer's fighting skill based on weight, name length, reach, and age.

        The formula used is:
            skill = (weight x name_length) + (reach ÷ 10) + age_modifier

        Where:
            - age_modifier is -1 if age < 25,
                              -2 if age > 35,
                              0 otherwise

        Args:
            boxer (Boxer): The boxer whose fighting skill is to be calculated.

        Returns:
            float: The calculated fighting skill score.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(
        f"Calculated skill for {boxer.name}: {skill:.2f} "
        f"(weight={boxer.weight}, name_length={len(boxer.name)}, "
        f"reach={boxer.reach}, age={boxer.age}, age_modifier={age_modifier})"
        )

        return skill