import time

import discord
from discord.ui import Button
from Game.Blackjack import Blackjack
from Game.Higher_Lower import Higher_Lower
import Util.variables
from Util.util_commands import *
from API.quote import Quote
from API.anime import Anime

quoteServce = Quote()
animeServce = Anime()

async def anime_quote(ctx: Context | Interaction):
    data = quoteServce.anime_Quote()
    character = data["author"]
    anime = data["anime"]
    quote = data["quote"]
    embed = create_social_embed(ctx, 0x6a329f, f"Anime Quote")
    embed.add_field(name=f"*{character}* ({anime})", value=quote)
    url = animeServce.get_anime_character_image(character)
    if url:
        embed.set_thumbnail(url=url)
    await send_message(ctx, embed=embed)

async def qotd_command(ctx: Context | Interaction):
    data = quoteServce.qotd()
    embed = create_social_embed(ctx, 0x6a329f, f"Quote of the Day")
    embed.add_field(name = f"*{data['a']}*", value=data["q"])
    await send_message(ctx, embed=embed)