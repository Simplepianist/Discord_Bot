"""
Dieses Modul enthält die Klassen AliasSelect und AliasSelectView,
die Dropdown-Menüs und Ansichten für die Auswahl von
Alias-Kategorien in einem Discord-Bot bereitstellen.
"""
import discord
from discord import Member
from Dropdowns.universal_select import UniversalSelect


class AliasSelect(UniversalSelect):
    """
    A dropdown menu for selecting different alias categories.

    Attributes:
        user (Member): The Discord member using the dropdown.
        view (discord.ui.View): The view that this dropdown is part of.
    """

    def __init__(self, user: Member, view):
        """
        Initializes the AliasSelect with predefined options and responses.

        Args:
            user (Member): The Discord member using the dropdown.
            view (discord.ui.View): The view that this dropdown is part of.
        """
        options = [
            discord.SelectOption(label="Allgemein",
                                 description="Allgemeine Aliase für den Bot",
                                 emoji="📖"),
            discord.SelectOption(label="Games",
                                 description="Aliase für die Games",
                                 emoji="🎮"),
            discord.SelectOption(label="Quotes",
                                 description="Zitate aus verschiedenen Bereichen",
                                 emoji="📒")
        ]
        response = {"Allgemein": [
            [".h", "Zeigt die Hilfe an", True],
            [".i", "Sendet den Inivtelink", True],
            [".s", "Zeigt die Streaming-Url an", True],
            [".a", "Zeigt diese Aliasliste an", True]
        ],
            "Games": [
                [".sc", "Zeigt das Scoreboard an", True],
                [".bal (User)", "Zeigt dein Aktuelles Guthaben (oder eines Users)", True],
                [".give <user> <money>", "Sendet den Betrag an den Ausgewählten User", True],
                [".bj <einsatz>", "Startet ein Blackjack Spiel mit gegeben Einsatz", True],
                [".hl <einsatz>", "Startet ein Higher-Lower Game von 1 bis 100", True],
                [".rl <einsatz> <wettstein>",
                 "Startet ein Roulette Spiel mit gegeben Einsatz auf den gesetzten Wert", True],
                [".rob (player)", "Raube die Bank aus (oder einen User)", True]
            ],
            "Quotes": [
                [".quote", "Gibt ein Zufälliges Anime Zitat aus", True],
                [".qotd", "Gibt das Zitat des Tages aus", True]
            ]}
        super().__init__(user, options, response, view)


class AliasSelectView(discord.ui.View):
    """
    A view that contains the AliasSelect dropdown.

    Attributes:
        user (Member): The Discord member using the view.
        timeout (int): The timeout duration for the view.
    """

    def __init__(self, user: Member, timeout=180):
        """
        Initializes the AliasSelectView with a timeout and adds the AliasSelect dropdown.

        Args:
            user (Member): The Discord member using the view.
            timeout (int, optional): The timeout duration for the view. Defaults to 180 seconds.
        """
        super().__init__(timeout=timeout)
        self.add_item(AliasSelect(user, self))
