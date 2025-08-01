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
        self.currentlyGaming = []
        self.shutdown_initiated = False
        self.logging = logging.getLogger('SimpleBot')
        self.db = DbController()
        self.config = load_config()

    async def notify_owner(self, message: str):
        """
        Sendet dem Bot-Owner eine DM mit einer Nachricht und versucht zusätzlich eine ntfy-Benachrichtigung zu senden.
        """
        # Discord DM
        owner = await self.fetch_user(self.owner_id)
        try:
            if not owner.dm_channel:
                await owner.create_dm()
            await owner.send(message)
        except Exception as e:
            await self.send_ntfy(f"Konnte Owner nicht per DM benachrichtigen: {e}")
            self.logging.warning(f"Konnte Owner nicht per DM benachrichtigen: {e}")

        await self.send_ntfy(message)

    async def send_ntfy(self, message: str):
        """
        Sendet eine Nachricht an den ntfy-Dienst, wenn die URL in den Umgebungsvariablen gesetzt ist.
        """
        import aiohttp
        ntfy_url = os.getenv("NTFY_URL")
        if ntfy_url:
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post(ntfy_url, data=message.encode("utf-8"))
                except Exception as e:
                    self.logging.warning(f"Konnte ntfy nicht benachrichtigen: {e}")

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

        await self.change_presence(status=Status.offline, activity=discord.Game(name="Starte..."))

        # Run migrations and initialize database
        try:
            await self.db.run_migrations()
            await self.db.init_pool()
        except Exception as e:
            await self.notify_owner(f"❗️ DB-Fehler beim Start: {e}")
            raise

        cogselector = CogSelector(self)
        await self.add_cog(cogselector)
        await cogselector.initialize_cogs_from_db()
        self.logging.info("CogSelector added successfully")

        await self.sync_commmands()
        self.logging.info("Sync gestartet (1h)")

        await self.change_presence(activity=Streaming(name=".help", url=self.config["streamURL"]))


    async def sync_commmands(self):
        """
        Synchronisiert die Befehle des Bots mit Discord.
        Diese Funktion wird aufgerufen, um sicherzustellen, dass alle Befehle
        korrekt registriert sind und verfügbar sind.
        """
        for guild in self.guilds:
            self.logging.info(f"Synchronisiere Befehle für Guild: {guild.name} (ID: {guild.id})")
            await self.tree.sync(guild=guild)
        self.logging.info("Befehle erfolgreich synchronisiert.")

    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, BadArgument):
            await ctx.send("Du hast ein ungültiges Argument eingegeben. Bitte überprüfe deine Eingabe und versuche es erneut.", delete_after=8)
        elif isinstance(error, MissingRequiredArgument):
            missing = getattr(error, 'param', None)
            if missing:
                await ctx.send(f"Es fehlt ein benötigtes Argument. Bitte gib alle erforderlichen Argumente an.", delete_after=8)
            else:
                await ctx.send("Es fehlen erforderliche Argumente. Bitte überprüfe die Befehlsbeschreibung.", delete_after=8)
        elif isinstance(error, (CheckFailure, NotOwner)):
            await ctx.send("Du hast nicht die Berechtigung, diesen Befehl auszuführen.", delete_after=5)
        elif isinstance(error, CommandInvokeError):
            await ctx.send("Bei der Ausführung des Befehls ist ein unerwarteter Fehler aufgetreten. Bitte versuche es erneut oder kontaktiere einen Admin.", delete_after=10)
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(f"Dieser Befehl ist auf Abklingzeit. Versuche es in {error.retry_after:.2f} Sekunden erneut.", delete_after=5)
        else:
            self.logging.error("Error: %s (caused by %s)", error, ctx.author.global_name)
            await self.notify_owner(f"Error: {error} (caused by {ctx.author.global_name})")

intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
simpleBot = SimpleBot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True, owner_id=int(os.getenv("OWNER_ID", "325779745436467201")))

try:
    simpleBot.run(os.environ["token"])
finally:
    logging.shutdown()