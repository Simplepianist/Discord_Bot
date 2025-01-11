"""
Dieses Modul enthält die Klasse `Quote`,
die Zitate von einer Anime-API und der ZenQuotes-API abruft.
"""
import logging
from typing import Any

import requests
from API.anime import daily_anime_quote

def animequote():
    """
    Ruft das tägliche Anime-Zitat ab.

    Returns:
        str: Das tägliche Anime-Zitat.
    """
    return daily_anime_quote()

def qotd() -> Any | None:
    """
    Ruft das Zitat des Tages von der ZenQuotes-API ab.

    Returns:
        dict: Das Zitat des Tages, wenn die Anfrage erfolgreich ist.
        bool: False, wenn die Anfrage fehlschlägt.
    """
    try:
        response = requests.get("https://zenquotes.io/api/today", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data[0]
        return None
    except requests.exceptions.RequestException as e:
        logging.error("Fehler beim Abrufen des Zitats: %s", e)
        return None
