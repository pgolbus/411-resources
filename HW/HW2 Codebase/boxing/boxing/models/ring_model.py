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
    A class to manage a boxing ring and fights between boxers.

    Attributes:
        ring (List[Boxer]): The list of boxers currently in the ring.
    """
    
    def __init__(self):
        """Initializes the RingModel with an empty ring.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a fight between two boxers in the ring.
        
        Returns:
            str: The name of the winning boxer.
            
        Raises:
            ValueError: If there are not exactly two boxers in the ring.
        """
        if len(self.ring) < 2:
            logger.error("Cannot start fight: Not enough boxers in the ring")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Starting fight between {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"Fighting skills: {boxer_1.name}={skill_1}, {boxer_2.name}={skill_2}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug(f"Normalized skill difference: {normalized_delta}")

        random_number = get_random()
        logger.debug(f"Random number: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner: {winner.name}")
        
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.
        
        If the ring is already empty, no action is taken.
        """
        if not self.ring:
            logger.debug("Ring is already empty")
            return
        
        logger.info("Clearing the ring")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.
        
        Args:
            boxer (Boxer): The boxer to add to the ring.
            
        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If the ring is already full (has 2 boxers).
        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid boxer type: {type(boxer).__name__}")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Ring is full, cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        logger.info(f"Boxer {boxer.name} is entering the ring")
        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of all boxers currently in the ring.
        
        Returns:
            List[Boxer]: The boxers in the ring.
        """
        logger.debug(f"Getting boxers from the ring. Count: {len(self.ring)}")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on their attributes.
        
        Args:
            boxer (Boxer): The boxer to evaluate.
            
        Returns:
            float: A numerical value representing the boxer's fighting skill.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        
        logger.debug(f"Calculated fighting skill for {boxer.name}: {skill}")
        return skill
