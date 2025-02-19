"""
UtilityCog module for Discord bot commands.

This module defines a cog for a Discord bot that includes various utility commands.
"""

from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands.context import Context

from Commands.main_commands import help_command, alias_command, \
    ping_command, invite_command, stream_command


class UtilityCog(commands.Cog, name="Utility"):
    """
    A cog that contains utility commands for the Discord bot.
    """

    def __init__(self, bot):
        """
        Initializes the UtilityCog.

        Parameters:
        bot (commands.Bot): The bot instance.
        """
        self.bot = bot

    @commands.command(name="help", description="Hilfe für alle Befehle")
    async def _help(self, ctx: Context | Interaction):
        """
        Command to display help information for all commands.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await help_command(ctx)

    @commands.command(name="alias", aliases=["a"], description="Aliasliste der Befehle")
    async def _aliases(self, ctx: Context | Interaction):
        """
        Command to display a list of command aliases.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await alias_command(ctx)

    @commands.command(name="ping", description="Ping des Bots/Pong")
    async def _ping(self, ctx: Context | Interaction):
        """
        Command to display the bot's ping.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await ping_command(ctx)

    @commands.command(name="invite", description="Invite-link für diesen Server")
    async def _invite(self, ctx: Context | Interaction):
        """
        Command to display the invite link for the server.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await invite_command(ctx)

    @commands.command(name="stream", description="Streamlink von Simplebox")
    async def _stream(self, ctx: Context | Interaction):
        """
        Command to display the stream link from Simplebox.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await stream_command(ctx)

    # Slash commands

    @app_commands.command(name="help", description="Hilfe für alle Befehle")
    async def help(self, ctx: Context | Interaction):
        """
        Slash command to display help information for all commands.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await help_command(ctx)

    @app_commands.command(name="alias", description="Aliasliste der Befehle")
    async def aliases(self, ctx: Context | Interaction):
        """
        Slash command to display a list of command aliases.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await alias_command(ctx)

    @app_commands.command(name="ping", description="Ping des Bots/Pong")
    async def ping(self, ctx: Context | Interaction):
        """
        Slash command to display the bot's ping.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await ping_command(ctx)

    @app_commands.command(name="invite", description="Invite-link für diesen Server")
    async def invite(self, ctx: Context | Interaction):
        """
        Slash command to display the invite link for the server.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await invite_command(ctx)

    @app_commands.command(name="stream", description="Streamlink von Simplebox")
    async def stream(self, ctx: Context | Interaction):
        """
        Slash command to display the stream link from Simplebox.

        Parameters:
        ctx (Context | Interaction): The context of the command.
        """
        await stream_command(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener that is called when the bot is ready.
        Adds the slash commands to the bot's command tree if they are not already present.
        """
        if not self.bot.tree.get_command("stream"):
            self.bot.tree.add_command(self.stream)
        if not self.bot.tree.get_command("help"):
            self.bot.tree.add_command(self.help)
        if not self.bot.tree.get_command("alias"):
            self.bot.tree.add_command(self.aliases)
        if not self.bot.tree.get_command("ping"):
            self.bot.tree.add_command(self.ping)
        if not self.bot.tree.get_command("invite"):
            self.bot.tree.add_command(self.invite)


async def setup(bot):
    """
    Sets up the UtilityCog.

    Parameters:
    bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(UtilityCog(bot))
