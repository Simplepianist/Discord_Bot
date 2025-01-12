import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.context import Context
from Commands.social_commands import anime_quote, qotd_command


class SocialCog(commands.Cog, name="Social"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="quote", description="Hol dir ein zufälliges Anime-Zitat")
    async def _quote(self, ctx: Context | discord.Interaction):
        await anime_quote(ctx)

    @commands.command(name="qotd", description="Hol dir das Zitat des Tages")
    async def _qotd(self, ctx: Context | discord.Interaction):
        await qotd_command(ctx)

    @app_commands.command(name="quote", description="Hol dir ein zufälliges Anime-Zitat")
    async def quote(self, ctx: Context | discord.Interaction):
        await anime_quote(ctx)

    @app_commands.command(name="qotd", description="Hol dir das Zitat des Tages")
    async def qotd(self, ctx: Context | discord.Interaction):
        await qotd_command(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.tree.get_command("quote"):
            self.bot.tree.add_command(self.quote)
        if not self.bot.tree.get_command("qotd"):
            self.bot.tree.add_command(self.qotd)

async def setup(bot):
    await bot.add_cog(SocialCog(bot))
