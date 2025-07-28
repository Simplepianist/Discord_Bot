from discord import Interaction, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from Commands.main_commands import MainCommands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainCommands = MainCommands(bot)
        self.bot.logging.info("MainCog loaded")

    @commands.hybrid_command(name="help", description="Gives you the Help-Menu", aliases=["h"])
    async def help_menu_slash(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um das Hilfemenü anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `help_command` auf, um das Hilfemenü anzuzeigen.
        """
        await self.mainCommands.help_command(ctx)

    @commands.hybrid_command(name="alias", aliases=["a"], description="Aliasliste der Befehle")
    async def aliases(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um die Aliasliste der Befehle anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `alias_command` auf, um die Aliasliste der Befehle anzuzeigen.
        """
        await self.mainCommands.alias_command(ctx)

    @commands.hybrid_command(name="ping", description="Pong")
    async def ping(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um auf den Ping-Befehl zu antworten.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `ping_command` auf, um mit "Pong" zu antworten.
        """
        await self.mainCommands.ping_command(ctx)

    @commands.hybrid_command(name="invite", aliases=["i"], description="Invite-link für diesen Server")
    async def invite(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um den Einladungslink für den Server anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `invite_command` auf, um den Einladungslink anzuzeigen.
        """
        await self.mainCommands.invite_command(ctx)

    @commands.hybrid_command(name="stream", aliases=["s"], description="Streamlink von Simplebox")
    async def stream(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um den Streamlink von Simplebox anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `stream_command` auf, um den Streamlink anzuzeigen.
        """
        await self.mainCommands.stream_command(ctx)


async def setup(bot):
    await bot.add_cog(MainCog(bot))