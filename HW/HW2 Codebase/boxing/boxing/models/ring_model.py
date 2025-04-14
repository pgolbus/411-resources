"""
Module for simulating boxing matches in a ring.

This module defines the RingModel class, which allows for adding boxers to the ring,
conducting a fight between two boxers, and computing the fight outcome based on their
calculated fighting skills. The module leverages logging for tracing execution, uses a
random number generator to simulate fight uncertainty, and updates boxer statistics
accordingly.
"""

import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """Model representing a boxing ring.

    This class manages a ring where boxers can enter, fight, and have their statistics updated.
    It provides methods to simulate a fight between two boxers, clear the ring after a fight,
    and compute a fighter's skill.
    """

    def __init__(self):
        """Initializes a new RingModel with an empty ring.

        Attributes:
            ring (List[Boxer]): A list holding the boxers currently in the ring.
        """
        self.ring: List[Boxer] = []
        logger.debug("RingModel initialized with an empty ring.")


    def fight(self) -> str:
        """Conducts a fight between two boxers in the ring.

        The method retrieves the two boxers, computes their fighting skills, and determines the winner
        based on a probabilistic model using a normalized logistic function and a random number.
        After the fight, it updates the boxer statistics and clears the ring.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        logger.info("Fight initiated.")

        if len(self.ring) < 2:
            logger.error("Fight cannot be started: less than two boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.debug(f"Boxers in ring: {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"Calculated fighting skills: {boxer_1.name}={skill_1}, {boxer_2.name}={skill_2}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug(f"Delta: {delta}, Normalized delta: {normalized_delta}")

        random_number = get_random()
        logger.debug(f"Random number generated: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Fight result: {winner.name} wins over {loser.name}.")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.debug("Boxer stats updated.")

        self.clear_ring()
        logger.info("Ring cleared after fight.")

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        If the ring is already empty, no action is taken.
        """
        if not self.ring:
            logger.debug("Clear ring called but the ring is already empty.")
            return
        self.ring.clear()
        logger.debug("Ring cleared successfully.")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring if space is available.

        Args:
            boxer (Boxer): The boxer that is entering the ring.

        Raises:
            TypeError: If the provided object is not an instance of Boxer.
            ValueError: If the ring already contains two boxers.
        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Ring is full, cannot add more boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Retrieves the boxers currently in the ring.

        Returns:
            List[Boxer]: The list of boxers in the ring.
        """
        if not self.ring:
            pass
        else:
            pass

        logger.debug(f"Retrieving boxers in ring: {len(self.ring)} found.")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Computes the fighting skill of a given boxer.

        Args:
            boxer (Boxer): The boxer whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Computed fighting skill for {boxer.name}: {skill}")

        return skill

