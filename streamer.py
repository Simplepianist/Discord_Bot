import os
import json
import logging
import discord
from discord import Streaming
from discord import Status
from discord.ext.commands import Bot
from Database.db_access import DbController
from cogs.CogSelector import CogSelector
from discord.app_commands import CommandInvokeError, CommandOnCooldown
from discord.ext.commands import Context, BadArgument, MissingRequiredArgument, \
    CheckFailure, NotOwner

# Configure logging ONCE at the top, before anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('bot.log')  # File output
    ],
    force=True
)

# Suppress specific loggers AFTER basic config
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
# More aggressive alembic logging suppression
logging.getLogger('alembic').setLevel(logging.WARNING)
logging.getLogger('alembic.runtime.migration').setLevel(logging.WARNING)
logging.getLogger('alembic.ddl.postgresql').setLevel(logging.WARNING)

# Keep our important loggers at INFO level
logging.getLogger('SimpleBot').setLevel(logging.INFO)
logging.getLogger('DbController').setLevel(logging.INFO)


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


class SimpleBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.owner: discord.User = self.get_user(self.owner_id)
        self.shutdown_initiated = False
        self.logging = logging.getLogger('SimpleBot')
        self.db = DbController()
        self.config = load_config()

    async def on_ready(self):
        """
        Diese Funktion wird aufgerufen, wenn der Bot bereit ist.
        Sie initialisiert die Datenbankverbindung, konfiguriert das Logging,
        synchronisiert die Befehle und setzt den Status des Bots.

        Aktionen:
        - Führt Datenbank-Migrationen aus.
        - Initialisiert den Datenbank-Pool.
        - Konfiguriert das Logging mit einem bestimmten Format und speichert die Logs in einer Datei.
        - Synchronisiert die Befehle des Bots.
        - Setzt den Besitzer des Bots.
        - Ändert die Präsenz des Bots zu einem Streaming-Status mit einem bestimmten Namen und URL.
        """
        # Test logger immediately
        self.logging.info("on_ready() method started")

        await self.add_cog(CogSelector(self))
        self.logging.info("CogSelector added successfully")

        await self.change_presence(status=Status.offline, activity=discord.Game(name="Starte..."))

        # Run migrations and initialize database
        await self.db.run_migrations()
        await self.db.init_pool()

        await self.change_presence(activity=Streaming(name=".help", url=self.config["streamURL"]))

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
            raise error


intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
simpleBot = SimpleBot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True)

try:
    simpleBot.run(os.environ["token"])
finally:
    logging.shutdown()