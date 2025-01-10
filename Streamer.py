from Commands.main_commands import *
from Commands.admin_commands import *
from Commands.social_commands import *
from Commands.game_commands import Games
from discord import app_commands
from discord.ext.commands.context import Context
from Util import variables
from Util.variables import bot, test


games = Games()

@bot.event
async def on_ready():
    logging.basicConfig(filename="./logs/Bot.log", level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    await bot.tree.sync()
    logging.info("Sync gestartet (1h)")
    variables.owner = await bot.fetch_user(325779745436467201)
    await bot.change_presence(activity=discord.Streaming(name=".help", url=variables.streamURL))


"""
.-Commands
"""


@bot.command(name="clear")
@commands.is_owner()
async def clearCommands(ctx: Context | Interaction):
    logging.info("Clear triggered by" + ctx.author.global_name)
    bot.tree.clear_commands(guild=None)
    await ctx.channel.send("Clearing Tree")


@bot.command(name="load", aliases=['sync'])
@commands.is_owner()
async def loadCommands(ctx: Context | Interaction):
    logging.info("Sync triggered by " + ctx.author.global_name)
    await bot.tree.sync()
    await ctx.channel.send("Loaded Commands (May be seen in 1h)")


@bot.command(name="set")
@commands.is_owner()
async def _setMoney(ctx: Context | Interaction, member: discord.Member, user_money=None):
    await setMoneyCommand(ctx, member, user_money)


@bot.command(aliases=["quit", "close", "stop"])
@commands.is_owner()
async def _shutdown(ctx: Context | Interaction):
    await shutdownCommand()


@bot.command(name="reset")
@commands.is_owner()
async def _reset(ctx: Context | Interaction):
    await resetStatusCommand(ctx)


@bot.command(name="setStatus")
@commands.is_owner()
async def _setStatus(ctx: Context | Interaction):
    await setStatusCommand(ctx)


@bot.tree.command(name="help", description="Gives you the Help-Menu")
async def _help(ctx: Context | Interaction):
    await helpCommand(ctx)


@bot.command(name="help")
async def _help(ctx: Context | Interaction):
    await helpCommand(ctx)


@bot.command(name="rule", aliases=["rules"])
async def _rules(ctx: Context | Interaction):
    await rulesCommand(ctx)


@bot.command(name="alias", aliases=["a"], description="Aliasliste der Befehle")
async def _aliases(ctx: Context | Interaction):
    await aliasCommand(ctx)


@bot.command(name="ping", description="Pong")
async def _ping(ctx: Context | Interaction):
    await pingCommand(ctx)


@bot.command(name="invite", aliases=["i"], description="Invite-link für diesen Server")
async def _invite(ctx: Context | Interaction):
    await inviteCommand(ctx)


@bot.command(name="stream", aliases=["s"], description="Streamlink von Simplebox")
async def _stream(ctx: Context | Interaction):
    await streamCommand(ctx)


@bot.command(name="scoreboard", aliases=["sc"], description="Scoreboard für die meisten :coin:")
async def _scoreboard(ctx: Context | Interaction):
    await games.scoreboardCommand(ctx)


@bot.command(name="daily")
async def _daily(ctx: Context | Interaction):
    await games.dailyCommand(ctx)


@bot.command(name="send", aliases=["give"])
async def _send(ctx: Context | Interaction, member: discord.Member, set_money: int = None):
    await games.sendCommand(ctx, member, set_money)


@bot.command(name="money", aliases=["bal"])
async def _money(ctx: Context | Interaction, may_member: discord.Member = None):
    await games.moneyCommand(ctx, may_member)

@bot.command(name="rob")
async def _robbing(ctx: Context | Interaction, may_member: discord.Member = None):
    await execute_gaming_with_timeout(ctx, games.robCommand, may_member)

@bot.command(name="blackjack", aliases=["bj"])
async def _blackjack(ctx: Context | Interaction, bet: int):
    await execute_gaming_with_timeout(ctx, games.blackjackCommand, bet)

@bot.command(name="roulette", aliases=["rl"])
async def _roulette(ctx: Context | Interaction, bet: int, entry: str):
    await execute_gaming_with_timeout(ctx, games.rouletteCommand, bet, entry)

@bot.command(name="higher low", aliases=["hl", "higherlower"])
async def _higherLower(ctx: Context | Interaction, bet: int):
    await execute_gaming_with_timeout(ctx, games.higherLowerCommand, bet)


@bot.command(name="quote")
async def _quote(ctx: Context | Interaction):
    await anime_quote(ctx)


@bot.command(name="qotd")
async def _qotd(ctx: Context | Interaction):
    await qotd_command(ctx)


"""
Tree-Commands
"""


@bot.tree.command(name="rules", description="Hier findest du Regeln der Spiele")
async def rules(ctx: Context | Interaction):
    await rulesCommand(ctx)


@bot.tree.command(name="alias", description="Aliasliste aller Befehle")
async def aliases(ctx: Context | Interaction):
    await aliasCommand(ctx)


@bot.tree.command(name="ping", description="Pong")
async def ping(ctx: Context | Interaction):
    await pingCommand(ctx)


@bot.tree.command(name="invite", description="Invite-link für diesen Server")
async def invite(ctx: Context | Interaction):
    await inviteCommand(ctx)


@bot.tree.command(name="stream", description="Streamlink von Simplebox")
async def stream(ctx: Context | Interaction):
    await streamCommand(ctx)


@bot.tree.command(name="scoreboard", description="Scoreboard für die Games")
async def scoreboard(ctx: Context | Interaction):
    await games.scoreboardCommand(ctx)


@bot.tree.command(name="daily", description="Gönn dir dein Daily")
async def daily(ctx: Context | Interaction):
    await games.dailyCommand(ctx)


@bot.tree.command(name="send", description="Gib Geld an andere")
@app_commands.describe(member="Person die Geld bekommt")
@app_commands.rename(member="person")
@app_commands.describe(set_money="Geld das du versendest")
@app_commands.rename(set_money="geld")
async def send(ctx: Context | Interaction, member: discord.Member, set_money: int):
    await games.sendCommand(ctx, member, set_money)


@bot.tree.command(name="money", description="Check das Geld")
@app_commands.describe(may_member="Person die du checken möchtest")
@app_commands.rename(may_member="person")
async def money(ctx: Context | Interaction, may_member: discord.Member = None):
    await games.moneyCommand(ctx, may_member)


@bot.tree.command(name="blackjack", description="Play a game of blackjack")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
async def blackjack(ctx: Context | Interaction, bet: int):
    await execute_gaming_with_timeout(ctx, games.blackjackCommand, bet)


@bot.tree.command(name="roulette", description="Spiel ein bisschen Roulette")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
@app_commands.describe(entry="Auf was wettest du")
@app_commands.rename(entry="wettstein")
async def roulette(ctx: Context | Interaction, bet: int, entry: str):
    await execute_gaming_with_timeout(ctx, games.rouletteCommand, bet, entry)

@bot.tree.command(name="higherlower", description="Spiel ein bisschen Higher/Lower")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
async def higherLower(ctx: Context | Interaction, bet: int):
    await execute_gaming_with_timeout(ctx, games.higherLowerCommand, bet)

@bot.tree.command(name="rob", description="Raube die Bank oder einen Spieler")
@app_commands.describe(may_member="Wähle eine Spieler oder Raube lieber die Bank")
@app_commands.rename(may_member="person")
async def robbing(ctx: Context | Interaction, may_member: discord.Member = None):
    await execute_gaming_with_timeout(ctx, games.robCommand, may_member)


@bot.tree.command(name="quote", description="Gives a random Anime Quote")
async def quote(ctx: Context | Interaction):
    await anime_quote(ctx)


@bot.tree.command(name="qotd", description="Tells you the Quote of the Day")
async def qotd(ctx: Context | Interaction):
    await qotd_command(ctx)


bot.run(os.environ["token"])
