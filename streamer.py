import os
import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from discord import Streaming
from discord.app_commands import CommandOnCooldown, CommandNotFound, \
    MissingPermissions
from discord.ext.commands import BadArgument, MissingRequiredArgument, \
    CheckFailure, NotOwner
from API.content_api import API
from Util import variables
from Util.variables import streamURL
from Util.util_commands import db
from Util.variables import bot

app = FastAPI()

@bot.event
async def on_ready():
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
    await db.init_pool()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    register_endpoints()
    try:
        amount = await bot.tree.sync()
        logging.info("Sync gestartet (%s Commands) (Kann bis zu 1h dauern)", {len(amount)})
    except Exception as e:
        logging.error(e)
        logging.error("Fehler beim Syncen der Commands (probably duplicates)")
    await bot.change_presence(activity=Streaming(name=".help", url=streamURL))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Dieser Befehl existiert nicht")
    elif isinstance(error, CheckFailure):
        await ctx.send("Du hast nicht die nötigen Rechte")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send("Fehlendes Argumente angegeben (siehe .help)")
    elif isinstance(error, BadArgument):
        await ctx.send("Falsches Argument angegeben (siehe .help)")
    elif isinstance(error, CommandOnCooldown):
        await ctx.send(f"Dieser Befehl ist noch auf Cooldown ({error.retry_after:.2f}s)")
    elif isinstance(error, MissingPermissions):
        await ctx.send("Du hast nicht die nötigen Rechte")
    elif isinstance(error, NotOwner):
        await ctx.send("Du bist nicht der Owner")
    else:
        logging.error(error)

def register_endpoints():
    api = API(bot)
    app.include_router(api.router)

async def load_cogs():
    await bot.load_extension("cogs.admin_cog")
    await bot.load_extension("cogs.game_cog")
    await bot.load_extension("cogs.social_cog")
    await bot.load_extension("cogs.utility_cog")

async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await load_cogs()
    await asyncio.gather(bot.start(os.environ["token"]), run_fastapi())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if not variables.SHUTDOWN_INITIATED:
            # Protokolliert, dass der Shutdown-Prozess gestartet wird
            logging.info("Shutting down")
            # Schließt den Datenbank-Pool
            db.close_pool()
            # Schließt den Bot
            bot.close()
            # Protokolliert, dass der Shutdown-Prozess abgeschlossen ist
            logging.info("Shutdown complete")
        # Beendet das Logging
        logging.shutdown()
