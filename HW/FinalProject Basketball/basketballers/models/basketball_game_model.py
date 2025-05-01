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
    
    def get_players(self) -> List[BasketballPlayer]:
        """Retrieves the current list of basketball players in both teams.

        Returns:
            List[BasketballPlayer]: A list of player objects representing the players in the game.
        """
        all_ids = self.team_1 + self.team_2
        if not all_ids:
            logger.warning("Retrieving players from an empty game.")
            return []
        else:
            logger.info(f"Retrieving {len(all_ids)} players from the game.")

        players = []
        for player_id in all_ids:
            ttl = self._ttl.get(player_id)
            if not ttl or time.time() > ttl:
                logger.info(f"TTL expired or missing for player {player_id}. Refreshing from DB.")
                player = BasketballPlayer.get_player_by_id(player_id)
                self._player_cache[player_id] = player
                self._ttl[player_id] = time.time() + self.ttl_seconds
            else:
                player = self._player_cache[player_id]
                logger.debug(f"Using cached player {player_id} (TTL valid).")

            players.append(player)

        logger.info(f"Retrieved {len(players)} players from the game.")
        return players

    def get_player_skill(self, player: BasketballPlayer) -> float:
        """Calculates the skill for an individual basketball player.
    
        Skill is calculated based on weight and height:
        - Skill = (weight in pounds) + (height in inches) + (position factor)
    
        Returns:
            float: The calculated skill value.
        """
        logger.info(f"Calculating skill for {player.full_name}: "
                    f"weight={player.weight_pounds}, "
                    f"height={player.height_feet}'{player.height_inches}\", "
                    f"position={player.position}")
        
        height_inches_total = player.height_feet * 12 + player.height_inches
        position_factor = {"G": 1.0, "F": 1.2, "C": 1.4}.get(player.position[:1].upper(), 1.0) 
    
        skill = player.weight_pounds + height_inches_total * position_factor
    
        logger.info(f"Calculated skill for {player.full_name}: {skill:.2f}")
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
            
    def clear_game(self):
        """
        Clears both teams from the game.
    
        Empties the player lists for Team 1 and Team 2 and logs the action.
        If both teams are already empty, logs a warning.
        """
        if not self.team_1 and not self.team_2:
            logger.warning("Attempted to clear an empty game (both teams are already empty).")
            return
        logger.info("Clearing all players from both teams.")
        self.team_1.clear()
        self.team_2.clear()
        
    def clear_cache(self):
        """Clears the local TTL cache of basketball players."""
        logger.info("Clearing local player cache in GameModel.")
        self._player_cache.clear()
        self._ttl.clear()