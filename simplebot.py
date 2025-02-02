"""
SimpleBot module

This module defines the SimpleBot class, which extends the discord.ext.commands.Bot class.
It includes methods to run a FastAPI server and to close the bot and its resources.
"""

import logging
from discord.ext import commands
from fastapi import FastAPI
from uvicorn import Config, Server
from API.content_api import API
from Database.db_access import DbController


class Simplebot(commands.Bot):
    """
    A simple bot class that extends the discord.ext.commands.Bot class.

    Attributes:
        api_server (Server): The FastAPI server instance.
        db (DbController): The database controller instance.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the SimpleBot instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.api_server = None
        self.db = DbController()

    async def run_fastapi(self, bot):
        """
        Starts the FastAPI server.

        Args:
            bot (commands.Bot): The bot instance to pass to the API.
        """
        logging.info("Starting FastAPI server")
        app = FastAPI()
        app.include_router(API(bot, self.db).router)
        config = Config(app, host="0.0.0.0", port=8000)
        self.api_server = Server(config)
        await self.api_server.serve()

    async def close(self) -> None:
        """
        Closes the bot and its resources.
        """
        await super().close()
        await self.db.close_pool()
        await self.api_server.shutdown()
