"""
Dieses Modul enthält die Klasse `Quote`,
die Zitate von einer Anime-API und der ZenQuotes-API abruft.
"""
import logging
from typing import Any

import requests
from API.anime import Anime


class Quote:
    """
    Eine Klasse, die Zitate von einer Anime-API und der ZenQuotes-API abruft.
    """
    def __init__(self):
        """
        Initialisiert die Klasse `Quote`.
        Erstellt eine Instanz der `Anime`-Klasse und setzt die URL für das Zitat des Tages.
        """
        self.anime = Anime()
        self.qotd_url = "https://zenquotes.io/api/today"

    def animequote(self):
        """
        Ruft das tägliche Anime-Zitat ab.

        Returns:
            str: Das tägliche Anime-Zitat.
        """
        return self.anime.daily_anime_quote()

    def qotd(self) -> Any | None:
        """
        Ruft das Zitat des Tages von der ZenQuotes-API ab.

        Returns:
            dict: Das Zitat des Tages, wenn die Anfrage erfolgreich ist.
            bool: False, wenn die Anfrage fehlschlägt.
        """
        try:
            response = requests.get(self.qotd_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data[0]
            return None
        except requests.exceptions.RequestException as e:
            logging.error("Fehler beim Abrufen des Zitats: %s", e)
            return None
