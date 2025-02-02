"""
Utility and Gaming Commands Module

This module contains utility functions and gaming-related commands for a Discord bot.
It includes functions for role checking, configuration loading, message sending, and gaming logic.
"""
import asyncio
import json
import os
from http.client import HTTPException
from fastapi import HTTPException as fastapiHTTPException, Security
from fastapi.security import api_key
from starlette import status
from discord import Interaction, Member, Embed, Colour, ui
from discord.ext.commands import Context, check

from Util.variables import botRole, currentlyGaming, OWNER, bot
from config_loader import Loader

db = bot.db

#region Utility
def has_role():
    """
    Check if the user has the required role.

    Returns:
        function: A predicate function to check the user's roles.
    """
    async def predicate(ctx: Context):
        return botRole in [y.name.lower() for y in ctx.author.roles]
    return check(predicate)

def load_config(name):
    """
    Load configuration from a JSON file.

    Args:
        name (str): The name of the configuration to load.

    Returns:
        dict: The loaded configuration.
    """
    with open("jsons/config.json") as f:
        json_file = json.load(f)
    try:
        json_file["embed"]["embeds_footerpic"] = OWNER.avatar
    except KeyError:
        pass
    return json_file[name]

def check_admin(ctx: Context | Interaction):
    """
    Check if the user is an admin.

    Args:
        ctx (Context | Interaction): The context or interaction.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    if botRole in [y.name.lower() for y in return_author(ctx).roles]:
        return True
    return False

def create_select_embed(user):
    """
    Create an embed for alias command help.

    Args:
        user (Member): The user requesting help.

    Returns:
        Embed: The created embed.
    """
    embed = Embed(title="Eine kleine Hilfe zu den alias Commands",
                          colour=Colour(0x0446b0),
                          description="hier erfährst du mehr zu "
                                      "den einzelnen alias Commands")
    loaded_config = Loader(user).load_config("embed")
    embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
    embed.set_footer(text="Asked by " + user.name,
                     icon_url=user.avatar)
    return embed

async def send_message(ctx: Context | Interaction, msg: str = None, view: ui.View = None,
                       embed: Embed = None,
                       ephemeral: bool = False, delete_after: int = None):
    """
    Send a message to the channel or interaction.

    Args:
        ctx (Context | Interaction): The context or interaction.
        msg (str, optional): The message content. Defaults to None.
        view (ui.View, optional): The view to attach. Defaults to None.
        embed (Embed, optional): The embed to send. Defaults to None.
        ephemeral (bool, optional): Whether the message is ephemeral. Defaults to False.
        delete_after (int, optional): Time in seconds to delete the message after. Defaults to None.

    Returns:
        Message: The sent message.
    """
    if isinstance(ctx, Context):
        if ephemeral:
            return await ctx.channel.send(content=msg, embed=embed, view=view,
                                          delete_after=delete_after)
        if delete_after:
            return await ctx.channel.send(content=msg, embed=embed,
                                          view=view, delete_after=delete_after)
        return await ctx.channel.send(content=msg, embed=embed,
                                      view=view)
    if isinstance(ctx, Interaction):
        try:
            await ctx.response.defer()
        except HTTPException:
            pass
        if view is not None:
            if ephemeral:
                return await ctx.followup.send(content=msg, embed=embed,
                                               view=view, ephemeral=ephemeral)
            return await ctx.followup.send(content=msg, embed=embed, view=view)
        if ephemeral:
            return await ctx.followup.send(content=msg, embed=embed, ephemeral=ephemeral)
        return await ctx.followup.send(content=msg, embed=embed)

def return_author(ctx: Context | Interaction):
    """
    Return the author of the context or interaction.

    Args:
        ctx (Context | Interaction): The context or interaction.

    Returns:
        Member: The author of the context or interaction.
    """
    if isinstance(ctx, Interaction):
        return ctx.user
    return ctx.author

#endregion

#region DB

async def get_daily(user):
    """
    Get the daily status for a user.

    Args:
        user (Member): The user to check.

    Returns:
        bool: Whether the user can claim daily rewards.
    """
    can_daily = await db.get_daily(user.id)
    return can_daily

#endregion

#region Gaming

async def execute_gaming_with_timeout(ctx: Context | Interaction, befehl,
                                      param_one, param_two=None):
    """
    Execute a gaming command with a timeout.

    Args:
        ctx (Context | Interaction): The context or interaction.
        befehl (function): The command to execute.
        param_one (any): The first parameter for the command.
        param_two (any, optional): The second parameter for the command. Defaults to None.
    """
    try:
        if param_two is None:
            await asyncio.wait_for(befehl(ctx, param_one), timeout=300)
        else:
            await asyncio.wait_for(befehl(ctx, param_one, param_two), timeout=300)
    except asyncio.TimeoutError:
        currentlyGaming.remove(str(return_author(ctx).id))
        await send_message(ctx, "Du hast zu lange gebraucht. Deine Runde endet.")

async def get_money_for_user(user: Member):
    """
    Get the money balance for a user.

    Args:
        user (Member): The user to check.

    Returns:
        int: The user's money balance.
    """
    money_user = await db.get_money_for_user(user.id)
    return money_user

def create_embed(ctx: Context | Interaction, colorcode, kind) -> Embed:
    """
    Create a basic embed for gaming.

    Args:
        ctx (Context | Interaction): The context or interaction.
        colorcode (int): The color code for the embed.
        kind (str): The kind of embed.

    Returns:
        Embed: The created embed.
    """
    return basic_embed_element(ctx, colorcode, kind, " is playing")

def create_social_embed(ctx: Context | Interaction, colorcode, kind) -> Embed:
    """
    Create a basic embed for social interactions.

    Args:
        ctx (Context | Interaction): The context or interaction.
        colorcode (int): The color code for the embed.
        kind (str): The kind of embed.

    Returns:
        Embed: The created embed.
    """
    return basic_embed_element(ctx, colorcode, kind, " has asked")

def basic_embed_element(ctx: Context | Interaction, colorcode, kind, text) -> Embed:
    """
    Create a basic embed element.

    Args:
        ctx (Context | Interaction): The context or interaction.
        colorcode (int): The color code for the embed.
        kind (str): The kind of embed.
        text (str): The footer text.

    Returns:
        Embed: The created embed.
    """
    embed = Embed(title=kind, colour=Colour(colorcode))
    embed.set_footer(text=return_author(ctx).name + text,
                     icon_url=return_author(ctx).avatar)
    return embed

async def can_play(ctx: Context | Interaction, bet):
    """
    Check if the user can play a game with the given bet.

    Args:
        ctx (Context | Interaction): The context or interaction.
        bet (int): The bet amount.

    Returns:
        list: A list containing whether the user can play,
        has enough money, and if the bet is an integer.
    """
    playable = True
    has_enough = True
    is_int = True
    user_money = await get_money_for_user(return_author(ctx))
    try:
        bet = int(bet)
    except ValueError:
        playable = False
        is_int = False
    if is_int:
        if bet < 1:
            playable = False
        if bet > user_money:
            has_enough = False
    return [playable, has_enough]

def get_first_card(cards) -> int:
    """
    Get the value of the first card in a list of cards.

    Args:
        cards (list): The list of cards.

    Returns:
        int: The value of the first card.
    """
    firstworth = 0
    card = cards[0]
    kind = card[0]
    if kind in ["Bube", "Dame", "König"]:
        firstworth += 10
    elif kind == "Ass":
        firstworth += 11
    else:
        firstworth += int(kind)

    return firstworth

#endregion

#region API
api_key_header = api_key.APIKeyHeader(name="X-API-KEY")

async def validate_api_key(key: str = Security(api_key_header)):
    if key != os.environ["API_KEY"]:
        raise fastapiHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized - API Key is wrong"
        )
#endregion