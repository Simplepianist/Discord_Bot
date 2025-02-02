"""
This module defines the SocialCog class, which provides commands
for fetching random anime quotes and the quote of the day (QOTD).
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.context import Context
from Commands.social_commands import anime_quote, qotd_command


class SocialCog(commands.Cog, name="Social"):
    """
    A Discord Cog that provides social commands
    such as fetching random anime quotes and the quote of the day.
    """

    def __init__(self, bot):
        """
        Initializes the SocialCog.

        Parameters:
        bot (commands.Bot): The bot instance.
        """
        self.bot = bot

    @commands.command(name="quote", description="Hol dir ein zufälliges Anime-Zitat")
    async def _quote(self, ctx: Context | discord.Interaction):
        """
        Command to fetch a random anime quote.

        Parameters:
        ctx (Context | discord.Interaction): The context of the command.
        """
        await anime_quote(ctx)

    @commands.command(name="qotd", description="Hol dir das Zitat des Tages")
    async def _qotd(self, ctx: Context | discord.Interaction):
        """
        Command to fetch the quote of the day.

        Parameters:
        ctx (Context | discord.Interaction): The context of the command.
        """
        await qotd_command(ctx)

    @app_commands.command(name="quote", description="Hol dir ein zufälliges Anime-Zitat")
    async def quote(self, ctx: Context | discord.Interaction):
        """
        Slash command to fetch a random anime quote.

        Parameters:
        ctx (Context | discord.Interaction): The context of the command.
        """
        await anime_quote(ctx)

    @app_commands.command(name="qotd", description="Hol dir das Zitat des Tages")
    async def qotd(self, ctx: Context | discord.Interaction):
        """
        Slash command to fetch the quote of the day.

        Parameters:
        ctx (Context | discord.Interaction): The context of the command.
        """
        await qotd_command(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener that is called when the bot is ready.
        Adds the slash commands to the bot's command tree if they are not already present.
        """
        if not self.bot.tree.get_command("quote"):
            self.bot.tree.add_command(self.quote)
        if not self.bot.tree.get_command("qotd"):
            self.bot.tree.add_command(self.qotd)


async def setup(bot):
    """
    Asynchronous setup function to add the SocialCog to the bot.

    Parameters:
    bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(SocialCog(bot))
