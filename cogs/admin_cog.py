"""
AdminCog module for managing administrative commands in a Discord bot.

This module contains commands for syncing, clearing, and managing bot commands,
as well as setting user money and bot status.

Classes:
    AdminCog: A class that defines administrative commands for the bot.

Functions:
    setup: Adds the AdminCog to the bot.
"""

import logging
import discord
from discord.ext import commands
from discord import Interaction
from discord.ext.commands.context import Context
from Util.util_commands import has_role

from Commands.admin_commands import set_money_command, shutdown_command, \
    reset_status_command, set_status_command

class AdminCog(commands.Cog, name="Admin"):
    """
    A class that defines administrative commands for the bot.

    Methods:
        __init__(bot): Initializes the AdminCog with the bot instance.
        load_commands(ctx): Syncs the commands with the Discord API.
        clear_commands(ctx): Clears all commands from the Discord API.
        _set_money(ctx, member, user_money): Sets the money of a user.
        _shutdown(ctx): Shuts down the bot.
        _reset(ctx): Resets the status of the bot.
        _set_status(ctx): Sets the status of the bot.
    """
    def __init__(self, bot):
        """
        Initializes the AdminCog with the bot instance.

        Parameters:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot

    @commands.command(name="load", aliases=['sync'],
                      description="Syncs the commands with the discord API")
    @has_role()
    async def load_commands(self, ctx: Context | Interaction):
        """
        Syncs the commands with the Discord API.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        logging.info("Sync triggered by %s", ctx.author.global_name)
        if self.bot.tree:
            amount = await self.bot.tree.sync()
            await ctx.channel.send(f"Loaded {len(amount)} Commands (May be seen in 1h)")
        else:
            await ctx.channel.send("Command tree is not initialized.")

    @commands.command(name="clear", description="Clears all commands from the discord API")
    @has_role()
    async def clear_commands(self, ctx: Context | Interaction):
        """
        Clears all commands from the Discord API.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        logging.info("Clear triggered by %s", ctx.author.global_name)
        if self.bot.tree:
            await self.bot.tree.clear_commands(guild=None)
            await ctx.channel.send("Cleared all commands")
        else:
            await ctx.channel.send("Command tree is not initialized.")

    @commands.command(name="set", description="Setze das Geld eines Users")
    @has_role()
    async def _set_money(self, ctx: Context | Interaction, member: discord.Member, user_money=None):
        """
        Sets the money of a user.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
            member (discord.Member): The member whose money is to be set.
            user_money (optional): The amount of money to set for the user.
        """
        await set_money_command(ctx, member, user_money)

    @commands.command(name="shutdown", aliases=["quit", "close", "stop"],
                      description="Fahre den Bot herunter")
    @has_role()
    async def _shutdown(self, ctx: Context | Interaction):
        """
        Shuts down the bot.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await shutdown_command()

    @commands.command(name="reset", description="Setze den Status des Bots zurück")
    @has_role()
    async def _reset(self, ctx: Context | Interaction):
        """
        Resets the status of the bot.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await reset_status_command(ctx)

    @commands.command(name="setStatus", description="Setze den Status des Bots")
    @has_role()
    async def _set_status(self, ctx: Context | Interaction):
        """
        Sets the status of the bot.

        Parameters:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await set_status_command(ctx)

async def setup(bot):
    """
    Adds the AdminCog to the bot.

    Parameters:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(AdminCog(bot))
