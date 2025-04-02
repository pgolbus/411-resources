import logging
import math
from typing import List

"""
This module provides functionality for managing fights in the boxing ring.
It includes the RingModel class which handles boxer entries, initiates fights,
clears the ring, and computes fighting skills for boxers.
Detailed logging is implemented for debugging and tracing fight execution.
"""

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)

# Class: RingModel
# Purpose: Manages the boxing ring by handling boxer entries, initiating fights,
# and maintaining the current state of the ring.
class RingModel:
    def __init__(self):
        self.ring: List[Boxer] = []
        # Initialize an empty ring for boxers.

    # Method: fight
    # Purpose: Simulates a fight between two boxers present in the ring.
    # Returns the name of the winning boxer.
    def fight(self) -> str:
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")
        logger.info(f"Starting fight with {len(self.ring)} boxers in the ring.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.info(f"Computed skills: {boxer_1.name} -> {skill_1}, {boxer_2.name} -> {skill_2}. Delta: {delta}, Normalized Delta: {normalized_delta}")

        random_number = get_random()
        logger.info(f"Random number generated: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info(f"Fight outcome determined: Winner - {winner.name}, Loser - {loser.name}")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info("Updating boxer statistics completed. Clearing the ring.")

        self.clear_ring()

        return winner.name

    # Method: clear_ring
    # Purpose: Clears the ring of all boxers.
    def clear_ring(self):
        logger.info("Attempting to clear the ring.")
        if not self.ring:
            logger.info("Ring is already empty, nothing to clear.")
            return
        self.ring.clear()
        logger.info("Ring cleared successfully.")

    # Method: enter_ring
    # Purpose: Allows a boxer to enter the ring if space is available and the input is valid.
    def enter_ring(self, boxer: Boxer):
        logger.info(f"Boxer {boxer} attempting to enter the ring.")
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} entered the ring successfully.")

    # Method: get_boxers
    # Purpose: Returns the list of boxers currently in the ring.
    def get_boxers(self) -> List[Boxer]:
        logger.info(f"Returning list of boxers in the ring: {self.ring}")
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    # Method: get_fighting_skill
    # Purpose: Computes the fighting skill for a given boxer based on weight, reach, and age.
    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Calculated fighting skill for boxer {boxer.name}: {skill}")
        return skill
