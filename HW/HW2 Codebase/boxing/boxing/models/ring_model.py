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
    A class to manage ring properties.

    Attributes:
        ring (List[Boxer]): Boxers slated to fight in the ring.

    """
    def __init__(self):
        """Initializes the RingModel with an empty list of fighters.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Initializes fighters and projected result.

        Attributes:
            boxer_1, boxer_2 (Boxer): gets boxers in the fight
            skill_1 (int): Gets skill index of boxer_1
            skill_2 (int): Gets skill index of boxer_2
            delta (float): difference in skill between boxers
            normalized_delta (float): normalized delta
            winner (str): winning boxer
            loser (str): losing boxer

        Raises:
            ValueError:  If there are less than two boxers in the fight.

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
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Enters a boxer in the ring.

        Args:
            boxer (Boxer): input boxer

        Raises:
            TypeError: Input was not a boxer.
            ValueError: If the ring is full and a boxer tries to enter.

        """
        logger.info(f"Attempting to enter {boxer.name} into the ring.")
        if not isinstance(boxer, Boxer):
            logger.warning(f"Cannot enter {boxer.name}")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning(f"Cannot enter {boxer.name}")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Boxer '{boxer.name}' is now in the ring.")

    def get_boxers(self) -> List[Boxer]:
        """ Get boxers
        """
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """ Calculates fighting skill of a boxer

        Args:
            boxer (Boxer): Input boxer

        Attributes:
            age_modifer (int): calculates a modifier that affects skill value
            skill (int): Calculated skill of a fighter
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
