# utils/api_interaction.py
import requests

API_URL = "https://www.balldontlie.io/api/v1/players"

def get_players_from_api():
    """Fetch player data from the BallDontLie API."""
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()  # Return the API response as a JSON object
    else:
        return None  # Return None if the API request fails
