"""
Dieses Modul enthält die Klassen HelpSelect und HelpSelectView,
die für die Erstellung und Verwaltung von Dropdown-Menüs in einem Discord-Bot verwendet werden.
"""

import discord
from discord import Member
from Dropdowns.universal_select import UniversalSelect

class HelpSelect(UniversalSelect):
    """
    Eine Klasse, die ein Dropdown-Menü für Hilfeoptionen erstellt.

    Attribute:
        user (Member): Der Benutzer, der das Dropdown-Menü verwendet.
        view (discord.ui.View): Die Ansicht, die das Dropdown-Menü enthält.
    """

    def __init__(self, user: Member, view):
        """
        Initialisiert die HelpSelect-Klasse mit den gegebenen Optionen und Antworten.

        Args:
            user (Member): Der Benutzer, der das Dropdown-Menü verwendet.
            view (discord.ui.View): Die Ansicht, die das Dropdown-Menü enthält.
        """
        options = [
            discord.SelectOption(label="Allgemein",
                                 description="Allgemeine Commands für den Bot",
                                 emoji="📖"),
            discord.SelectOption(label="Games",
                                 description="Commands für die Games",
                                 emoji="🎮"),
            discord.SelectOption(label="Quotes",
                                 description="Zitate aus verschiedenen Bereichen",
                                 emoji="📒")
        ]
        response = { "Allgemein": [
            [".help", "Zeigt diese Hilfe an", True],
            [".invite", "Sendet den Inivtelink", True],
            [".stream", "Zeigt die Streaming-Url an", True],
            [".alias", "Zeigt die Aliasliste an", True],
            [".ping", "Pong", True]
        ],
            "Games": [
                [".scoreboard", "Zeigt das Scoreboard an", True],
                [".daily", "Claim der daily Coins", True],
                [".money (user)", "Zeigt dein Aktuelles Guthaben (oder eines Users)", True],
                [".send <user> <money>", "Sendet den Betrag an den Ausgewählten User", True],
                [".blackjack <einsatz>", "Startet ein Blackjack Spiel mit gegeben Einsatz", True],
                [".higherlow <einsatz>", "Startet ein Higher-Lower Game von 1 bis 100", True],
                [".roulette <einsatz> <wettstein>",
                 "Startet ein Roulette Spiel mit gegeben Einsatz auf den gesetzten Wert", True],
                [".rob (player)", "Raube die Bank aus (oder einen User)", True]
            ],
            "Quotes": [
                [".quote", "Gibt ein Zufälliges Anime Zitat aus", True],
                [".qotd", "Gibt das Zitat des Tages aus", True]
            ]}
        super().__init__(user, options, response, view)

class HelpSelectView(discord.ui.View):
    """
    Eine Klasse, die eine Ansicht für das HelpSelect-Dropdown-Menü erstellt.

    Attribute:
        user (Member): Der Benutzer, der die Ansicht verwendet.
        timeout (int): Die Zeit in Sekunden, nach der die Ansicht abläuft.
    """

    def __init__(self, user: Member, timeout=180):
        """
        Initialisiert die HelpSelectView-Klasse mit dem gegebenen Benutzer und Timeout.

        Args:
            user (Member): Der Benutzer, der die Ansicht verwendet.
            timeout (int, optional): Die Zeit in Sekunden,
            nach der die Ansicht abläuft. Standard ist 180 Sekunden.
        """
        super().__init__(timeout=timeout)
        self.add_item(HelpSelect(user, self))
