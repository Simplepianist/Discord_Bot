"""
Dieses Modul enthält die UniversalSelect-Klasse,
die eine benutzerdefinierte Auswahlkomponente für Discord-Bots darstellt.
"""
from discord import Interaction, SelectOption, Member
from discord.ui import Select
from Util.util_commands import Utility

class UniversalSelect(Select):
    """
    Eine benutzerdefinierte Auswahlkomponente für Discord-Bots, die es Benutzern ermöglicht,
    eine Kategorie auszuwählen und eine entsprechende Antwort anzuzeigen.
    """

    @property
    def view(self):
        """
        Getter für die view-Eigenschaft.
        """
        return self._view

    @view.setter
    def view(self, value):
        """
        Setter für die view-Eigenschaft.
        """
        self._view = value

    def __init__(self, user: Member, options: list[SelectOption], response: dict, view, bot):
        """
        Initialisiert eine neue Instanz der UniversalSelect-Klasse.

        :param user: Der Benutzer, der die Auswahl trifft.
        :param options: Eine Liste von Auswahloptionen.
        :param response: Ein Wörterbuch mit den Antworten für jede Auswahloption.
        :param view: Die Ansicht, die aktualisiert werden soll.
        """
        self.utils = Utility(bot)
        self.user = user
        self.response = response
        self.embed = self.utils.create_select_embed(user)
        self.view = view
        self.loaded_config = self.utils.load_config("embed")
        self.embed.set_thumbnail(url=self.loaded_config["embeds_thumbnail"])
        super().__init__(placeholder="Wähle eine Category",
                         max_values=1,
                         min_values=1,
                         options=options)

    async def callback(self, interaction: Interaction):
        """
        Callback-Funktion, die aufgerufen wird, wenn der Benutzer eine Auswahl trifft.

        :param interaction: Die Interaktion, die die Auswahl ausgelöst hat.
        """
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
