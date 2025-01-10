import asyncio

from discord import Interaction
from discord.ext.commands import Context
from Database.db_access import DB_Controller
from Util.variables import *

db = DB_Controller(test)


def load_config(name):
    with open("jsons/config.json") as f:
        json_file = json.load(f)
    try:
        json_file["embed"]["embeds_footerpic"] = owner.avatar
    except:
        pass
    return json_file[name]


def get_money_for_user(user: discord.Member):
    global user_money_dir
    money_user = db.get_money_for_user(user.id)
    return money_user


def checkAdmin(ctx: Context | Interaction):
    if botRole in [y.name.lower() for y in return_author(ctx).roles]:
        return True
    else:
        return False


"""
DB Command
"""


def get_daily(user):
    can_daily = db.get_daily(user.id)
    return can_daily


"""
Gaming
"""


def create_embed(ctx: Context | Interaction, colorcode, kind) -> discord.Embed:
    return basic_embed_element(ctx, colorcode, kind, " is playing")


def create_social_embed(ctx: Context | Interaction, colorcode, kind) -> discord.Embed:
    return basic_embed_element(ctx, colorcode, kind, " has asked")


def basic_embed_element(ctx: Context | Interaction, colorcode, kind, text) -> discord.Embed:
    embed = discord.Embed(title=kind, colour=discord.Colour(colorcode))
    embed.set_footer(text=return_author(ctx).name + text,
                     icon_url=return_author(ctx).avatar)
    return embed


def can_play(ctx: Context | Interaction, bet):
    canPlay = True
    has_enough = True
    is_int = True
    user_money = get_money_for_user(return_author(ctx))
    try:
        bet = int(bet)
    except:
        canPlay = False
        is_int = False
    if is_int:
        if bet < 1:
            canPlay = False
        if bet > user_money:
            has_enough = False
    return [canPlay, has_enough]


def get_first_card(cards) -> int:
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


async def send_message(ctx: Context | Interaction, msg: str = None, view: discord.ui.View = None,
                       embed: discord.Embed = None, ephemeral: bool = False, delete_after: int = None):
    if type(ctx) is Context:
        if ephemeral:
            return await ctx.channel.send(content=msg, embed=embed, view=view,
                                          delete_after=delete_after)
        else:
            return await ctx.channel.send(content=msg, embed=embed, view=view, delete_after=delete_after)
    elif type(ctx) is Interaction:
        try:
            await ctx.response.defer()
        except:
            pass
        if view is not None:
            if ephemeral:
                return await ctx.followup.send(content=msg, embed=embed, view=view, ephemeral=ephemeral)
            else:
                return await ctx.followup.send(content=msg, embed=embed, view=view)
        else:
            if ephemeral:
                return await ctx.followup.send(content=msg, embed=embed, ephemeral=ephemeral)
            else:
                return await ctx.followup.send(content=msg, embed=embed)


def return_author(ctx: Context | Interaction):
    if type(ctx) is Interaction:
        return ctx.user
    return ctx.author

async def execute_gaming_with_timeout(ctx: Context | Interaction, befehl, param_one, param_two=None):
    try:
        if param_two is None:
            await asyncio.wait_for(befehl(ctx, param_one), timeout=300)
        else:
            await asyncio.wait_for(befehl(ctx, param_one, param_two), timeout=300)
    except asyncio.TimeoutError:
        currentlyGaming.remove(str(return_author(ctx).id))
        await send_message(ctx, "Du hast zu lange gebraucht. Deine Runde endet.")