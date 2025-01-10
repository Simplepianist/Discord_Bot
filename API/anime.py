import os

import requests
from Util.util_commands import load_config

class Anime:
    def __init__(self):
        self.waifuit = "https://waifu.it/api/v4/"
        self.waifuitheader = {
            "Authorization": os.environ["waifuit"],
        }

    def daily_anime_quote(self):
        url = self.waifuit + "quote"
        response = requests.get(url, headers=self.waifuitheader)
        return response.json()

    def get_anime_character_image(self, character):
        try:
            # URL for the Waifu.pics API endpoint
            url = f'https://api.jikan.moe/v4/characters?q={character}&limit=1'

            # Sending a GET request to the API endpoint
            response = requests.get(url)

            # Checking if the response status code is 200 (OK)
            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["images"]["jpg"]["image_url"]
            else:
                return False
        except Exception as e:
            return str(e)
