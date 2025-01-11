from discord import Interaction, SelectOption, Member
from discord.ui import Select

from Util.util_commands import create_select_embed
from config_loader import Loader
from Util.variables import OWNER

class UniversalSelect(Select):
    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, value):
        self._view = value

    def __init__(self, user: Member, options: list[SelectOption],
                 response: dict, view):
        self.user = user
        self.response = response
        self.embed = create_select_embed(user)
        self.view = view
        self.loaded_config = Loader(OWNER).load_config("embed")
        self.embed.set_thumbnail(url=self.loaded_config["embeds_thumbnail"])
        super().__init__(placeholder="Wähle eine Category",
                         max_values=1,
                         min_values=1,
                         options=options)

    async def callback(self, interaction: Interaction):
        self.embed.clear_fields()
        if interaction.user.id == self.user.id:
            for element in self.response[self.values[0]]:
                self.embed.add_field(name=element[0],
                                     value=element[1],
                                     inline=element[2])
            await interaction.response.edit_message(embed=self.embed,
                                                      view=self.view)
        else:
            await interaction.response.send_message(content="Du hast nicht dieses "
                                                              "Menü aufgerufen",
                                                      ephemeral=True)
