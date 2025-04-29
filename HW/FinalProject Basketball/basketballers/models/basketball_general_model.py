import logging
import math
import os
import time
from typing import List

from basketballers.models.basketball_player_model import BasketballPlayer  # Basketball player model import
from basketballers.utils.logger import configure_logger
from basketballers.utils.api_utils import get_random

# Temp
logger = logging.getLogger(__name__)
configure_logger(logger)


class GameModel:
    """A class to manage the basketball game between two teams of 2 players each."""

    def __init__(self):
        """Initializes the GameManager with two teams of 2 players each.

        Attributes:
            team_1 (List[int]): The list of ids of the players in team 1.
            team_2 (List[int]): The list of ids of the players in team 2.
            _player_cache (dict[int, BasketballPlayer]): A cache to store player objects for quick access.
            _ttl (dict[int, float]): A cache to store the time-to-live for each player.
            ttl_seconds (int): The time-to-live in seconds for the cached player objects.
        """
        self.team_1: List[int] = []  # List of player IDs for team 1
        self.team_2: List[int] = []  # List of player IDs for team 2
        self._player_cache: dict[int, BasketballPlayer] = {}  # Cache to store player objects
        self._ttl: dict[int, float] = {}  # Cache for TTL of player objects
        self.ttl_seconds: int = int(os.getenv("TTL_SECONDS", 60))  # TTL for player cache

    def play_game(self) -> str:
        """Simulates a basketball game between two teams of 2 players each.

        Calculates the total skill of each team and determines the winner based on a random factor.

        Returns:
            str: The name of the winning team.
        """
        if len(self.team_1) < 2 or len(self.team_2) < 2:
            logger.error("Each team must have 2 players to start a game.")
            raise ValueError("Each team must have 2 players to start a game.")

        team_1_skill = self.get_team_skill(self.team_1)
        team_2_skill = self.get_team_skill(self.team_2)

        logger.info(f"Game started between Team 1 and Team 2")
        logger.debug(f"Team 1 skill: {team_1_skill:.3f}, Team 2 skill: {team_2_skill:.3f}")

        # Normalize the skill difference and use a random factor to decide the winner
        delta = abs(team_1_skill - team_2_skill)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        logger.debug(f"Normalized skill delta: {normalized_delta:.3f}")

        random_number = get_random()

        logger.debug(f"Random number from random.org: {random_number:.3f}")

        if random_number < normalized_delta:
            winner = "Team 1"
        else:
            winner = "Team 2"

        logger.info(f"The winner is: {winner}")
        
        # Update stats for the winning and losing teams
        self.update_team_stats(winner)

        return winner

    def get_team_skill(self, team: List[int]) -> float:
        """Calculates the total skill for a team based on its players.

        Args:
            team (List[int]): A list of player IDs for a team.

        Returns:
            float: The total skill of the team.
        """
        total_skill = 0.0
        for player_id in team:
            player = self._get_player_by_id(player_id)
            total_skill += self.get_player_skill(player)
        return total_skill

    def get_player_skill(self, player: BasketballPlayer) -> float:
        """Calculates the skill for an individual player.

        Args:
            player (BasketballPlayer): The BasketballPlayer object for the player.

        Returns:
            float: The player's skill score.
        """
        logger.info(f"Calculating skill for {player.name}: weight={player.weight}, age={player.age}, reach={player.reach}")
        
        # Arbitrary skill calculation (you can modify this logic)
        skill = (player.weight * len(player.name)) + (player.reach / 10) - (player.age / 2)

        logger.debug(f"Calculated skill for {player.name}: {skill:.3f}")
        return skill

    def update_team_stats(self, winning_team: str):
        """Updates the stats for the winning and losing teams (optional)."""
        if winning_team == "Team 1":
            logger.info("Team 1 wins! Update stats accordingly.")
            # Implement stat updates for Team 1 and Team 2 (e.g., win/loss count)
        elif winning_team == "Team 2":
            logger.info("Team 2 wins! Update stats accordingly.")
            # Implement stat updates for Team 2 and Team 1 (e.g., win/loss count)
    
    def enter_game(self, player_id: int, team: int):
        """Adds a player to the specified team for the game.

        Args:
            player_id (int): The ID of the player.
            team (int): The team to add the player to (1 or 2).
        """
        if team == 1 and len(self.team_1) < 2:
            self.team_1.append(player_id)
        elif team == 2 and len(self.team_2) < 2:
            self.team_2.append(player_id)
        else:
            logger.error(f"Cannot add more players to team {team}. Each team can have only 2 players.")
            raise ValueError(f"Team {team} is already full.")

    def _get_player_by_id(self, player_id: int) -> BasketballPlayer:
        """Retrieve a player by their ID from the cache or database.

        Args:
            player_id (int): The ID of the player.

        Returns:
            BasketballPlayer: The player object.
        """
        player = self._player_cache.get(player_id)
        if not player:
            logger.info(f"Player {player_id} not found in cache. Refreshing from DB.")
            player = BasketballPlayer.get_player_by_id(player_id)
            self._player_cache[player_id] = player
        return player
