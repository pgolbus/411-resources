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
    A class to manage a ring where boxers can enter and  fight.

    Attributes:
        ring (List[Boxer]): The list of boxers currently in the ring.

    """

    def __init__(self):
        """Initializes the RingModel with an empty ring.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a fight between the two boxers in the ring

        Calculate the fighting skill of the two boxers in the ring and determine the winner by comparing their normalized skill difference. The boxers' stats are then updated accordingly and the ring is cleared.

        Returns:
            str: Name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
            
        """
        logger.info("Starting a fight")

        if len(self.ring) < 2:
            logger.error("Failed to start a fight with fewer than two boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Match between {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.info(f"Fighting skills: {boxer_1.name}: {skill_1}, {boxer_2.name}: {skill_2}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.info(f"Normalized skill difference: {normalized_delta}")

        random_number = get_random()
        logger.info(f"Random number for calculating outcome: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"{winner.name} won against {loser.name}")

        logger.info("Updating stats for the boxers")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info("Finished updating stats for the boxers")

        logger.info("Fight ended, clearing the ring")
        self.clear_ring()
        logger.info("Finished clearing the ring")

        return winner.name
        logger.info("Winner name returned")

    def clear_ring(self):
        """Clears all boxers from the ring.

        Clears all boxerss from the ring. If the ring is already empty, logs a warning.

        """
        logger.info("Received request to clear the ring")

        if not self.ring:
            logger.warning("The ring is already empty")
            return

        self.ring.clear()
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If the ring already has two boxers and is full.

        """
        logger.info("Received request to add a boxer to the ring")

        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: Boxer is not a valid Boxer instance")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Failed to add a boxer because the ring is full")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Successfully added boxer {boxer.name} to the ring")

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of the boxers currently in the ring.

        Returns:
            List[Boxer]: A list of all boxers in the ring.

        """
        logger.info("Retrieving all boxers in the ring")

        if not self.ring:
            logger.warning("Ring is empty")
            pass
        else:
            logger.info(f"Retrieved {len(self.ring)} boxers")
            pass

        return self.ring
        logger.info("Successfully retrieved all boxers in the ring")

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on their attributes.

        Args:
            boxer (Boxer): The boxer whose fighting skill is to be calculated.

        Returns:
            float: The calculated fighting skill value.
        """
        logger.info(f"Calculating fighting skill for boxer {boxer.name}")

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Finished calculating fighting skill for {boxer.name}: {skill}")

        return skill
