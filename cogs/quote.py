from discord import Interaction
from discord.ext import commands
from discord.ext.commands import Context
from Commands.social_commands import SocialCommands


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.socialCommands = SocialCommands(bot)
        self.bot.logging.info("QuoteCog loaded")

    @commands.hybrid_command(name="quote", description="Gives a random Anime Quote")
    async def quote_slash(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um ein zufälliges Anime-Zitat auszugeben.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `anime_quote` auf, um ein zufälliges Anime-Zitat auszugeben.
        """
        await self.socialCommands.anime_quote(ctx)

    @commands.hybrid_command(name="qotd", description="Tells you the Quote of the Day")
    async def qotd_slash(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um das Zitat des Tages auszugeben.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `qotd_command` auf, um das Zitat des Tages auszugeben.
        """
        await self.socialCommands.qotd_command(ctx)

async def setup(bot):
    await bot.add_cog(QuoteCog(bot))