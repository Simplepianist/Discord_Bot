"""
This module defines the API class for handling API routes related to the bot and database.

Classes:
    API: A class to handle API routes for scoreboard and command list.

Methods:
    __init__(self, bot, db): Initializes the API class with bot and database instances.
    scoreboard(self): Asynchronously retrieves and returns the scoreboard data.
    command_list(self): Asynchronously retrieves and returns the list of commands.
"""

from discord.ext.commands import Command
from fastapi import APIRouter, Request

class API:
    """
    A class to handle API routes for scoreboard and command list.

    Attributes:
        bot: The bot instance.
        db: The database instance.
        router: The FastAPI router instance.
    """

    def __init__(self):
        """
        Initializes the API class with bot and database instances.
        """
        self.router = APIRouter()
        self.router.add_api_route("/scoreboard", scoreboard, methods=["GET"])
        self.router.add_api_route("/commands", command_list, methods=["GET"])

async def scoreboard(request: Request):
    """
    Asynchronously retrieves and returns the scoreboard data.

    Returns:
        A list of dictionaries containing usernames and their corresponding money.
    """
    db = request.app.state.db
    bot = request.app.state.bot
    scorelist = sorted(await db.get_users_with_money(), key=lambda x: x[1], reverse=True)
    result = []
    for score in scorelist:
        user = bot.get_user(int(score[0])) or await bot.fetch_user(int(score[0]))
        result.append({"username": user.name, "money": score[1]})
    return result

async def command_list(request: Request):
    """
    Asynchronously retrieves and returns the list of commands.

    Returns:
        A list of dictionaries containing cog names and their corresponding commands.
    """
    bot = request.app.state.bot
    result = []
    for cog_name, cog in bot.cogs.items():
        commands = []
        for command in cog.get_commands():
            if isinstance(command, Command):
                checks = [check.__qualname__.split(".")[0] for check in command.checks]
                aliases = []
                for alias in command.aliases:
                    aliases.append("." + alias)
                commands.append([command.name, aliases, command.description, checks])
        result.append({cog_name: commands})
    return result
