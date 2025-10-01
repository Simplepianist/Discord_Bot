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
    b = SimpleBot(command_prefix="!", intents=intents, application_id=int(app_id))
    b.remove_command("help")
    await b._async_setup_hook()
    try:
        await b.load_extension("cogs.main")
    except CommandRegistrationError:
        pass
    dpytest.configure(b)
    yield b
    await dpytest.empty_queue()

@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("!ping")
    dpytest.verify().message().content("PONG!!!")

@pytest.mark.asyncio
async def test_help_command_sends_category_dropdown(bot):
    await dpytest.message("!help")
    dpytest.verify().message().content("Wähle eine Category")

@pytest.mark.asyncio
async def test_alias_command_sends_alias_dropdown(bot):
    await dpytest.message("!alias")
    dpytest.verify().message().content("Wähle eine Category")

@pytest.mark.asyncio
async def test_invite_command_sends_invite_link(bot):
    await dpytest.message("!invite")
    dpytest.verify().message().content(bot.config["inviteLink"])

@pytest.mark.asyncio
async def test_stream_command_sends_stream_url(bot):
    await dpytest.message("!stream")
    dpytest.verify().message().content(bot.config["streamURL"])