import typing
import discord
from discord.ui import View


class DCView(View):
    def __init__(self, author: typing.Union[discord.Member, discord.User]):
        self.author = author
        self.bool = False
        super().__init__(timeout=None)

    async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
        if inter is None:
            return False
        if inter.user != self.author:
            self.bool = False
        else:
            self.bool = True
