import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """ A class to manage a ring where two boxers can enter.

    Attributes:
        ring (List[Boxer]): A list containing the boxers currently in the ring.

    """


    def __init__(self):
       """ Intializes an empty boxing ring."""

        self.ring: List[Boxer] = []
        logger.info("RingModel initialized with an empty ring.")

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in the ring.
            
        Args:
            boxer1 (Boxer): The first boxer added to the ring.
            boxer2 (boxer): the second boxer added to the ring.

        Raises:
            ValueError: IF there are fewer than 2 boxers in the ring.
        
        Returns:
            The name of the winning Boxer.
        """

        if len(self.ring) < 2:
             logger.error("Attempted to start a fight with fewer than two boxers.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        logger.info(f"Starting fight between {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        logger.debug(f"{boxer_1.name}'s skill: {skill_1}, {boxer_2.name}'s skill: {skill_2}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
         logger.debug(f"Random number generated: {random_number}, Normalized delta: {normalized_delta}")

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

        return winner.name

    def clear_ring(self):
        """ 
        Removes all boxers from the ring.
        
        If the ring is empty, then a warning is logged.

        """
        if not self.ring:
            logger.warning("Attempted to clear an empty ring.")
            return
        
        logger.info("Clearing the ring")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args: boxer (Boxer): The boxer that is entering the ring.

        Raises:
           TypeError: If the input is not a 'Boxer' instance.
           ValueError: If the ring already has two boxers.

        """

        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Attempted to enter a full ring.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
         logger.info(f"Boxer {boxer.name} entered the ring.")

    def get_boxers(self) -> List[Boxer]:    
        """
        Returns the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The active boxers in the ring.

        """

        if not self.ring:
            logger.warning("No boxers found in the ring.")
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations

        """

        Calculates teh boxer's fighting skills based on weight, reach, and age.

        Args:
            boxer (Boxer): The boxer whose skill is being calculated.

        Returns:
            (float): The calculated skill level.

        """
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.debug(f"Computed skill for {boxer.name}: {skill}")
        return skill
