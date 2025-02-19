"""
Dieses Modul enthält verschiedene Variablen und Konfigurationsfunktionen für den Discord-Bot.
"""

import json
import logging
import discord
from simplebot import Simplebot


def load_config(name):
    """
    Lädt die Konfiguration aus der Datei `jsons/config.json`
    und gibt den Wert für den angegebenen Namen zurück.

    Args:
        name (str): Der Name des Konfigurationswerts, der zurückgegeben werden soll.

    Returns:
        dict: Der Konfigurationswert für den angegebenen Namen.
    """
    with open("jsons/config.json") as f:
        json_file = json.load(f)
    try:
        json_file["embed"]["embeds_footerpic"] = OWNER.avatar
    except:
        pass
    return json_file[name]

intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
currentlyGaming = []
SHUTDOWN_INITIATED = False
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
bot = Simplebot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True)
OWNER = discord.Member
botRole = load_config("botrole")
streamURL = load_config("streamURL")
inviteLink = load_config("inviteLink")
