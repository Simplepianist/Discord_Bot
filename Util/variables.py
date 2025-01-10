import json
import os
import discord
from discord.ext import commands

def load_config(name):
    with open("jsons/config.json") as f:
        json_file = json.load(f)
    try:
        json_file["embed"]["embeds_footerpic"] = owner.avatar
    except:
        pass
    return json_file[name]

test: bool = load_config("test")
intents = discord.Intents.default()
intents.all()
intents.members = True
intents.message_content = True
currentlyGaming = []
bot = commands.Bot(command_prefix=".", help_command=None, intents=intents, case_insensitive=True)
owner: discord.Member = None
botRole = load_config("botrole")
streamURL = load_config("streamURL")
inviteLink = load_config("inviteLink")