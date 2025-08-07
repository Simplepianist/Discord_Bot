import os
import logging
import discord

from simplebot import SimpleBot

# Configure logging ONCE at the top, before anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('bot.log')  # File output
    ],
    force=True
)

# Suppress specific loggers AFTER basic config
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
# More aggressive alembic logging suppression
logging.getLogger('alembic').setLevel(logging.WARNING)
logging.getLogger('alembic.runtime.migration').setLevel(logging.WARNING)
logging.getLogger('alembic.ddl.postgresql').setLevel(logging.WARNING)

# Keep our important loggers at INFO level
logging.getLogger('SimpleBot').setLevel(logging.INFO)
logging.getLogger('DbController').setLevel(logging.INFO)

intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
simpleBot = SimpleBot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True, owner_id=int(os.getenv("OWNER_ID", "325779745436467201")))

try:
    simpleBot.run(os.environ["token"])
finally:
    logging.shutdown()