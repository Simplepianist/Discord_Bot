import os
import pytest_asyncio
import pytest
import discord
import discord.ext.test as dpytest
from discord.ext.commands import CommandRegistrationError
from simplebot import SimpleBot
from unittest.mock import AsyncMock, MagicMock

# Hilfsfunktion für Intents
def getIntents():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    return intents

@pytest_asyncio.fixture(scope="module")
async def bot():
    intents = getIntents()
    app_id = os.getenv("APPLICATION_ID", "1234567890")
    b = SimpleBot(command_prefix="!", intents=intents, application_id=int(app_id), owner_id=int(app_id))
    b.remove_command("help")
    await b._async_setup_hook()
    try:
        await b.load_extension("cogs.gaming")
    except CommandRegistrationError:
        pass
    dpytest.configure(b)
    yield b
    await dpytest.empty_queue()

@pytest.mark.asyncio
async def test_money_command_shows_own_balance(bot):
    games = bot.cogs["GamingCog"].games
    games.utils.get_money_for_user = AsyncMock(return_value=1000)
    games.utils.return_author = AsyncMock(return_value=MagicMock(spec=discord.Member))
    await dpytest.message("!money")
    dpytest.verify().message().content("Du hast aktuell 1000 :coin:")

@pytest.mark.asyncio
async def test_money_command_shows_other_user_balance(bot):
    games = bot.cogs["GamingCog"].games
    games.utils.get_money_for_user = AsyncMock(return_value=500)
    member = MagicMock(spec=discord.Member)
    member.name = "TestUser"
    member.bot = False
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.money_command(ctx, member)
    ctx.send.assert_awaited_with("TestUser hat aktuell 500 :coin:")

@pytest.mark.asyncio
async def test_money_command_rejects_bot_user(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.bot = True
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.money_command(ctx, member)
    ctx.send.assert_awaited_with("Bitte nicht die Bots pingen", delete_after=20)

@pytest.mark.asyncio
async def test_send_command_rejects_self_transfer(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.bot = False
    games.utils.return_author = MagicMock(return_value=member)
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.send_command(ctx, member, 100)
    ctx.send.assert_awaited_with("Du kannst dir selbst kein Geld senden", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_send_command_rejects_negative_amount(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.name = "User"
    member.bot = False
    other = MagicMock(spec=discord.Member)
    other.name = "other"
    other.bot = False
    games.utils.return_author = AsyncMock(return_value=member)
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.send_command(ctx, other, -50)
    ctx.send.assert_awaited_with("Betrag muss positiv sein", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_send_command_rejects_bot_member(bot):
    games = bot.cogs["GamingCog"].games
    bot_member = MagicMock(spec=discord.Member)
    bot_member.bot = True
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.send_command(ctx, bot_member, 100)
    ctx.send.assert_awaited_with("Bitte nicht die Bots pingen")

@pytest.mark.asyncio
async def test_daily_command_without_streak(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.id = 1
    member.name = "User"
    games.utils.return_author = MagicMock(return_value=member)
    games.utils.get_daily = AsyncMock(return_value=True)
    games.utils.get_money_for_user = AsyncMock(return_value=100)
    bot.db.update_streak_and_get_bonus = AsyncMock(return_value=0)
    bot.db.set_money_for_user = AsyncMock()
    bot.db.set_daily = AsyncMock()
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.daily_command(ctx)
    ctx.send.assert_awaited_with("Du hast 300 Coins erhalten.\n" +
                               "**Total: 400 Coins**")
    bot.db.set_money_for_user.assert_awaited()
    bot.db.set_daily.assert_awaited()

@pytest.mark.asyncio
async def test_daily_command_with_streak(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.id = 1
    member.name = "User"
    games.utils.return_author = MagicMock(return_value=member)
    games.utils.get_daily = AsyncMock(return_value=True)
    games.utils.get_money_for_user = AsyncMock(return_value=100)
    bot.db.update_streak_and_get_bonus = AsyncMock(return_value=15)
    bot.db.set_money_for_user = AsyncMock()
    bot.db.set_daily = AsyncMock()
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.daily_command(ctx)
    ctx.send.assert_awaited_with("Du hast 315 Coins erhalten.\n" +
                               "**Total: 415 Coins**")
    bot.db.set_money_for_user.assert_awaited()
    bot.db.set_daily.assert_awaited()

@pytest.mark.asyncio
async def test_daily_command_rejects_multiple_claims(bot):
    games = bot.cogs["GamingCog"].games
    member = MagicMock(spec=discord.Member)
    member.id = 1
    member.name = "User"
    games.utils.return_author = AsyncMock(return_value=member)
    games.utils.get_daily = AsyncMock(return_value=False)
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await games.daily_command(ctx)
    ctx.send.assert_awaited_with("**Du hast dein Daily heute schon geclaimed**")
