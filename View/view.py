import typing
import discord
from discord.ui import View


class DCView(View):
    """
    A custom Discord UI view that checks interactions from a specific author.
    """

    def __init__(self, author: typing.Union[discord.Member, discord.User]):
        """
        Initialize the DCView.

        :param author: The Discord member or user who is the author of the interaction.
        """
        self.author = author
        self.bool = False
        super().__init__(timeout=None)

    async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
        """
        Check if the interaction is from the author.

        :param inter: The interaction to check.
        :return: True if the interaction is from the author, False otherwise.
        """
        if inter is None:
            return False
        if inter.user != self.author:
            self.bool = False
        else:
            self.bool = True
