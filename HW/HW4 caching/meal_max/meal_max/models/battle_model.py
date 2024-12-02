import logging
import os
import time
from typing import Any, List

from meal_max.models.kitchen_model import Meals
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


TTL = os.getenv("TTL", 60)  # Default TTL is 60 seconds


class BattleModel:
    """
    A class to manage the battle between two combatants.

    Attributes:
        combatants (List[dict[str, Any]]): The list of combatants in the battle.
        combatant_ttls (dict[int, int]): A dictionary to store TTL for each combatant.
        meals_cache (dict[int, dict[str, Any]]): A dictionary to cache meal data by ID.
    """

    def __init__(self):
        """Initializes the BattleManager with an empty list of combatants and TTL."""
        self.combatants: List[int] = []  # List of active combatants
        self.combatant_ttls: dict[int, int] = {}  # Dictionary to store TTL for each combatant
        self.meals_cache: dict[int, dict[str, Any]] = {}  # Cache of meal data by ID

    def battle(self) -> str:
        """
        Simulates a battle between two combatants.

        Simulates a battle between two combatants. Computes their battle scores,
        normalizes the delta between the scores, and determines the winner
        based on a random number from random.org.

        Returns:
            str: The name of the winning combatant (meal).
        """
        logger.info("Two meals enter, one meal leaves!")

        if len(self.combatants) < 2:
            logger.error("Not enough combatants to start a battle.")
            raise ValueError("Two combatants must be prepped for a battle.")

        # Refresh combatants' data if TTLs have expired
        for meal_id in self.combatants:
            if time.time() > self.combatant_ttls.get(meal_id, 0):  # Check TTL expiration
                # Fetch latest data and update cache
                logger.info("Cache expired for meal ID %s, refreshing cache.", meal_id)
                updated_meal = Meals.get_meal_by_id(meal_id)
                self.combatant_ttls[meal_id] = time.time() + TTL  # Reset TTL
                self.meals_cache[meal_id] = updated_meal

        combatant_1 = self.meals_cache[self.combatants[0]]
        combatant_2 = self.meals_cache[self.combatants[1]]

        # Log the start of the battle
        logger.info("Battle started between %s and %s", combatant_1["meal"], combatant_2["meal"])

        # Get battle scores for both combatants
        score_1 = self.get_battle_score(combatant_1)
        score_2 = self.get_battle_score(combatant_2)

        # Log the scores for both combatants
        logger.info("Score for %s: %.3f", combatant_1["meal"], score_1)
        logger.info("Score for %s: %.3f", combatant_2["meal"], score_2)

        # Compute the delta and normalize between 0 and 1
        delta = abs(score_1 - score_2) / 100

        # Log the delta and normalized delta
        logger.info("Delta between scores: %.3f", delta)

        # Get random number from random.org
        random_number = get_random()

        # Log the random number
        logger.info("Random number from random.org: %.3f", random_number)

        # Determine the winner based on the normalized delta
        if delta > random_number:
            winner = combatant_1
            loser = combatant_2
        else:
            winner = combatant_2
            loser = combatant_1

        # Log the winner
        logger.info("The winner is: %s", winner["meal"])

        # Update stats for both combatants
        Meals.update_meal_stats(winner["id"], 'win')
        Meals.update_meal_stats(loser["id"], 'loss')

        # Remove the losing combatant from combatants
        self.combatants.remove(loser["id"])

        return winner["meal"]

    def clear_combatants(self):
        """
        Clears the list of combatants.
        """
        logger.info("Clearing the combatants list.")
        self.combatants.clear()

    def get_battle_score(self, combatant: dict[str, Any]) -> float:
        """
        Calculates the battle score for a combatant based on the price and difficulty of the meal.

        Calculates the battle score for a combatant based on the following rule:
        - Multiply the price by the number of letters in the cuisine.
        - Subtract a difficulty modifier (HIGH = 1, MED = 2, LOW = 3).

        Args:
            combatant (dict[str, Any]): A dict representing the combatant.

        Returns:
            float: The calculated battle score.
        """
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

        # Log the calculation process
        logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
                    combatant["meal"], combatant["price"], combatant["cuisine"], combatant["difficulty"])

        # Calculate score
        score = (combatant["price"] * len(combatant["cuisine"])) - difficulty_modifier[combatant["difficulty"]]

        # Log the calculated score
        logger.info("Battle score for %s: %.3f", combatant["meal"], score)

        return score

    def get_combatants(self) -> List[dict[str, Any]]:
        """
        Retrieves the current list of combatants for a battle.

        Returns:
            List[dict[str, Any]]: A list of dicts representing combatants.
        """
        logger.info("Retrieving current list of combatants.")
        return self.combatants

    def prep_combatant(self, combatant_data: dict[str, Any]):
        """
        Prepares a combatant by adding it to the combatants list for an upcoming battle.

        Args:
            combatant_data (dict[str, Any]): A dict containing the combatant details.

        Raises:
            ValueError: If the combatants list already has two combatants (battle is full).
        """
        if len(self.combatants) >= 2:
            logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data["meal"])
            raise ValueError("Combatant list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", combatant_data["meal"])

        id = combatant_data["id"]
        self.combatants.append(id)
        self.meals_cache[id] = combatant_data
        self.combatant_ttls[id] = time.time() + TTL

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [self.meals_cache[combatant]["meal"] for combatant in self.combatants])