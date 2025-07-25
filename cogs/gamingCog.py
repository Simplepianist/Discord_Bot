from discord import Interaction, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from Commands.game_commands import GamingCommands
from Commands.main_commands import MainCommands


class GamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = GamingCommands(bot)
        self.mainCommands = MainCommands(bot)

    @commands.hybrid_command(name="rule", aliases=["rules"], description="Hier findest du Regeln der Spiele")
    async def rules(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um die Regeln anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `rules_command` auf, um die Regeln anzuzeigen.
        """
        await self.mainCommands.rules_command(ctx)

    @commands.hybrid_command(name="scoreboard", aliases=["sc"], description="Scoreboard für die meisten :coin:")
    async def scoreboard(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um das Scoreboard für die meisten Coins anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `scoreboard_command` auf, um das Scoreboard anzuzeigen.
        """
        await self.games.scoreboard_command(ctx)

    @commands.hybrid_command(name="daily")
    async def daily(self, ctx: Context | Interaction):
        """
        Diese Funktion wird aufgerufen, um den täglichen Befehl auszuführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

        Aktionen:
        - Ruft die Funktion `daily_command` auf, um den täglichen Befehl auszuführen.
        """
        await self.games.daily_command(ctx)

    @commands.hybrid_command(name="send", description="Gib Geld an andere")
    @app_commands.describe(member="Person die Geld bekommt")
    @app_commands.rename(member="person")
    @app_commands.describe(money_to_set="Geld das du versendest")
    @app_commands.rename(money_to_set="geld")
    async def send_slash(self, ctx: Context | Interaction, member: Member, money_to_set: int):
        """
        Diese Funktion wird aufgerufen, um Geld an einen anderen Benutzer zu senden.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - member (Member): Der Benutzer, der das Geld erhalten soll.
        - set_money (int): Der Betrag, der gesendet werden soll.

        Aktionen:
        - Ruft die Funktion `send_command` auf, um das Geld zu senden.
        """
        await self.games.send_command(ctx, member, money_to_set)

    @commands.hybrid_command(name="money", description="Zeigt dein Geld an", aliases=["bal"])
    @app_commands.describe(user="User dessen Geld du sehen möchtest")
    @app_commands.rename(user="person")
    async def money(self, ctx: Context | Interaction, user: Member = None):
        """
        Diese Funktion wird aufgerufen, um das Geld eines Benutzers anzuzeigen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - may_member (Member, optional): Der Benutzer, dessen Geld angezeigt werden soll.
        Standardmäßig None.

        Aktionen:
        - Ruft die Funktion `money_command` auf, um das Geld des Benutzers anzuzeigen.
        """
        await self.games.money_command(ctx, user)

    @commands.hybrid_command(name="blackjack", description="Play a game of blackjack", aliases=["bj"])
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    async def blackjack_slash(self, ctx: Context | Interaction, bet: int):
        """
        Diese Funktion wird aufgerufen, um eine Runde Blackjack zu spielen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - bet (int): Der Einsatzbetrag für das Spiel.

        Aktionen:
        - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Blackjack zu spielen.
        """
        await self.games.execute_gaming_with_timeout(ctx, self.games.blackjack_command, bet)

    @commands.hybrid_command(name="roulette", description="Spiel ein bisschen Roulette")
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    @app_commands.describe(entry="Auf was wettest du")
    @app_commands.rename(entry="wettstein")
    async def roulette_slash(self, ctx: Context | Interaction, bet: int, entry: str):
        """
        Diese Funktion wird aufgerufen, um eine Runde Roulette zu spielen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - bet (int): Der Einsatzbetrag für das Spiel.
        - entry (str): Die Wette, die der Benutzer platzieren möchte.

        Aktionen:
        - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Roulette zu spielen.
        """
        await self.games.execute_gaming_with_timeout(ctx, self.games.roulette_command, bet, entry)

    @commands.hybrid_command(name="higherlower", description="Spiel ein bisschen Higher/Lower")
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    async def higher_lower_slash(self, ctx: Context | Interaction, bet: int):
        """
        Diese Funktion wird aufgerufen, um eine Runde Higher/Lower zu spielen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - bet (int): Der Einsatzbetrag für das Spiel.

        Aktionen:
        - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Higher/Lower zu spielen.
        """
        await self.games.execute_gaming_with_timeout(ctx, self.games.higher_lower_command, bet)

    @commands.hybrid_command(name="rob", description="Raube die Bank oder einen Spieler")
    @app_commands.describe(may_member="Wähle eine Spieler oder Raube lieber die Bank")
    @app_commands.rename(may_member="person")
    async def robbing_slash(self, ctx: Context | Interaction, may_member: Member = None):
        """
        Diese Funktion wird aufgerufen, um den Raubbefehl auszuführen.

        Parameter:
        - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
        - may_member (Member, optional): Der Benutzer, der ausgeraubt werden soll. Standardmäßig None.

        Aktionen:
        - Ruft die Funktion `execute_gaming_with_timeout` auf, um den Raubbefehl auszuführen.
        """
        await self.games.execute_gaming_with_timeout(ctx, self.games.rob_command, may_member)

async def setup(bot):
    await bot.add_cog(GamingCog(bot))