"""
Dieses Modul enthält die Implementierung eines Discord-Bots
mit verschiedenen Befehlen und Ereignishandlern.
Der Bot verwendet die discord.py-Bibliothek und bietet Funktionen
wie das Synchronisieren von Befehlen,
das Verwalten von Benutzerkonten und das Spielen von Minispielen.

Importierte Module:
- os: Zum Zugriff auf Umgebungsvariablen.
- logging: Zum Protokollieren von Ereignissen und Fehlern.
- discord: Zum Interagieren mit der Discord-API.
- app_commands: Zum Erstellen von Anwendungsbefehlen.
- discord.ext.commands: Zum Erstellen von Befehlen und Ereignishandlern.
- Commands: Enthält verschiedene Befehlsimplementierungen.
- Util: Enthält Hilfsfunktionen und Variablen.

Konstanten:
- SHUTDOWN_INITIATED: Ein boolescher Wert, der anzeigt, ob der Shutdown-Prozess initiiert wurde.

Funktionen:
- on_ready: Wird aufgerufen, wenn der Bot bereit ist.
- on_command_error: Wird aufgerufen, wenn ein Fehler bei der Befehlsausführung auftritt.
- clear_commands: Löscht alle Befehle aus dem Befehlsbaum.
- load_commands: Synchronisiert die Befehle mit dem Befehlsbaum.
- _setMoney: Setzt das Geld eines Benutzers.
- _shutdown: Fährt den Bot herunter.
- _reset: Setzt den Status des Bots zurück.
- _setStatus: Setzt den Status des Bots.
- _help: Zeigt das Hilfemenü an.
- _rules: Zeigt die Regeln an.
- _aliases: Zeigt die Aliasliste der Befehle an.
- _ping: Antwortet mit "Pong".
- _invite: Gibt den Einladungslink für den Server aus.
- _stream: Gibt den Streamlink von Simplebox aus.
- _scoreboard: Zeigt das Scoreboard für die meisten Coins an.
- _daily: Führt den täglichen Befehl aus.
- _send: Sendet Geld an einen anderen Benutzer.
- _money: Zeigt das Geld eines Benutzers an.
- _robbing: Führt den Raubbefehl aus.
- _blackjack: Spielt eine Runde Blackjack.
- _roulette: Spielt eine Runde Roulette.
- _higherLower: Spielt eine Runde Higher/Lower.
- _quote: Gibt ein zufälliges Anime-Zitat aus.
- _qotd: Gibt das Zitat des Tages aus.
- rules: Zeigt die Regeln der Spiele an.
- aliases: Zeigt die Aliasliste aller Befehle an.
- ping: Antwortet mit "Pong".
- invite: Gibt den Einladungslink für den Server aus.
- stream: Gibt den Streamlink von Simplebox aus.
- scoreboard: Zeigt das Scoreboard für die Games an.
- daily: Führt den täglichen Befehl aus.
- send: Sendet Geld an einen anderen Benutzer.
- money: Zeigt das Geld eines Benutzers an.
- blackjack: Spielt eine Runde Blackjack.
- roulette: Spielt eine Runde Roulette.
- higher_lower: Spielt eine Runde Higher/Lower.
- robbing: Führt den Raubbefehl aus.
- quote: Gibt ein zufälliges Anime-Zitat aus.
- qotd: Gibt das Zitat des Tages aus.
"""
import os
import json
import logging
import discord
from alembic.config import Config
from alembic import command
from discord import Streaming
from discord.ext.commands import Bot
from Database.db_access import DbController
from cogs.CogSelector import CogSelector
from discord.app_commands import CommandInvokeError, CommandOnCooldown
from discord.ext.commands import Context, BadArgument, MissingRequiredArgument, \
    CheckFailure, NotOwner

def load_config():
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
        json_file["embed"]["embeds_footerpic"] = discord.Member
    except:
        pass
    return json_file

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

class SimpleBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.owner: discord.User = self.get_user(self.owner_id)
        self.shutdown_initiated = False
        self.logging = logging
        self.db = DbController()
        self.config = load_config()

    async def on_ready(self):
        """
        Diese Funktion wird aufgerufen, wenn der Bot bereit ist.
        Sie initialisiert die Datenbankverbindung, konfiguriert das Logging,
        synchronisiert die Befehle und setzt den Status des Bots.

        Aktionen:
        - Initialisiert den Datenbank-Pool.
        - Konfiguriert das Logging mit einem bestimmten Format und speichert die Logs in einer Datei.
        - Synchronisiert die Befehle des Bots.
        - Setzt den Besitzer des Bots.
        - Ändert die Präsenz des Bots zu einem Streaming-Status mit einem bestimmten Namen und URL.
        """
        self.logging.basicConfig(level=logging.INFO,
                                 format='%(asctime)s:%(levelname)s:%(message)s')
        await self.add_cog(CogSelector(self))
        await self.change_presence(activity=Streaming(name=".help", url=self.config["streamURL"]))
        await self.db.init_pool()
        await self.tree.sync()
        self.logging.info("Sync gestartet (1h)")


    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, BadArgument):
            await ctx.send("Falsche Angabe von Argumenten", delete_after=5)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send("Fehlende Argumente", delete_after=5)
        elif isinstance(error, (CheckFailure, NotOwner)):
            await ctx.send("Du hast nicht die Berechtigung, diesen Befehl auszuführen",
                           delete_after=5)
        elif isinstance(error, CommandInvokeError):
            await ctx.send("Ein Fehler ist bei der Ausführung des Befehls aufgetreten",
                           delete_after=5)
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(f"Dieser Befehl ist auf Abklingzeit. "
                           f"Versuche es in {error.retry_after:.2f} Sekunden erneut.",
                           delete_after=5)
        else:
            self.logging.error("Error: %s (caused by %s)", error, ctx.author.global_name)

intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
simpleBot = SimpleBot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True)

try:
    run_migrations()
    simpleBot.run(os.environ["token"])
finally:
    logging.shutdown()