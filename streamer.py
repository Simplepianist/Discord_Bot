"""
This module contains the main functionality for the Discord bot, including event handlers,
command error handling, and cog loading.

Modules:
- os: Provides a way of using operating system dependent functionality.
- asyncio: Provides support for asynchronous programming.
- logging: Provides a way to configure and use logging.
- threading: Provides support for creating and managing threads.
- discord: Provides the Discord API.
- Util.variables: Contains utility functions and variables for the bot.
"""

import os
import asyncio
import logging
import threading

from discord import Streaming
from discord.app_commands import CommandOnCooldown, CommandNotFound, MissingPermissions
from discord.ext.commands import BadArgument, MissingRequiredArgument, CheckFailure, NotOwner
from Util import variables
from Util.variables import bot

@bot.event
async def on_ready():
    """
    This function is called when the bot is ready.
    It initializes the database connection, configures logging,
    synchronizes commands, and sets the bot's status.

    Actions:
    - Initializes the database pool.
    - Configures logging with a specific format and saves logs to a file.
    - Synchronizes the bot's commands.
    - Sets the bot's owner.
    - Changes the bot's presence to a streaming status with a specific name and URL.
    """
    await bot.db.init_pool()
    fastapi_thread = threading.Thread(target=lambda: asyncio.run(bot.run_fastapi(bot)))
    fastapi_thread.start()
    try:
        amount = await bot.tree.sync()
        logging.info("Sync gestartet (%d Commands) (Kann bis zu 1h dauern)" % len(amount))
    except Exception as e:
        logging.error(e)
        logging.error("Fehler beim Syncen der Commands (probably duplicates)")

    variables.owner = await bot.fetch_user(325779745436467201)
    await bot.change_presence(activity=Streaming(name=".help", url=variables.streamURL))

@bot.event
async def on_command_error(ctx, error):
    """
    This function handles errors that occur when a command is invoked.

    Parameters:
    - ctx: The context in which the command was invoked.
    - error: The error that was raised.

    Handles specific errors and sends appropriate messages to the user.
    Logs the error if it is not specifically handled.
    """
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
    """
    This function loads the bot's cogs (extensions).

    Cogs:
    - admin_cog
    - game_cog
    - social_cog
    - utility_cog
    """
    await bot.load_extension("cogs.admin_cog")
    await bot.load_extension("cogs.game_cog")
    await bot.load_extension("cogs.social_cog")
    await bot.load_extension("cogs.utility_cog")

async def main():
    """
    The main entry point for the bot.

    Loads the cogs and starts the bot using the token from the environment variables.
    Ensures the bot is properly closed if an error occurs.
    """
    await load_cogs()
    try:
        await bot.start(os.environ["token"])
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
