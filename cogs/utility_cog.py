import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.context import Context

from Commands.main_commands import (help_command, alias_command, ping_command,
                                    invite_command, stream_command)

class UtilityCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", description="Hilfe für alle Befehle")
    async def _help(self, ctx: Context | discord.Interaction):
        await help_command(ctx)

    @commands.command(name="alias", aliases=["a"], description="Aliasliste der Befehle")
    async def _aliases(self, ctx: Context | discord.Interaction):
        await alias_command(ctx)

    @commands.command(name="ping", description="Ping des Bots/Pong")
    async def _ping(self, ctx: Context | discord.Interaction):
        await ping_command(ctx)

    @commands.command(name="invite", description="Invite-link für diesen Server")
    async def _invite(self, ctx: Context | discord.Interaction):
        await invite_command(ctx)

    # Slash commands
    @app_commands.command(name="stream", description="Streamlink von Simplebox")
    async def stream(self, ctx: Context | discord.Interaction):
        await stream_command(ctx)

    @app_commands.command(name="help", description="Hilfe für alle Befehle")
    async def help(self, ctx: Context | discord.Interaction):
        await help_command(ctx)

    @app_commands.command(name="alias", description="Aliasliste der Befehle")
    async def aliases(self, ctx: Context | discord.Interaction):
        await alias_command(ctx)

    @app_commands.command(name="ping", description="Ping des Bots/Pong")
    async def ping(self, ctx: Context | discord.Interaction):
        await ping_command(ctx)

    @app_commands.command(name="invite", description="Invite-link für diesen Server")
    async def invite(self, ctx: Context | discord.Interaction):
        await invite_command(ctx)

    @app_commands.command(name="stream", description="Streamlink von Simplebox")
    async def stream(self, ctx: Context | discord.Interaction):
        await stream_command(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
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
    await bot.add_cog(UtilityCog(bot))