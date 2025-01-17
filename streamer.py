import os
import asyncio
import logging
import threading

from discord import Streaming
from discord.app_commands import CommandOnCooldown, CommandNotFound, \
    MissingPermissions
from discord.ext.commands import BadArgument, MissingRequiredArgument, \
    CheckFailure, NotOwner
from Util import variables
from Util.variables import bot

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
    await bot.db.init_pool()
    fastapi_thread = threading.Thread(target=lambda: asyncio.run(bot.run_fastapi(bot)))
    fastapi_thread.start()
    try:
        amount = await bot.tree.sync()
        logging.info(f"Sync gestartet ({len(amount)} Commands) (Kann bis zu 1h dauern)")
    except Exception as e:
        logging.error(e)
        logging.error("Fehler beim Syncen der Commands (probably duplicates)")

    variables.owner = await bot.fetch_user(325779745436467201)
    await bot.change_presence(activity=Streaming(name=".help", url=variables.streamURL))

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


async def load_cogs():
    await bot.load_extension("cogs.admin_cog")
    await bot.load_extension("cogs.game_cog")
    await bot.load_extension("cogs.social_cog")
    await bot.load_extension("cogs.utility_cog")


async def main():
    await load_cogs()
    try:
        await bot.start(os.environ["token"])
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())

