import asyncio
import json
from http.client import HTTPException
from discord import Interaction, Member, Embed, Colour, ui
from discord.ext.commands import Context, check
from Database.db_access import DbController
from Util.variables import botRole, currentlyGaming, OWNER
from config_loader import Loader

db = DbController()

#region Utility
def has_role():
    async def predicate(ctx: Context):
        return botRole in [y.name.lower() for y in ctx.author.roles]
    return check(predicate)

def load_config(name):
    with open("jsons/config.json") as f:
        json_file = json.load(f)
    try:
        json_file["embed"]["embeds_footerpic"] = OWNER.avatar
    except KeyError:
        pass
    return json_file[name]


def check_admin(ctx: Context | Interaction):
    if botRole in [y.name.lower() for y in return_author(ctx).roles]:
        return True
    return False


def create_select_embed(user):
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
    if isinstance(ctx, Interaction):
        return ctx.user
    return ctx.author
#endregion

#region DB
async def get_daily(user):
    can_daily = await db.get_daily(user.id)
    return can_daily
#endregion

#region Gaming
async def execute_gaming_with_timeout(ctx: Context | Interaction, befehl,
                                      param_one, param_two=None):
    try:
        if param_two is None:
            await asyncio.wait_for(befehl(ctx, param_one), timeout=300)
        else:
            await asyncio.wait_for(befehl(ctx, param_one, param_two), timeout=300)
    except asyncio.TimeoutError:
        currentlyGaming.remove(str(return_author(ctx).id))
        await send_message(ctx, "Du hast zu lange gebraucht. Deine Runde endet.")

async def get_money_for_user(user: Member):
    money_user = await db.get_money_for_user(user.id)
    return money_user

def create_embed(ctx: Context | Interaction, colorcode, kind) -> Embed:
    return basic_embed_element(ctx, colorcode, kind, " is playing")


def create_social_embed(ctx: Context | Interaction, colorcode, kind) -> Embed:
    return basic_embed_element(ctx, colorcode, kind, " has asked")


def basic_embed_element(ctx: Context | Interaction, colorcode, kind, text) -> Embed:
    embed = Embed(title=kind, colour=Colour(colorcode))
    embed.set_footer(text=return_author(ctx).name + text,
                     icon_url=return_author(ctx).avatar)
    return embed


async def can_play(ctx: Context | Interaction, bet):
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
