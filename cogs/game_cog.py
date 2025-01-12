import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands.context import Context
from Commands.game_commands import scoreboard_command, daily_command, send_command, money_command, \
    rob_command, blackjack_command, roulette_command, higher_lower_command
from Commands.main_commands import rules_command
from Util.util_commands import execute_gaming_with_timeout


class GameCog(commands.Cog, name="Games"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="scoreboard", aliases=["sc"], description="Scoreboard for the most :coin:")
    async def _scoreboard(self, ctx: Context | discord.Interaction):
        await scoreboard_command(ctx)

    @commands.command(name="rule", aliases=["rules"], description="Regeln der Spiele")
    async def _rules(self, ctx: Context | discord.Interaction):
        await rules_command(ctx)

    @commands.command(name="daily", description="Claim der tägliche Belohnung")
    async def _daily(self, ctx: Context | discord.Interaction):
        await daily_command(ctx)

    @commands.command(name="send", aliases=["give"], description="Gib deinen Freunden etwas Geld")
    async def _send(self, ctx: Context | discord.Interaction, member: discord.Member, set_money: int = None):
        await send_command(ctx, member, set_money)

    @commands.command(name="money", aliases=["bal"], description="Check dein Geld oder das von anderen")
    async def _money(self, ctx: Context | discord.Interaction, may_member: discord.Member = None):
        await money_command(ctx, may_member)

    @commands.command(name="rob", description="Raube von anderen Spielern oder der Bank")
    async def _robbing(self, ctx: Context | discord.Interaction, may_member: discord.Member = None):
        await execute_gaming_with_timeout(ctx, rob_command, may_member)

    @commands.command(name="blackjack", aliases=["bj"], description="Spiele etwas Blackjack")
    async def _blackjack(self, ctx: Context | discord.Interaction, bet: int):
        await execute_gaming_with_timeout(ctx, blackjack_command, bet)

    @commands.command(name="roulette", aliases=["rl"], description="Spiele etwas Roulette")
    async def _roulette(self, ctx: Context | discord.Interaction, bet: int, entry: str):
        await execute_gaming_with_timeout(ctx, roulette_command, bet, entry)

    @commands.command(name="higherlower", aliases=["hl"], description="Spiele etwas HigherLower")
    async def _higher_lower(self, ctx: Context | discord.Interaction, bet: int):
        await execute_gaming_with_timeout(ctx, higher_lower_command, bet)

    # Slash commands
    @app_commands.command(name="scoreboard", description="Scoreboard for the most :coin:")
    async def scoreboard(self, ctx: Context | discord.Interaction):
        await scoreboard_command(ctx)

    @app_commands.command(name="rule", description="Regeln der Spiele")
    async def rules(self, ctx: Context | discord.Interaction):
        await rules_command(ctx)

    @app_commands.command(name="daily", description="Claim der tägliche Belohnung")
    async def daily(self, ctx: Context | discord.Interaction):
        await daily_command(ctx)

    @app_commands.command(name="give", description="Gib deinen Freunden etwas Geld")
    @app_commands.describe(member="Person die Geld bekommt")
    @app_commands.rename(member="person")
    @app_commands.describe(set_money="Geld das du versendest")
    @app_commands.rename(set_money="geld")
    async def send(self, ctx: Context | discord.Interaction, member: discord.Member, set_money: int = None):
        await send_command(ctx, member, set_money)

    @app_commands.command(name="money", description="Check dein Geld oder das von anderen")
    @app_commands.describe(may_member="Person die du checken möchtest")
    @app_commands.rename(may_member="person")
    async def money(self, ctx: Context | discord.Interaction, may_member: discord.Member = None):
        await money_command(ctx, may_member)

    @app_commands.command(name="rob", description="Raube von anderen Spielern oder der Bank")
    @app_commands.describe(may_member="Wähle eine Spieler oder Raube lieber die Bank (default)")
    @app_commands.rename(may_member="person")
    async def robbing(self, ctx: Context | discord.Interaction, may_member: discord.Member = None):
        await execute_gaming_with_timeout(ctx, rob_command, may_member)

    @app_commands.command(name="blackjack", description="Spiele etwas Blackjack")
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    async def blackjack(self, ctx: Context | discord.Interaction, bet: int):
        await execute_gaming_with_timeout(ctx, blackjack_command, bet)

    @app_commands.command(name="roulette", description="Spiele etwas Roulette")
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    @app_commands.describe(entry="Auf was wettest du")
    @app_commands.rename(entry="wettstein")
    async def roulette(self, ctx: Context | discord.Interaction, bet: int, entry: str):
        await execute_gaming_with_timeout(ctx, roulette_command, bet, entry)

    @app_commands.command(name="higherlower", description="Spiele etwas HigherLower")
    @app_commands.describe(bet="Wieviel du setzen möchtest")
    @app_commands.rename(bet="einsatz")
    async def higher_lower(self, ctx: Context | discord.Interaction, bet: int):
        await execute_gaming_with_timeout(ctx, higher_lower_command, bet)

    # Register the commands
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.tree.get_command("scoreboard"):
            self.bot.tree.add_command(self.scoreboard)
        if not self.bot.tree.get_command("rule"):
            self.bot.tree.add_command(self.rules)
        if not self.bot.tree.get_command("daily"):
            self.bot.tree.add_command(self.daily)
        if not self.bot.tree.get_command("give"):
            self.bot.tree.add_command(self.send)
        if not self.bot.tree.get_command("money"):
            self.bot.tree.add_command(self.money)
        if not self.bot.tree.get_command("rob"):
            self.bot.tree.add_command(self.robbing)
        if not self.bot.tree.get_command("blackjack"):
            self.bot.tree.add_command(self.blackjack)
        if not self.bot.tree.get_command("roulette"):
            self.bot.tree.add_command(self.roulette)
        if not self.bot.tree.get_command("higherlower"):
            self.bot.tree.add_command(self.higher_lower)


async def setup(setup_bot):
    await setup_bot.add_cog(GameCog(setup_bot))
