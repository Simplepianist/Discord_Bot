import sys
import os
import pytest_asyncio

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
    b = SimpleBot(command_prefix="!", intents=intents, application_id=int(app_id), owner_id=int(app_id))
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
async def test_clear_commands_raises_not_owner_for_non_owner(bot):
    bot.owner_id = 999999999  # Setze auf eine andere ID
    with pytest.raises(Exception) as excinfo:
        await dpytest.message("!clear")
    assert "you do not own this bot." in str(excinfo.value).lower()