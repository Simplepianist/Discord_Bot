"""
SimpleBot module

This module defines the SimpleBot class, which extends the discord.ext.commands.Bot class.
It includes methods to run a FastAPI server and to close the bot and its resources.
"""

from discord.ext import commands
from Database.db_access import DbController


class Simplebot(commands.Bot):
    """
    A simple bot class that extends the discord.ext.commands.Bot class.

    Attributes:
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
        self.db = DbController()

    async def close(self) -> None:
        """
        Closes the bot and its resources.
        """
        await super().close()
        await self.db.close_pool()
