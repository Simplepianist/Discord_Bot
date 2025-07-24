from discord import Interaction, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from Util import variables


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear")
    @commands.is_owner()
    async def clear_commands(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um alle Befehle aus dem Befehlsbaum zu löschen.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Protokolliert, dass der Clear-Befehl ausgelöst wurde.
        - Löscht alle Befehle aus dem Befehlsbaum.
        - Sendet eine Nachricht, dass der Befehlsbaum gelöscht wurde.
        """
        self.bot.logging.info("Clear triggered by %s", ctx.author.global_name)
        self.bot.tree.clear_commands(guild=None)
        await ctx.channel.send("Clearing Tree")

    @commands.hybrid_command(name="load", aliases=['sync'])
    @commands.is_owner()
    async def load_commands(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um die Befehle des Bots zu synchronisieren.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Protokolliert, dass der Sync-Befehl ausgelöst wurde.
        - Synchronisiert die Befehle des Bots.
        - Sendet eine Nachricht, dass die Befehle geladen wurden.
        """
        self.bot.logging.info("Sync triggered by %s", ctx.author.global_name)
        await self.bot.tree.sync()
        await ctx.channel.send("Loaded Commands (May be seen in 1h)")

    @commands.hybrid_command(name="set")
    @app_commands.rename(member="person")
    @app_commands.describe(member="Person deren Geld du setzen möchtest")
    @commands.is_owner()
    async def set_money(self, ctx: Context | Interaction, member: Member, user_money=None):
        """
        Diese Funktion wird aufgerufen, um das Geld eines Benutzers zu setzen.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - member (Member): Der Benutzer, dessen Geld gesetzt werden soll.
        - user_money (optional): Der Betrag, der gesetzt werden soll. Wenn nicht angegeben,
        wird ein Standardwert verwendet.

        Aktionen:
        - Ruft die Funktion `set_money_command` auf, um das Geld des Benutzers zu setzen.
        """
        await set_money_command(ctx, member, user_money)

    @commands.hybrid_command(name="stop", aliases=["quit", "close"], description="Stoppt den Bot")
    @commands.is_owner()
    async def shutdown(self, _: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um den Bot herunterzufahren.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Setzt die globale Variable `SHUTDOWN_INITIATED` auf True.
        - Ruft die Funktion `shutdown_command` auf, um den Bot herunterzufahren.
        """
        variables.SHUTDOWN_INITIATED = True
        await shutdown_command()

    @commands.hybrid_command(name="reset")
    @commands.is_owner()
    async def reset(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um den Status des Bots zurückzusetzen.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `reset_status_command` auf, um den Status des Bots zurückzusetzen.
        """
        await reset_status_command(ctx)

    @commands.hybrid_command(name="status", description="Setzt den Status des Bots")
    @app_commands.describe(
        name="Name des Status",
        status="Status-Typ",
        art="Art des Status (nur für nicht-streaming)"
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Online", value="online"),
            app_commands.Choice(name="DND", value="dnd"),
            app_commands.Choice(name="Offline", value="offline"),
            app_commands.Choice(name="Idle", value="idle"),
            app_commands.Choice(name="Streaming", value="streaming"),
        ],
        art=[
            app_commands.Choice(name="Listening", value="listening"),
            app_commands.Choice(name="Playing", value="playing"),
        ]
    )
    @commands.is_owner()
    async def set_status(self, ctx, name: str, status: str, art: str = None):
        """
        Diese Funktion wird aufgerufen, um den Status des Bots zu setzen.
        Nur der Besitzer des Bots kann diesen Befehl ausführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `set_status_command` auf, um den Status des Bots zu setzen.
        """
        await set_status_command(ctx, name, status, art)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
