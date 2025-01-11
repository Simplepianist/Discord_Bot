"""
This module contains commands for interacting with social APIs,
such as fetching anime quotes and quotes of the day.

Functions:
    anime_quote(ctx: Context | Interaction):
        Fetches an anime quote and sends it as an embed message.
    qotd_command(ctx: Context | Interaction):
        Fetches the quote of the day and sends it as an embed message.
"""
from discord import Interaction
from discord.ext.commands import Context
from API.quote import animequote, qotd
from API.anime import get_anime_character_image
from Util.util_commands import create_social_embed, send_message


async def anime_quote(ctx: Context | Interaction):
    """
    Fetches an anime quote and sends it as an embed message.

    Args:
        ctx (Context | Interaction): The context or interaction from Discord.
    """
    data = animequote()
    character = data["author"]
    anime = data["anime"]
    quote = data["quote"]
    embed = create_social_embed(ctx, 0x6a329f, "Anime Quote")
    embed.add_field(name=f"*{character}* ({anime})", value=quote)
    url = get_anime_character_image(character)
    if url:
        embed.set_thumbnail(url=url)
    await send_message(ctx, embed=embed)

async def qotd_command(ctx: Context | Interaction):
    """
    Fetches the quote of the day and sends it as an embed message.

    Args:
        ctx (Context | Interaction): The context or interaction from Discord.
    """
    data = qotd()
    if not data:
        await send_message(ctx, "Error fetching quote of the day")
        return
    embed = create_social_embed(ctx, 0x6a329f, "Quote of the Day")
    embed.add_field(name = f"*{data['a']}*", value=data["q"])
    await send_message(ctx, embed=embed)
