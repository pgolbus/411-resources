import logging
import math
import os
import time
from typing import List, Dict, Optional
from threading import Lock  # Import the Lock

from boxing.models.boxers_model import Boxers
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A class to manage the the ring in which boxers have fights.
    """

    def __init__(self):
        """Initializes the RingManager with an empty list of combatants.
        """
        self.ring: List[int] = []
        self._boxer_cache: Dict[int, Boxers] = {}
        self._ttl: Dict[int, float] = {}
        self.ttl_seconds: int = int(os.getenv("TTL_SECONDS", 60))
        self._cache_lock = Lock()  # Initialize the lock

    def fight(self) -> str:
        """Simulates a fight between two combatants.
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

        winner.update_stats('win')
        loser.update_stats('loss')

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
        self.clear_cache()  # Clear the cache when the ring is cleared

    def enter_ring(self, boxer_id: int):
        """Prepares a boxer by adding them to the ring for an upcoming fight.
        """
        if len(self.ring) >= 2:
            logger.error(f"Attempted to add boxer ID {boxer_id} but the ring is full")
            raise ValueError("Ring is full")  # Added raise

        try:
            boxer = Boxers.get_boxer_by_id(boxer_id)
        except ValueError as e:
            logger.error(str(e))
            raise  # Re-raise the ValueError

        logger.info(f"Adding boxer '{boxer.name}' (ID {boxer_id}) to the ring")
        self.ring.append(boxer_id)  # Append the ID, not the boxer object

        logger.info(f"Current boxers in the ring: {[Boxers.get_boxer_by_id(b).name for b in self.ring]}")

    def get_boxers(self) -> List[Boxers]:
        """Retrieves the current list of boxers in the ring, using the cache when available."""
        boxers: List[Boxers] = []
        now = time.time()

        for boxer_id in self.ring:
            with self._cache_lock:  # Acquire lock for thread safety
                if boxer_id in self._boxer_cache and self._ttl.get(boxer_id, 0) > now:
                    logger.debug(f"Using cached boxer with ID {boxer_id}")
                    boxers.append(self._boxer_cache[boxer_id])
                    continue  # Important: Continue to the next boxer_id

            logger.info(f"Fetching boxer with ID {boxer_id} from DB")
            try:
                boxer = Boxers.get_boxer_by_id(boxer_id)
                with self._cache_lock:  # Acquire lock before updating cache
                    self._boxer_cache[boxer_id] = boxer
                    self._ttl[boxer_id] = now + self.ttl_seconds
                boxers.append(boxer)
            except ValueError as e:
                logger.warning(f"Boxer with ID {boxer_id} not found: {e}")
                # Handle missing boxer:  Remove from ring, raise, or skip.
                self.ring.remove(boxer_id)  # Remove from the ring
                logger.warning(
                    f"Boxer with ID {boxer_id} removed from ring because it was not found in DB."
                )
        logger.info(f"Retrieved {len(boxers)} boxers for the ring.")
        return boxers

    def get_fighting_skill(self, boxer: Boxers) -> float:
        """Calculates the fighting skill for a boxer based on arbitrary rules.
        """
        logger.info(
            f"Calculating fighting skill for {boxer.name}: weight={boxer.weight}, age={boxer.age}, reach={boxer.reach}"
        )

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Fighting skill for {boxer.name}: {skill:.3f}")
        return skill

    def clear_cache(self):
        """Clears the local cache of boxer objects and their TTLs."""
        logger.info("Clearing local boxer cache in RingModel.")
        with self._cache_lock:  # Acquire lock before clearing
            self._boxer_cache.clear()
            self._ttl.clear()