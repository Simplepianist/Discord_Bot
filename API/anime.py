"""
This module provides the Anime class to interact with the Waifu.it
and Jikan APIs to fetch anime quotes and character images.
"""
import logging
import os
import requests

def daily_anime_quote():
    """
    Fetches the daily anime quote from the Waifu.it API.

    Returns:
        dict: The JSON response from the API containing the anime quote.
    """
    url = "https://waifu.it/api/v4/quote"
    waifuitheader = {
        "Authorization": os.getenv("waifuit"),
    }
    response = requests.get(url, headers=waifuitheader, timeout=5)
    return response.json()

def get_anime_character_image(character):
    """
    Fetches the image URL of an anime character from the Jikan API.

    Args:
        character (str): The name of the anime character.

    Returns:
        str: The URL of the character's image if found, otherwise False.
    """
    try:
        # URL for the Waifu.pics API endpoint
        url = f'https://api.jikan.moe/v4/characters?q={character}&limit=1'

        # Sending a GET request to the API endpoint
        if url is None:
            return False
        response = requests.get(url, timeout=5)

        # Checking if the response status code is 200 (OK)
        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["images"]["jpg"]["image_url"]
        return False
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching image: %s", e)
        return False
