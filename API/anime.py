"""
This module provides the Anime class to interact with the Waifu.it
and Jikan APIs to fetch anime quotes and character images.
"""
import logging
import os
import requests

class Anime:
    """
    A class to interact with the Waifu.it and Jikan APIs to fetch anime quotes and character images.
    """

    def __init__(self):
        """
        Initializes the Anime class with the base URL and headers for the Waifu.it API.
        """
        self.waifuit = "https://waifu.it/api/v4/"
        self.waifuitheader = {
            "Authorization": os.environ["waifuit"],
        }

    def daily_anime_quote(self):
        """
        Fetches the daily anime quote from the Waifu.it API.

        Returns:
            dict: The JSON response from the API containing the anime quote.
        """
        url = self.waifuit + "quote"
        response = requests.get(url, headers=self.waifuitheader, timeout=5)
        return response.json()

    def get_anime_character_image(self, character):
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
