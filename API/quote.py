import requests
from Util.util_commands import load_config
from API.anime import Anime


class Quote():
    def __init__(self):
        self.anime = Anime()
        self.qotd_Url = "https://zenquotes.io/api/today"
    def anime_Quote(self):
        return self.anime.daily_anime_quote()

    def qotd(self):
        try:
            response = requests.get(self.qotd_Url)
            if response.status_code == 200:
                data = response.json()
                return data[0]
            else:
                return False
        except Exception as e:
            return str(e)