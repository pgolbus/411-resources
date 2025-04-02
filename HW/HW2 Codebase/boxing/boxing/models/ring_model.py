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
        # Initialize the ring with an empty list to hold up to two boxers
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        # Simulate a fight between the two boxers currently in the ring
        if len(self.ring) < 2:
            logger.error("Fight attempted with fewer than 2 boxers")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Fight between {boxer_1.name} and {boxer_2.name} started")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"Skill levels: {boxer_1.name} = {skill_1}, {boxer_2.name} = {skill_2}")

        # Compute the absolute skill difference and apply logistic normalization
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
        logger.debug(f"Random number: {random_number}, Normalized delta: {normalized_delta}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner is {winner.name}, Loser is {loser.name}")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        # Clears the ring of all boxers
        if not self.ring:
            logger.info("Ring is already empty")
            return
        logger.info("Clearing the ring")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        # Add a boxer to the ring
        if not isinstance(boxer, Boxer):
            logger.error(f"Attempted to enter non-Boxer type: {type(boxer).__name__}")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Ring is full, cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer {boxer.name} entered the ring")

    def get_boxers(self) -> List[Boxer]:
        # Retrieve current boxers in the ring
        if not self.ring:
            logger.warning("No boxers in the ring")
            raise ValueError("No boxers in the ring")
        else:
            logger.info(f"Current boxers in the ring: {[boxer.name for boxer in self.ring]}")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Compute a simplified fighting skill score based on boxer attributes
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for {boxer.name}: {skill}")
        return skill
