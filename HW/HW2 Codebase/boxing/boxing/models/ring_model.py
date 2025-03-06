import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A class to manage the the ring in which boxers have fights.

    Attributes:
        ring (List[Boxer]): The list of combatants in the battle.
    """

    def __init__(self):
        """Initializes the RingManager with an empty list of combatants.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a fight between two combatants.

        Simulates a fight between two combatants. Computes their fighting skill levels,
        normalizes the difference, and determines the winner based on a random number.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are not enough boxers in the ring.

        """
        if len(self.ring) < 2:
            logger.error("There must be two boxers to start a fight.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        logger.info(f"Fight started between {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        logger.debug(f"Fighting skill for {boxer_1.name}: {skill_1:.3f}")
        logger.debug(f"Fighting skill for {boxer_2.name}: {skill_2:.3f}")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        logger.debug(f"Raw delta between skills: {delta:.3f}")
        logger.debug(f"Normalized delta: {normalized_delta:.3f}")

        random_number = get_random()

        logger.debug(f"Random number from random.org: {random_number:.3f}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"The winner is: {winner.name}")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Clears the list of boxers.

        """
        if not self.ring:
            logger.warning("Attempted to clear an empty ring.")
            return
        logger.info("Clearing the boxers from the ring.")
        self.ring.clear()


    def enter_ring(self, boxer: Boxer):
        """Prepares a boxer by adding them to the ring for an upcoming fight.

        Args:
            boxer (Boxer): A Boxer dataclass instance representing the combatant.

        Raises:
            TypeError: If the input is not an instance of `Boxer`.
            ValueError: If the ring already has two boxers (fight is full).

        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error(f"Attempted to add boxer '{boxer.name}' but the ring is full")
            raise ValueError("Ring is full, cannot add more boxers.")

        logger.info(f"Adding boxer '{boxer.name}' to the ring")

        self.ring.append(boxer)

        logger.info(f"Current boxers in the ring: {[b.name for b in self.ring]}")


    def get_boxers(self) -> List[Boxer]:
        """Retrieves the current list of boxers in the ring.

        Returns:
            List[Boxer]: A list of Boxer dataclass instances representing the boxers in the ring.

        """
        if not self.ring:
            logger.warning("Retrieving boxers from an empty ring.")
        else:
            logger.info(f"Retrieving {len(self.ring)} boxers from the ring.")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill for a boxer based on arbitrary rules.

        The fighting skill is computed as:
        - Multiply the boxer's weight by the number of letters in their name.
        - Subtract an age modifier (if age < 25, subtract 1; if age > 35, subtract 2).
        - Add a reach bonus (reach / 10).

        Args:
            boxer (Boxer): A Boxer dataclass representing the combatant.

        Returns:
            float: The calculated fighting skill.

        """
        logger.info(f"Calculating fighting skill for {boxer.name}: weight={boxer.weight}, age={boxer.age}, reach={boxer.reach}")

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Fighting skill for {boxer.name}: {skill:.3f}")
        return skill
