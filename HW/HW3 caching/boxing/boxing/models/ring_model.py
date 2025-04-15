import logging
import math
import os
import time
from typing import List

from boxing.models.boxers_model import Boxers
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """A class to manage the the ring in which boxers have fights.

    """

    #TODO: IMPLEMENT###########################################################
    def __init__(self):
        """Initializes the RingManager with an empty list of combatants.

        The ring is initially empty, and the boxer cache and time-to-live (TTL) caches are also initialized.
        The TTL is set to 60 seconds by default, but this can be overridden by setting the TTL_SECONDS environment variable.

        Attributes:
            ring (List[int]): The list of ids of the boxers in the ring.
            _boxer_cache (dict[int, Boxers]): A cache to store boxer objects for quick access.
            _ttl (dict[int, float]): A cache to store the time-to-live for each boxer.
            ttl_seconds (int): The time-to-live in seconds for the cached boxer objects.

        """
        self.ring: List[int] = []
        self._boxer_cache: dict[int, Boxers] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))  # Default TTL is 60 seconds

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

    #TODO: IMPLEMENT###########################################################
    def enter_ring(self, boxer_id: int):
        """Prepares a boxer by adding them to the ring for an upcoming fight.

        Args:
            boxer_id (int): The ID of the boxer to enter the ring.

        Raises:
            ValueError: If the ring already has two boxers (fight is full).
            ValueError: If the boxer ID is invalid or the boxer does not exist.

        """
        logger.info(f"Received request to add Boxer with ID {boxer_id} to the ring")

        if len(self.ring) >= 2:
            logger.error(f"Attempted to add boxer ID {boxer_id} but the ring is full")
            raise ValueError("Ring is full")

        try:
            boxer = Boxers.get_boxer_by_id(boxer_id)
        except ValueError as e:
            logger.error(str(e))
            raise
        
        if boxer_id in self.ring:
            logger.warning(f"Boxer ID {boxer_id} is already in the ring.")
            return

        logger.info(f"Adding boxer '{boxer.name}' (ID {boxer_id}) to the ring")
        logger.info(f"Current boxers in the ring: {[Boxers.get_boxer_by_id(b).name for b in self.ring]}")
        self.ring.append(boxer_id)

    #TODO: IMPLEMENT###########################################################
    def get_boxers(self) -> List[Boxers]:
        """Retrieves the current list of boxers in the ring.

        Returns:
            List[Boxers]: A list of Boxers dataclass instances representing the boxers in the ring.

        """
        if not self.ring:
            logger.warning("Retrieving boxers from an empty ring.")
        else:
            logger.info(f"Retrieving {len(self.ring)} boxers from the ring.")

        boxers: List[Boxers] = [] # this is the get from cache or db implementation, we should be calling this from another method
    
        for boxer_id in self.ring:
            boxers.append(self._get_boxer_from_cache_or_db(boxer_id))
            # try:
            #     boxer = Boxers.get_boxer_by_id(boxer_id)
            #     boxers.append(boxer)
            # if expired:
            #     logger.info(f"TTL expired or missing for boxer {boxer_id}. Refreshing from DB.")
            # else:
            #     logger.debug(f"Using cached boxer {boxer_id} (TTL valid).")

        logger.info(f"Retrieved {len(boxers)} boxers from the ring.")
        
        return boxers
    
    def _get_boxer_from_cache_or_db(self, boxer_id: int) -> Boxers:
        """
        Retrieves a boxer by ID, using the internal cache if possible.

        This method checks whether a cached version of the song is available
        and still valid. If not, it queries the database, updates the cache, and returns the song.

        Args:
            boxer_id (int): The unique ID of the boxer to retrieve.

        Returns:
            Boxers: The boxer object corresponding to the given ID.

        Raises:
            ValueError: If the boxer cannot be found in the database.
        """
        now = time.time()

        if boxer_id in self._boxer_cache and self._ttl.get(boxer_id, 0) > now:
            logger.debug(f"Boxer ID {boxer_id} retrieved from cache")
            return self._boxer_cache[boxer_id]

        try:
            song = Boxers.get_boxer_by_id(boxer_id)
            logger.info(f"Boxer ID {boxer_id} loaded from DB")
        except ValueError as e:
            logger.error(f"Boxer ID {boxer_id} not found in DB: {e}")
            raise ValueError(f"Boxer ID {boxer_id} not found in database") from e

        self._boxer_cache[boxer_id] = song
        self._ttl[boxer_id] = now + self.ttl_seconds
        return song


    def get_fighting_skill(self, boxer: Boxers) -> float:
        """Calculates the fighting skill for a boxer based on arbitrary rules.

        The fighting skill is computed as:
        - Multiply the boxer's weight by the number of letters in their name.
        - Subtract an age modifier (if age < 25, subtract 1; if age > 35, subtract 2).
        - Add a reach bonus (reach / 10).

        Args:
            boxer (Boxers): A Boxers dataclass representing the combatant.

        Returns:
            float: The calculated fighting skill.

        """
        logger.info(f"Calculating fighting skill for {boxer.name}: weight={boxer.weight}, age={boxer.age}, reach={boxer.reach}")

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info(f"Fighting skill for {boxer.name}: {skill:.3f}")
        return skill

    #TODO: IMPLEMENT###########################################################
    def clear_cache(self):
        """Clears the local TTL cache of boxer objects.

        """
        logger.info("Clearing local boxer cache in RingModel.")

        if not self._boxer_cache and not self._ttl:
            logger.debug("Boxer cache and TTL already empty.")
            return

        self._boxer_cache.clear()
        self._ttl.clear()
        logger.info("Successfully cleared boxer cache and TTLs.")

