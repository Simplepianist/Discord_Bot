import json

import discord.ext.commands
from discord import Interaction, Member, Embed, Colour
from discord.ext.commands import Context


class Utility:
    """
    A class to handle utility functions for the Discord bot.
    """

    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    #region Utility
    async def load_config(self, name):
        with open("jsons/config.json") as f:
            json_file = json.load(f)
        try:
            json_file["embed"]["embeds_footerpic"] = None
        except KeyError:
            pass
        return json_file[name]


    def check_admin(self, ctx: Context | Interaction):
        if self.bot.config["botRole"] in [y.name.lower() for y in self.return_author(ctx).roles]:
            return True
        return False


    def create_select_embed(self, user):
        embed = Embed(title="Eine kleine Hilfe zu den alias Commands",
                              colour=Colour(0x0446b0),
                              description="hier erfährst du mehr zu "
                                          "den einzelnen alias Commands")
        loaded_config = self.bot.config["embed"]
        embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
        embed.set_footer(text="Asked by " + user.name,
                         icon_url=user.avatar)
        return embed

    def return_author(self, ctx: Context | Interaction):
        if isinstance(ctx, Interaction):
            return ctx.user
        return ctx.author
    #endregion

    #region DB
    async def get_daily(self, user):
        can_daily = await self.bot.db.get_daily(user.id)
        return can_daily
    #endregion

    #region Gaming


    async def get_money_for_user(self,user: Member):
        money_user = await self.bot.db.get_money_for_user(user.id)
        return money_user

    def create_embed(self, ctx: Context | Interaction, colorcode, kind) -> Embed:
        return self.basic_embed_element(ctx, colorcode, kind, " is playing")


    def create_social_embed(self, ctx: Context | Interaction, colorcode, kind) -> Embed:
        return self.basic_embed_element(ctx, colorcode, kind, " has asked")


    def basic_embed_element(self, ctx: Context | Interaction, colorcode, kind, text) -> Embed:
        embed = Embed(title=kind, colour=Colour(colorcode))
        embed.set_footer(text=self.return_author(ctx).name + text,
                         icon_url=self.return_author(ctx).avatar)
        return embed


    async def can_play(self, ctx: Context | Interaction, bet):
        playable = True
        has_enough = True
        is_int = True
        user_money = await self.bot.db.get_money_for_user(self.return_author(ctx).id)
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


    def get_first_card(self, cards) -> int:
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
