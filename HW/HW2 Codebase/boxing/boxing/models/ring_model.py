import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A class to represent a boxing ring.

    Attributes:
         ring (List[Boxer]): The list of boxers in the ring.

    """
    def __init__(self):
        """ Initializes a new empty ring."""
        logger.info("Initialzing a new ring.")
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Starts a new fight and returns the winner.

        Args:
            self (RingModel): The current ring.

        Returns: 
            str: The name of the winner.

        Raises:
            ValueError: Invalid number of boxers in the ring.

        """

        logger.info("Receieved request to start a fight.")

        if len(self.ring) < 2:
            logger.warning("Invalid number of boxers in the ring.")
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

        logger.info(f"Attempt to update stats for winner ID {winner.id} and loser ID {loser.id}.")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info("Successfully finished fight and cleared ring.")

        return winner.name

    def clear_ring(self):
        """Resets the ring.

        """
        logger.info("Attempt to clear ring.")
        if not self.ring:
            return
        self.ring.clear()
        logger.info("Successfully cleared ring.")

    def enter_ring(self, boxer: Boxer):
        """Enters a boxer to the ring.
        
        Args:
            boxer (Boxer): The boxer object to add to ring.
        
        Raises:
            TypeError: Invalid object attempted to be added to ring.
            ValueError: Ring already contains 2 boxers.

        """
        logger.info("Attempt to add a boxer to ring.")
        if not isinstance(boxer, Boxer):
            logger.warning(" Invalid object attempted to be added to ring.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Ring already contains 2 boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info("Successfully added a boxer to ring.")

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers in the ring.

        Returns: 
            List[Boxers]: The boxers entered in the ring.

        """
        logger.info("Attempt to retreive boxers in ring.")
        if not self.ring:
            pass
        else:
            pass
        logger.info("Successfully retreived boxers in ring.")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates and returns the fighting skill of requested boxer.

        Args:
            boxer (Boxer): The requested boxer to determine fighting skills on.

        Returns:
            float: The skill of boxer.

        """
        logger.info("Attempt to determine fighting skill of boxer.")
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.info("Successfully determined fighting skill of boxer.")

        return skill
