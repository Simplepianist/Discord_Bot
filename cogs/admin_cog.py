import logging
import discord
from discord.ext import commands
from discord import Interaction
from discord.ext.commands.context import Context
from Util.util_commands import has_role

from Commands.admin_commands import set_money_command, shutdown_command, reset_status_command, set_status_command

class AdminCog(commands.Cog, name="Admin"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", aliases=['sync'], description="Syncs the commands with the discord API")
    @has_role()
    async def load_commands(self, ctx: Context | Interaction):
        logging.info("Sync triggered by %s", ctx.author.global_name)
        if self.bot.tree:
            amount = await self.bot.tree.sync()
            await ctx.channel.send(f"Loaded {len(amount)} Commands (May be seen in 1h)")
        else:
            await ctx.channel.send("Command tree is not initialized.")

    @commands.command(name="clear", description="Clears all commands from the discord API")
    @has_role()
    async def clear_commands(self, ctx: Context | Interaction):
        logging.info("Clear triggered by %s", ctx.author.global_name)
        if self.bot.tree:
            await self.bot.tree.clear_commands(guild=None)
            await ctx.channel.send("Cleared all commands")
        else:
            await ctx.channel.send("Command tree is not initialized.")

    @commands.command(name="set", description="Setze das Geld eines Users")
    @has_role()
    async def _set_money(self, ctx: Context | Interaction, member: discord.Member, user_money=None):
        await set_money_command(ctx, member, user_money)

    @commands.command(name="shutdown", aliases=["quit", "close", "stop"], description="Fahre den Bot herunter")
    @has_role()
    async def _shutdown(self, ctx: Context | Interaction):
        await shutdown_command()

    @commands.command(name="reset", description="Setze den Status des Bots zurück")
    @has_role()
    async def _reset(self, ctx: Context | Interaction):
        await reset_status_command(ctx)

    @commands.command(name="setStatus", description="Setze den Status des Bots")
    @has_role()
    async def _set_status(self, ctx: Context | Interaction):
        await set_status_command(ctx)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
