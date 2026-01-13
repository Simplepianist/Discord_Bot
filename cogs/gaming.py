from discord import Interaction, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from Commands.main_commands import MainCommands
from games import BlackjackGame, RouletteGame, HigherLowerGame, GameManager


class GamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_manager = GameManager(bot)
        self.mainCommands = MainCommands(bot)
        self.bot.logging.info("GamingCog loaded")

    def _return_author(self, ctx: Context | Interaction) -> Member:
        """Helper to get the command author."""
        return ctx.user if isinstance(ctx, Interaction) else ctx.author

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
        """Play a game of blackjack (21)."""
        author = self._return_author(ctx)

        # Validate bet
        is_valid, error_msg = await self.game_manager.validate_bet(ctx, bet)
        if not is_valid:
            await ctx.send(f"❌ {error_msg}", ephemeral=True, delete_after=5)
            return

        # Create and execute game
        game = BlackjackGame(author, bet)
        await self.game_manager.execute_game(ctx, game, author)

    @commands.hybrid_command(name="roulette", description="Play roulette", aliases=["rl"])
    @app_commands.describe(
        bet="Amount to bet",
        wager="What to bet on (number 0-36, or color: red/black/green)"
    )
    async def roulette(self, ctx: Context | Interaction, bet: int, wager: str):
        """Play roulette by betting on numbers or colors."""
        author = self._return_author(ctx)

        # Validate bet
        is_valid, error_msg = await self.game_manager.validate_bet(ctx, bet)
        if not is_valid:
            await ctx.send(f"❌ {error_msg}", ephemeral=True, delete_after=5)
            return

        # Create game
        game = RouletteGame(author, bet, wager)

        # Validate wager
        if not game.is_valid_bet():
            await ctx.send(
                "❌ Invalid wager! Valid options:\n"
                "• Numbers: 0-36\n"
                "• Colors: red, black, green",
                ephemeral=True,
                delete_after=10
            )
            return

        # Execute game
        await self.game_manager.execute_game(ctx, game, author)

    @commands.hybrid_command(name="higherlower", description="Spiel ein bisschen Higher/Lower", aliases=["hl"])
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
        author = self._return_author(ctx)

        # Validate bet
        is_valid, error_msg = await self.game_manager.validate_bet(ctx, bet)
        if not is_valid:
            await ctx.send(f"❌ {error_msg}", ephemeral=True, delete_after=5)
            return

        # Create game
        game = HigherLowerGame(author, bet)
        await self.game_manager.execute_game(ctx, game, author)

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