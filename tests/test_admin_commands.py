import sys
import os
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import discord
import discord.ext.test as dpytest
from discord.ext.commands import CommandRegistrationError
from simplebot import SimpleBot

def getIntents():
    intents = discord.Intents.default()
    intents.all()
    intents.members = True
    intents.message_content = True
    return intents

@pytest_asyncio.fixture(scope="module")
async def bot():
    intents = getIntents()
    app_id = os.getenv("APPLICATION_ID")
    b = SimpleBot(command_prefix="!", intents=intents, application_id=int(app_id))
    b.remove_command("help")
    await b._async_setup_hook()
    try:
        await b.load_extension("cogs.admin")
    except CommandRegistrationError:
        pass
    dpytest.configure(b)
    yield b
    await dpytest.empty_queue()

@pytest.mark.asyncio
async def test_shutdown_command_closes_bot(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    bot.close = AsyncMock()
    await admin.shutdown_command()
    bot.close.assert_awaited()

@pytest.mark.asyncio
async def test_reset_status_command_sets_streaming_for_admin(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    admin.utils.check_admin = MagicMock(return_value=True)
    bot.change_presence = AsyncMock()
    bot.config = {"streamURL": "https://twitch.tv/stream"}
    await admin.reset_status_command(ctx)
    bot.change_presence.assert_awaited()

@pytest.mark.asyncio
async def test_reset_status_command_rejects_non_admin(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    admin.utils.check_admin = MagicMock(return_value=False)
    await admin.reset_status_command(ctx)
    ctx.send.assert_awaited_with("Piss dich ", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_set_status_command_sets_streaming(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    admin.utils.check_admin = MagicMock(return_value=True)
    bot.change_presence = AsyncMock()
    bot.config = {"streamURL": "https://twitch.tv/stream"}
    await admin.set_status_command(ctx, "Test", "streaming")
    bot.change_presence.assert_awaited()
    ctx.send.assert_awaited_with("Status geändert zu Streaming")

@pytest.mark.asyncio
async def test_set_status_command_rejects_non_admin(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    admin.utils.check_admin = MagicMock(return_value=False)
    await admin.set_status_command(ctx, "Test", "online", "playing")
    ctx.send.assert_awaited_with("Keine Berechtigung", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_set_status_command_requires_art_for_non_streaming(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    admin.utils.check_admin = MagicMock(return_value=True)
    await admin.set_status_command(ctx, "Test", "online")
    ctx.send.assert_awaited_with("Art muss angegeben werden (listening/playing)")

@pytest.mark.asyncio
async def test_set_money_command_sets_money_for_user(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    member = MagicMock()
    member.name = "User"
    member.discriminator = 0
    member.id = 123
    admin.bot.db.set_money_for_user = AsyncMock()
    admin.utils.get_money_for_user = AsyncMock(return_value=100)
    admin.utils.return_author = MagicMock(return_value=member)
    await admin.set_money_command(ctx, member, 100)
    admin.bot.db.set_money_for_user.assert_awaited_with(123, 100)
    ctx.send.assert_awaited()

@pytest.mark.asyncio
async def test_set_money_command_rejects_negative_amount(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    member = MagicMock()
    member.name = "User"
    member.discriminator = 0
    member.id = 123
    await admin.set_money_command(ctx, member, -50)
    ctx.send.assert_awaited_with("Betrag muss positiv sein", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_set_money_command_rejects_no_amount(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    member = MagicMock()
    member.name = "User"
    member.discriminator = 0
    member.id = 123
    await admin.set_money_command(ctx, member, None)
    ctx.send.assert_awaited_with("Betrag muss angegeben sein", ephemeral=True, delete_after=5)

@pytest.mark.asyncio
async def test_set_money_command_rejects_invalid_amount(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    member = MagicMock()
    member.name = "User"
    member.discriminator = 0
    member.id = 123
    await admin.set_money_command(ctx, member, "abc")
    ctx.send.assert_awaited_with("Falsche Parameter übergeben")

@pytest.mark.asyncio
async def test_set_money_command_rejects_no_member(bot):
    admin = bot.cogs["AdminCog"].adminCommands
    ctx = MagicMock()
    ctx.send = AsyncMock()
    await admin.set_money_command(ctx, None, 100)
    ctx.send.assert_awaited_with("Kein Spieler angegeben", ephemeral=True, delete_after=5)
