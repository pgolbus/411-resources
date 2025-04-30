# utils/api_interaction.py

import requests
from basketball.models.basketball_player_model import BasketballPlayer

def fetch_and_store_players():
    """
    Fetches player data from the BallDontLie API (default: 30 players on page 1)
    and stores valid players in the database.
    """
    url = "https://www.balldontlie.io/api/v1/players"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from BallDontLie API")

    players_data = response.json().get("data", [])

    for player in players_data:
        try:
            # Handle missing/null values gracefully
            if not all([
                player["first_name"], player["last_name"], player["team"], player["position"]
            ]):
                continue

            full_name = f"{player['first_name']} {player['last_name']}"
            position = player["position"]
            team = player["team"]["full_name"]
            height_feet = player.get("height_feet")
            height_inches = player.get("height_inches")
            weight_pounds = player.get("weight_pounds")

            # Only insert if all essential stats exist
            if None in (height_feet, height_inches, weight_pounds):
                continue

            BasketballPlayer.create_player(
                full_name=full_name,
                position=position,
                team=team,
                height_feet=height_feet,
                height_inches=height_inches,
                weight_pounds=weight_pounds
            )
        except ValueError as ve:
            print(f"Skipping player due to validation error: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")